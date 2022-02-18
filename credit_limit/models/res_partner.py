from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
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

    @api.depends('sale_order_ids.order_line.amt_noinvoice')
    def _get_sale_noinvoice(self):
        for rec in self :
            sale_noinvoice = 0
            domain = [
                ('order_id.partner_id', 'child_of', rec.id),
                ('order_id.state', 'in', ['sale','done']),
                ('amt_noinvoice', '>', 0),
            ]
            order_line_ids = self.env['sale.order.line'].search(domain)
            for line in order_line_ids :
                sale_noinvoice += line.order_id.currency_id.compute(line.amt_noinvoice, self.env.user.company_id.currency_id)
            rec.sale_noinvoice = sale_noinvoice

    limit_ids = fields.Many2many(
        'credit.limit',
        'partner_limit_rel',
        'partner_id',
        'limit_id',
        string='Credit Limit')
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_get_invoice_count')
    sale_noinvoice = fields.Monetary(compute='_get_sale_noinvoice', string='Uninvoiced Amount', store=True)

    @api.multi
    def check_limit(self, order_id):
        partner_ids = self.search([('id', 'parent_of', self.id)])
        for partner_id in partner_ids:
            message = ''
            types = partner_id.limit_ids.mapped('type')
            limit_ids = partner_id.limit_ids + self.env['credit.limit'].search([('is_global', '=', True), ('type', 'not in', types)])
            for limit_id in limit_ids:
                if limit_id.type == 'overdue' and partner_id.total_due:
                    total_due = 0
                    if not limit_id.payment_term_id :
                        total_due = partner_id.total_due
                    else :
                        pterm = limit_id.payment_term_id
                        today = fields.Date.context_today(self)
                        pterm_list = pterm.with_context(currency_id=self.env.user.company_id.currency_id.id).compute(value=1, date_ref=today)[0]
                        date_due = max(line[0] for line in pterm_list)
                        today = datetime.strptime(today, '%Y-%m-%d')
                        date_due = datetime.strptime(date_due, '%Y-%m-%d')
                        time_diff = date_due - today
                        date_due_final = today - timedelta(days=time_diff.days)
                        date_due_final = date_due_final.strftime('%Y-%m-%d')
                        domain = partner_id.get_followup_lines_domain(date_due_final)
                        for aml in self.env['account.move.line'].search(domain):
                            total_due += aml.amount_residual
                    if total_due > 0 :
                        message += '\n - %s (overdue: %s)' % (limit_id.display_name, '{:,.2f}'.format(total_due))
                elif limit_id.type == 'count' and partner_id.invoice_count >= limit_id.count:
                    message += '\n - %s (invoice count: %s. limit: %s)' % (limit_id.display_name, partner_id.invoice_count, limit_id.count)
                elif limit_id.type == 'amount':
                    limit_amount = limit_id.currency_id.compute(limit_id.amount, self.env.user.company_id.currency_id)
                    current_amount = order_id.pricelist_id.currency_id.compute(order_id.amount_total, self.env.user.company_id.currency_id)
                    total_amount = current_amount + partner_id.credit + partner_id.sale_noinvoice
                    if total_amount > limit_amount:
                        message += '\n - %s (receivable + uninvoiced amount: %s. current amount: %s. total: %s. limit: %s)' % (limit_id.display_name, '{:,.2f}'.format(partner_id.credit + partner_id.sale_noinvoice), '{:,.2f}'.format(current_amount), '{:,.2f}'.format(total_amount), '{:,.2f}'.format(limit_amount))
            if message:
                raise ValidationError(_('Customer credit limit for %s exceeded. See details below: \n%s' % (partner_id.display_name, message)))

    @api.constrains('limit_ids')
    def _check_double_limit(self):
        for rec in self:
            for l in rec.limit_ids :
                other_limit_ids = self.env['credit.limit'].search([
                    ('partner_ids', 'in', rec.ids),
                    ('type','=',l.type),
                ])
                if len(other_limit_ids) > 1 :
                    raise ValidationError(_(f'Double credit limit with same type for customer {rec.display_name}: {", ".join(other_limit_ids.mapped("display_name"))}'))

    @api.onchange('company_id')
    def onchange_company(self):
        self.limit_ids = False
