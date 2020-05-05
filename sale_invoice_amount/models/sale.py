from odoo import models, fields, tools, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

import time
import math
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Monetary(
        string='Invoiced', store=True, readonly=True, compute='_compute_invoice_amount')
    balance_amount = fields.Monetary(
        string='Balance', store=True, readonly=True, compute='_compute_invoice_amount')

    @api.one
    @api.depends('invoice_ids.state')
    def _compute_invoice_amount(self):
        sale = self.sudo()
        invoiced_amount = sum(inv.amount_total for inv in sale.invoice_ids.filtered(
            lambda x: x.state in ('open', 'paid') and x.type == 'out_invoice'))
        sale.invoiced_amount = invoiced_amount
        sale.balance_amount = sale.amount_total - invoiced_amount
