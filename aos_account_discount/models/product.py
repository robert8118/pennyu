# -*- coding: utf-8 -*- 
# Part of Odoo. See LICENSE file for full copyright and licensing details. 
from odoo import api, fields, models 
from datetime import datetime
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class ProductCategory(models.Model):
    _inherit = 'product.category'

#     property_discount = fields.Selection([
#         ('non_journal', 'Non Jurnal'),
#         ('with_journal', 'With Journal')], string='Discount Entries',
#         company_dependent=True, copy=True, default='with_journal')
    property_discount_account_input_categ_id = fields.Many2one(
        'account.account', 'Discount Vendor Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the source location. This is the default value for all products in this category. It "
             "can also directly be set on each product")
    property_discount_account_output_categ_id = fields.Many2one(
        'account.account', 'Discount Customer Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the source location. This is the default value for all products in this category. It "
             "can also directly be set on each product")

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
#     property_discount = fields.Selection([
#         ('non_journal', 'Non Jurnal'),
#         ('with_journal', 'With Journal')], string='Discount Entries',
#         company_dependent=True, copy=True, default='with_journal',
#         help="""Manual: The accounting entries to value the inventory are not posted automatically.
#         Automated: An accounting entry is automatically created to value the inventory when a product enters or leaves the company.""")
#     valuation_discount = fields.Char(compute='_compute_valuation_discount', inverse='_set_valuation_discount')
    property_discount_account_input = fields.Many2one(
        'account.account', 'Discount Vendor Account',
        company_dependent=True, domain=[('deprecated', '=', False)],
        help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the source location. When not set on the product, the one from the product category is used.")
    property_discount_account_output = fields.Many2one(
        'account.account', 'Discount Customer Account',
        company_dependent=True, domain=[('deprecated', '=', False)],
        help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the destination location. When not set on the product, the one from the product category is used.")

#     @api.one
#     @api.depends('property_discount', 'categ_id.property_discount')
#     def _compute_valuation_discount(self):
#         self.valuation_discount = self.property_discount or self.categ_id.property_discount
# 
#     @api.one
#     def _set_valuation_discount(self):
#         return self.write({'property_discount': self.valuation_discount})
    
    @api.multi
    def get_product_accounts(self, fiscal_pos=None):
        """ Add the stock journal related to product to the result of super()
        @return: dictionary which contains all needed information regarding stock accounts and journal and super (income+expense accounts)
        """
        accounts = super(ProductTemplate, self).get_product_accounts(fiscal_pos=fiscal_pos)
        accounts.update({'discount_output': self.categ_id.property_discount_account_output_categ_id \
                            and self.categ_id.property_discount_account_output_categ_id.id or False,
                         'discount_input': self.categ_id.property_discount_account_input_categ_id \
                            and self.categ_id.property_discount_account_input_categ_id.id or False})
        return accounts

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    def _discount_move_lines(self, type, name, product, uom, qty, price_unit, currency=False, amount_currency=False, fiscal_position=False, account_analytic=False, analytic_tags=False):
        """Prepare dicts describing new journal COGS journal items for a product sale.

        Returns a dict that should be passed to `_convert_prepared_anglosaxon_line()` to
        obtain the creation value for the new journal items.

        :param Model product: a product.product record of the product being sold
        :param Model uom: a product.uom record of the UoM of the sale line
        :param Integer qty: quantity of the product being sold
        :param Integer price_unit: unit price of the product being sold
        :param Model currency: a res.currency record from the order of the product being sold
        :param Interger amount_currency: unit price in the currency from the order of the product being sold
        :param Model fiscal_position: a account.fiscal.position record from the order of the product being sold
        :param Model account_analytic: a account.account.analytic record from the line of the product being sold
        """
        accounts = product.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        # debit account dacc will be the in_invoice
        dacc = accounts['discount_output']
        # credit account cacc will be the out_invoice
        cacc = accounts['discount_input']
        if type in ('in_invoice', 'out_refund') and cacc:
            #DISCOUNT IN_INVOICE & OUT_REFUND
            return [
                 {
                     'type': 'src',
                     'name': 'Disc: %s'%name[:64],
                     'price_unit': price_unit,
                     'quantity': qty,
                     'price': -1 * price_unit * qty,
                     'currency_id': currency and currency.id,
                     'amount_currency': -1 * amount_currency,
                     'account_id': cacc,
                     'product_id': product.id,
                     'uom_id': uom.id,
                     'account_analytic_id': account_analytic and account_analytic.id,
                     'analytic_tag_ids': analytic_tags and analytic_tags.ids and [(6, 0, analytic_tags.ids)] or False,
                 }]
        elif type in ('out_invoice', 'in_refund') and dacc:
            #DISCOUNT OUT_INVOICE & IN_REFUND
            return [{
                'type': 'src',
                'name': 'Disc: %s'%name[:64],
                'price_unit': price_unit,
                'quantity': qty,
                'price': -1 * price_unit * qty,
                'currency_id': currency and currency.id,
                'amount_currency': -1 * amount_currency,
                'account_id': dacc,
                'product_id': product.id,
                'uom_id': uom.id,
                'account_analytic_id': account_analytic and account_analytic.id,
                'analytic_tag_ids': analytic_tags and analytic_tags.ids and [(6, 0, analytic_tags.ids)] or False,
            }]
        return []
