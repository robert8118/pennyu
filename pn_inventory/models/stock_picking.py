# -*- coding: utf-8 -*-
"""file stock picking"""
from odoo import api, models, fields, _


class StockPicking(models.Model):
    """inherit model Stock Picking"""
    _inherit = 'stock.picking'

    postal_code = fields.Integer()
