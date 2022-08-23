from odoo import api, fields, models, tools, _
from frozendict import frozendict

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # SUKSES
    # @api.onchange('order_line')
    # def onchange_order_line(self):
    #     for rec in self:
    #         rec.id

    # GAGAL
    # @api.depends('order_line.price_total')
    # def get_order_line(self):
    #     for rec in self:
    #         print(rec.id)

    def recompute_pricelist(self):
        self.upd_multi_cat_pricelist()
    
    # Method to recompute multi cat Pricelist
    def upd_multi_cat_pricelist(self):
        # v1.0
        # for pricelist in self.pricelist_id:
        #     date, uom_id = None, None
        #     if not date:
        #         date = pricelist._context.get('date') or fields.Date.context_today(self)
        #     if not uom_id and pricelist._context.get('uom'):
        #         uom_id = pricelist._context['uom']
        #     for item in pricelist.item_ids:
        #         if item.applied_on == '4_product_categories' and item.categs_ids:
        #             product_ids = self.env['product.product'].search([('categ_id', 'in', item.categs_ids.ids)])
        #             line_ids = self.env['sale.order.line'].search([('order_id', '=', self.id), ('product_id', 'in', product_ids.ids)])
        #             price_temp = line_ids.mapped('price_total')
        #             if sum(price_temp) > item.min_amount:
        #                 for line in line_ids:
        #                     if item.base == 'pricelist' and item.base_pricelist_id:
        #                         price_tmp = item.base_pricelist_id._compute_price_rule([(line.product_id, line.product_uom_qty, self.partner_id)], date, uom_id)[line.product_id.id][0]  # TDE: 0 = price, 1 = item
        #                         price = item.base_pricelist_id.currency_id.compute(price_tmp, pricelist.currency_id, round=False)
        #                     else:
        #                         # if base option is public price take sale price else cost price of product
        #                         # price_compute returns the price in the context UoM, i.e. qty_uom_id
        #                         price = line.product_id.price_compute(item.base)[line.product_id.id]

        #                     convert_to_price_uom = (lambda price: line.product_id.uom_id._compute_price(price, line.product_id.uom_id))
                            
        #                     if price is not False:
        #                         if item.compute_price == 'fixed':
        #                             if line.price_total < item.fixed_price:
        #                                 continue
        #                             price = convert_to_price_uom(item.fixed_price)
        #                         elif item.compute_price == 'percentage':
        #                             line.discount, line.discount1 = item.percent_price, item.percent_price
        #                             price = (line.price_unit - (line.price_unit * (item.percent_price / 100))) or 0.0
        #                         else:
        #                             # complete formula
        #                             price_limit = price
        #                             line.discount, line.discount1 = item.price_discount, item.price_discount
        #                             price = (price - (price * (item.price_discount / 100))) or 0.0
        #                             if item.price_round:
        #                                 price = tools.float_round(price, precision_rounding=item.price_round)

        #                             if item.price_surcharge:
        #                                 price_surcharge = convert_to_price_uom(item.price_surcharge)
        #                                 price += price_surcharge

        #                             if item.price_min_margin:
        #                                 price_min_margin = convert_to_price_uom(item.price_min_margin)
        #                                 price = max(price, price_limit + price_min_margin)

        #                             if item.price_max_margin:
        #                                 price_max_margin = convert_to_price_uom(item.price_max_margin)
        #                                 price = min(price, price_limit + price_max_margin)
        #                     # Final price conversion into pricelist currency
        #                     if item and item.compute_price != 'fixed' and item.base != 'pricelist':
        #                         if item.base == 'standard_price':
        #                             # The cost of the product is always in the company currency
        #                             price = line.product_id.cost_currency_id.compute(price, self.currency_id, round=False)
        #                         else:
        #                             price = line.product_id.currency_id.compute(price, self.currency_id, round=False)
        #                     line.price_reduce = price
        
        # v1.1
        # for pricelist in self.pricelist_id:
        #     for item in pricelist.item_ids:
        #         if item.applied_on == '4_product_categories' and item.categs_ids:
        #             product_ids = self.env['product.product'].search([('categ_id', 'in', item.categs_ids.ids)])
        #             line_ids = self.env['sale.order.line'].search([('order_id', '=', self.id), ('product_id', 'in', product_ids.ids)])
        #             price_multi_cat_ppi = sum(line_ids.mapped('price_unit'))
        #             for line in line_ids:
        #                 product_context = dict(self.env.context, partner_id=self.partner_id.id, date=self.date_order, uom=line.product_uom.id, sale_order_id=self.id, price_multi_cat_ppi=price_multi_cat_ppi)
        #                 price, rule_id = pricelist.with_context(product_context).get_product_price_rule(line.product_id, line.product_uom_qty or 1.0, self.partner_id)
                        
        #                 # From _onchange_discount()
        #                 new_list_price, currency_id = line.with_context(product_context)._get_real_price_currency(line.product_id, rule_id, line.product_uom_qty, line.product_uom, pricelist.id)

        #                 if new_list_price != 0:
        #                     if pricelist.currency_id.id != currency_id:
        #                         # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
        #                         new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(new_list_price, pricelist.currency_id)
        #                     discount = (new_list_price - price) / new_list_price * 100
        #                     if discount > 0:
        #                         line.discount = discount
        #                         line.discount1 = discount
        #                     elif discount == 0:
        #                         line.discount = 0.0
        #                         line.discount1 = 0.0

        #                 # if item.min_amount > price_multi_cat_ppi and\
        #                 #     line.price_unit == price and\
        #                 #     item.min_amount > (price * line.product_uom_qty):
        #                 #     # From _compute_amount()
        #                 #     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
        #                 #     line.update({
        #                 #         'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
        #                 #         'price_total': taxes['total_included'],
        #                 #         'price_subtotal': taxes['total_excluded'],
        #                 #     })
        #                 # Update price_reduce
        #                 line.price_reduce = price

        # v1.2
        for line in self.order_line:
            product_context = dict(self.env.context, partner_id=self.partner_id.id, date=self.date_order, uom=line.product_uom.id, sale_order_id=self.id)
            price, rule_id = line.order_id.pricelist_id.with_context(product_context).get_product_price_rule(line.product_id, line.product_uom_qty or 1.0, self.partner_id)
            
            # From _onchange_discount()
            new_list_price, currency_id = line.with_context(product_context)._get_real_price_currency(line.product_id, rule_id, line.product_uom_qty, line.product_uom, line.order_id.pricelist_id.id)

            if new_list_price != 0:
                if line.order_id.pricelist_id.currency_id.id != currency_id:
                    # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                    new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(new_list_price, line.order_id.pricelist_id.currency_id)
                discount = (new_list_price - price) / new_list_price * 100
                if discount > 0:
                    line.discount = discount
                    line.discount1 = discount
                else:
                    line.discount = 0.0
                    line.discount1 = 0.0

            # if item.min_amount > price_multi_cat_ppi and\
            #     line.price_unit == price and\
            #     item.min_amount > (price * line.product_uom_qty):
            #     # From _compute_amount()
            #     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            #     line.update({
            #         'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            #         'price_total': taxes['total_included'],
            #         'price_subtotal': taxes['total_excluded'],
            #     })
            # Update price_reduce
            line.price_reduce = price


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
