from itertools import chain
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    # Add some validation
    @api.multi
    def write(self, vals):
        res = super(ProductPricelist, self).write(vals)
        for item in self.item_ids:
            if item.min_amount < 0.0:
                raise ValidationError(_(f'Negative amount ({item.min_amount:,}) in {item.name} - {self.name} is not allowed.'))
            if item.compute_price == 'fixed' and item.min_amount > 0.0 and item.fixed_price > item.min_amount:
                raise ValidationError(_(f'Fixed price ({item.fixed_price:,}) in {item.name} - {self.name} cannot exceed the minimum amount ({item.min_amount:,}).'))
        return res

    # Replace method
    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Add categs_ids for query
        categs_ids_temp = [categs for item in self.item_ids if item.applied_on == '4_product_categories' and item.categs_ids for categs in item.categs_ids.ids]
        categs_ids = list(set(categs_ids_temp))

        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'LEFT JOIN product_category_product_pricelist_item_rel AS categs '
            'ON categs.product_pricelist_item_id = item.id '
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (categs.product_category_id IS NULL OR categs.product_category_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc, item.min_amount desc',
            (prod_tmpl_ids, prod_ids, categ_ids, categs_ids, self.id, date, date))

        item_ids_temp = [x[0] for x in self._cr.fetchall()]
        item_ids = [i for n, i in enumerate(item_ids_temp) if i not in item_ids_temp[:n]]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue
                
                # Add categs_ids Condition; Add sum of price multi cat ppi for price reference
                if rule.applied_on == '4_product_categories' and rule.categs_ids:
                    if product.categ_id.id not in rule.categs_ids.ids:
                        continue
                    product_ids = self.env['product.product'].search([('categ_id', 'in', rule.categs_ids.ids)])
                    # Skip sale_order_id because price_sum_multi_cat_ppi cannot be calculated if there is no sale_order_id
                    sale_order_id = self._context.get('sale_order_id', False)
                    if not sale_order_id:
                        continue
                    sale_order_line_id = self.env['sale.order.line'].search([('order_id', '=', sale_order_id), ('product_id', 'in', product_ids.ids)])
                    price_unit_multi_cat_ppi = sale_order_line_id.mapped('price_unit')
                    qty_multi_cat_ppi = sale_order_line_id.mapped('product_uom_qty')
                    price_sum_multi_cat_ppi = sum([price_unit_multi_cat_ppi[i] * qty_multi_cat_ppi[i] for i in range(len(price_unit_multi_cat_ppi))])

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                # Add min_amount Condition
                if rule.min_amount > 0.0:
                    price_total_temp = price * qty_in_product_uom
                    if rule.min_amount > price_total_temp:
                        if not price_sum_multi_cat_ppi:
                            continue
                        else:
                            if rule.min_amount > price_sum_multi_cat_ppi:
                                continue

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'standard_price':
                    # The cost of the product is always in the company currency
                    price = product.cost_currency_id.compute(price, self.currency_id, round=False)
                else:
                    price = product.currency_id.compute(price, self.currency_id, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # Add selection by overriding this field
    applied_on = fields.Selection([
        ('3_global', 'Global'),
        ('2_product_category', ' Product Category'),
        ('4_product_categories', 'Product Categories'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='3_global', required=True,
        help='Pricelist Item applicable on selected option')
    
    categs_ids = fields.Many2many('product.category', string='Product Categories', ondelete='cascade')
    min_amount = fields.Float('Min. Amount')

    # Replace method
    @api.one
    @api.depends('categ_id', 'categs_ids', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        if self.categ_id:
            self.name = _("Category: %s") % (self.categ_id.name)
        elif self.categs_ids:
            categ_name = [categ.name for categ in self.categs_ids]
            self.name = _("Categories: %s") % (", ".join(categ_name))
        elif self.product_tmpl_id:
            self.name = self.product_tmpl_id.name
        elif self.product_id:
            self.name = self.product_id.display_name.replace('[%s]' % self.product_id.code, '')
        else:
            self.name = _("All Products")

        if self.compute_price == 'fixed':
            self.price = ("%s %s") % (self.fixed_price, self.pricelist_id.currency_id.name)
        elif self.compute_price == 'percentage':
            self.price = _("%s %% discount") % (self.percent_price)
        else:
            self.price = _("%s %% discount and %s surcharge") % (self.price_discount, self.price_surcharge)

    # Override method
    @api.onchange('applied_on')
    def _onchange_applied_on(self):
        res = super(PricelistItem, self)._onchange_applied_on()
        if self.applied_on != '4_product_categories':
            self.categs_ids = [(6, 0, [])]
        return res
    