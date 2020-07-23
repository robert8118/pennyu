# -*- coding: utf-8 -*-
'''pn_sale'''
from odoo import api, fields, models, _
from openerp.exceptions import Warning
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    '''inherit sale.order'''
    _inherit = "sale.order"

    @api.multi
    def total_terbilang(self, amount_total):
        '''function total terbilang'''
        for order in self:
            unit = ["", "Satu", "Dua", "Tiga", "Empat",
                    "Lima", "Enam", "Tujuh", "Delapan",
                    "Sembilan", "Sepuluh", "Sebelas"]
            result = " "
            total_terbilang = self.total_terbilang
            n = int(amount_total)
            if n >= 0 and n <= 11:
                result = result + unit[n]
            elif n < 20:
                result = total_terbilang(n % 10) + " Belas"
            elif n < 100:
                result = total_terbilang(n / 10) + " Puluh" + total_terbilang(n % 10)
            elif n < 200:
                result = " Seratus" + total_terbilang(n - 100)
            elif n < 1000:
                result = total_terbilang(n / 100) + " Ratus" + total_terbilang(n % 100)
            elif n < 2000:
                result = " Seribu" + total_terbilang(n - 1000)
            elif n < 1000000:
                result = total_terbilang(n / 1000) + " Ribu" + total_terbilang(n % 1000)
            elif n < 1000000000:
                result = total_terbilang(n / 1000000) + " Juta" + total_terbilang(n % 1000000)
            else:
                result = total_terbilang(n / 1000000000) + " Miliar" + total_terbilang(n % 1000000000)
            return result

    @api.multi
    def write(self, vals):
        '''extend function write to add warning if
        payment term customer is different with sale order'''
        res = super(SaleOrder, self).write(vals)
        for sale in self:
            partner_id = sale.partner_id
            payment_term_id = partner_id.property_payment_term_id
            _logger.warning("Payment term %s, %s: %s", partner_id.name, payment_term_id and payment_term_id.name, sale.payment_term_id.name)
            if payment_term_id and payment_term_id.id != sale.payment_term_id.id:
                raise Warning("Cannot change Payment Term!")
        return res





class SaleOrder_msi(models.Model):
    '''inherit sale.order.line'''
    _inherit = "sale.order.line"


    discount1 = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)



    @api.model
    def create(self, values):
        values['discount'] = values.get('discount1')
        values.update(self._prepare_add_missing_fields(values))
        line = super(SaleOrder_msi, self).create(values)
        if line.order_id.state == 'sale':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.order_id.message_post(body=msg)
            # create an analytic account if at least an expense product
            if line.product_id.expense_policy != 'no' and not self.order_id.analytic_account_id:
                self.order_id._create_analytic_account()

        return line



    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        self.discount = 0.0
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

        price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        new_list_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)

        if new_list_price != 0:
            if self.order_id.pricelist_id.currency_id.id != currency_id:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(new_list_price, self.order_id.pricelist_id.currency_id)
            discount = (new_list_price - price) / new_list_price * 100
            if discount > 0:
                self.discount = discount
                self.discount1 = discount
