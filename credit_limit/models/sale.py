# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for rec in self :
            rec.partner_id.check_limit(rec)
        return super(SaleOrder, self).action_confirm()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('amt_invoiced')
    def _get_sale_noinvoice(self):
        for rec in self :
            sale_noinvoice = 0
            if rec.order_id.state in ('sale','done'):
                sale_noinvoice = rec.order_id.currency_id.compute(rec.price_total - rec.amt_invoiced, self.env.user.company_id.currency_id)
            rec.amt_noinvoice = sale_noinvoice

    amt_noinvoice = fields.Monetary(compute='_get_sale_noinvoice', string='Uninvoiced Amount', store=True)
