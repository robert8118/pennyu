from odoo import models, fields, tools, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Monetary(
        string='Invoiced', store=True, readonly=True, compute='_compute_invoice_amount', compute_sudo=True)
    balance_amount = fields.Monetary(
        string='Balance', store=True, readonly=True, compute='_compute_invoice_amount', compute_sudo=True)

    @api.depends('order_line.qty_invoiced')
    def _compute_invoice_amount(self):
        for sale in self:
            invoiced_amount = sum(inv.amount_total for inv in sale.invoice_ids.filtered(
                lambda x: x.state in ('draft', 'open', 'paid') and x.type == 'out_invoice'))
            if invoiced_amount:
                sale.invoiced_amount = invoiced_amount
                sale.balance_amount = sale.amount_total - invoiced_amount
            else:
                sale.invoiced_amount = 0.0
                sale.balance_amount = sale.amount_total
