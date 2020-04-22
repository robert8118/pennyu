"""inherit product template"""
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):
    """inherit product template"""
    _inherit = "product.template"

    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user, pn_user.group_portal_rws, pn_user.group_portal_sales",
        help="Cost used for stock valuation in standard "
               "price and as a first price to set in average/fifo. "
               "Also used as a base price for pricelists. "
               "Expressed in the default unit of measure of the product. ")

class ProductProduct(models.Model):
    """inherit product product"""
    _inherit = "product.product"

    standard_price = fields.Float(
        'Cost', company_dependent=True,
        digits=dp.get_precision('Product Price'),
        groups="base.group_user, pn_user.group_portal_rws, pn_user.group_portal_sales",
        help="Cost used for stock valuation in standard price and "
             "as a first price to set in average/fifo. "
               "Also used as a base price for pricelists. "
               "Expressed in the default unit of measure of the product.")
