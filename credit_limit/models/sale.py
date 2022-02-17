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

    @api.depends('amt_invoiced','move_ids.state')
    def _get_sale_noinvoice(self):
        for rec in self :
            sale_noinvoice = 0
            if rec.order_id.state in ('sale','done'):
                unit_price = rec.price_total / rec.product_uom_qty if rec.product_uom_qty else 0
                cancelled_moves = rec.move_ids.filtered(lambda m: m.state == 'cancel')
                cancelled_amount = sum(cancelled_moves.mapped('product_uom_qty')) * unit_price
                sale_noinvoice = rec.order_id.currency_id.compute(rec.price_total - cancelled_amount - rec.amt_invoiced, self.env.user.company_id.currency_id)
            rec.amt_noinvoice = sale_noinvoice

    amt_noinvoice = fields.Monetary(compute='_get_sale_noinvoice', string='Uninvoiced Amount', store=True)
