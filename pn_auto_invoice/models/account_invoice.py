from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete='set null', index=True, readonly=True)
