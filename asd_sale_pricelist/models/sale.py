from odoo import api, fields, models, tools, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def recompute_pricelist(self):
        self.upd_multi_cat_pricelist()
    
    # Method to recompute multi cat Pricelist
    def upd_multi_cat_pricelist(self):
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
            line.price_reduce = price

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
