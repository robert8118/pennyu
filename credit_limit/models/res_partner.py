from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import pytz
from pytz import timezone

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_invoice_count(self):
        for rec in self :
            domain = [
                ('partner_id', 'child_of', rec.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'open'),
            ]
            invoice_ids = self.env['account.invoice'].search(domain)
            rec.invoice_count = len(invoice_ids)

    limit_ids = fields.Many2many(
        'credit.limit',
        'partner_limit_rel',
        'partner_id',
        'limit_id',
        string='Credit Limit')
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_get_invoice_count')

    @api.multi
    def check_limit(self, order_id):
        partner_ids = self.search([('id', 'parent_of', self.id)])
        for partner_id in partner_ids:
            message = ''
            limit_ids = partner_id.limit_ids + self.env['credit.limit'].search([('is_global', '=', True)])
            for limit_id in limit_ids:
                if limit_id.type == 'overdue' and partner_id.total_due:
                    message += '\n - %s (overdue: %s)' % (
                    limit_id.display_name, '{:,.2f}'.format(partner_id.total_due))
                elif limit_id.type == 'count' and partner_id.invoice_count >= limit_id.count:
                    message += '\n - %s (invoice count: %s. limit: %s)' % (
                    limit_id.display_name, partner_id.invoice_count, limit_id.count)
                elif limit_id.type == 'amount':
                    limit_amount = limit_id.currency_id.compute(limit_id.amount, self.env.user.company_id.currency_id)
                    current_amount = order_id.pricelist_id.currency_id.compute(order_id.amount_total, self.env.user.company_id.currency_id)
                    total_amount = current_amount + partner_id.credit
                    if total_amount > limit_amount:
                        message += '\n - %s (receivable: %s. current amount: %s. total: %s. limit: %s)' % (limit_id.display_name, '{:,.2f}'.format(partner_id.credit), '{:,.2f}'.format(current_amount), '{:,.2f}'.format(partner_id.credit + current_amount), '{:,.2f}'.format(limit_amount))
            if message:
                raise ValidationError(_('Customer credit limit for %s exceeded. See details below: \n%s' % (partner_id.display_name, message)))
