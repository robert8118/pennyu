# -*- coding: utf-8 -*-
# Copyright 2025 PT Arkana Solusi Digital

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, pycompat, float_repr, float_round, float_compare
from odoo.addons import decimal_precision as dp

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _prepare_impacted_products(self, product_category=None, product_template=None):
        impacted_product_ids = []
        impacted_products = self.env["product.product"]
        products_orig_qty_at_date = {}

        # get the impacted products
        domain = [("type", "=", "product")]
        if product_category is not None:
            domain += [("categ_id", "=", product_category.id)]
        elif product_template is not None:
            domain += [("product_tmpl_id", "=", product_template.id)]
        else:
            raise ValueError()
        products = self.env["product.product"].search_read(domain, ["qty_at_date"])
        for product in products:
            impacted_product_ids.append(product["id"])
            products_orig_qty_at_date[product["id"]] = product["qty_at_date"]
        impacted_products |= self.env["product.product"].browse(impacted_product_ids)
        return products_orig_qty_at_date, impacted_products

    def _prepare_account_move_stock(self, products, description):
        move_vals_list = []
        quant_obj = self.env["stock.quant"]
        location_obj = self.env["stock.location"]

        for product in products:
            quant_locs = quant_obj.sudo().read_group([("product_id", "in", product.ids)], ["location_id"], ["location_id"])
            quant_loc_ids = [loc["location_id"][0] for loc in quant_locs]
            
            locations_domain = [
                    ("usage", "=", "internal"),
                    ("company_id", "=", self.env.user.company_id.id),
                    ("id", "in", quant_loc_ids)
                ]
            locations = location_obj.search(locations_domain)

            product_accounts = {rec.id: rec.product_tmpl_id.get_product_accounts() for rec in product}

            for location in locations:
                for prod in product.with_context(location=location.id, compute_child=False).filtered(lambda r: r.valuation == "real_time"):
                    product = prod
                    if not product_accounts[product.id].get("stock_input", False):
                        raise UserError(_("You don't have any input valuation account defined on your product category. You must define one before processing this operation."))
                    if not product_accounts[product.id].get("stock_valuation", False):
                        raise UserError(_("You don't have any stock valuation account defined on your product category. You must define one before processing this operation."))
                    if not product_accounts[product.id].get("stock_output", False):
                        raise UserError(_("You don't have any output valuation account defined on your product category. You must define one before processing this operation."))

                    qty_available = product.qty_available
                    total_price = product.standard_price * qty_available
                    if qty_available:
                        # Accounting Entries
                        if total_price > 0:
                            debit_account_id = product_accounts[product.id]["stock_output"].id
                            credit_account_id = product_accounts[product.id]["stock_valuation"].id
                        else:
                            debit_account_id = product_accounts[product.id]["stock_valuation"].id
                            credit_account_id = product_accounts[product.id]["stock_input"].id

                        move_vals = {
                            "journal_id": product_accounts[product.id]["stock_journal"].id,
                            "company_id": location.company_id.id,
                            "line_ids": [(0, 0, {
                                "name": description,
                                "account_id": debit_account_id,
                                "debit": abs(total_price),
                                "credit": 0,
                                "product_id": product.id,
                            }), (0, 0, {
                                "name": description,
                                "account_id": credit_account_id,
                                "debit": 0,
                                "credit": abs(total_price),
                                "product_id": product.id,
                            })],
                        }
                    move_vals_list.append(move_vals)
        return move_vals_list

class ProductCategory(models.Model):
    _inherit = "product.category"

    def write(self, vals):
        impacted_categories = {}
        move_vals_list = []
        product_obj = self.env["product.product"]
        move_obj = self.env["account.move"]

        if "property_valuation" in vals:
            # When the valuation are changed on a product category, we empty out and replenish the stock for each impacted products.
            new_valuation = vals.get("property_valuation")

            for product_category in self:
                valuation_impacted = False
                if new_valuation and new_valuation != product_category.property_valuation:
                    valuation_impacted = True
                if valuation_impacted is False:
                    continue

                if new_valuation:
                    description = _("Valuation method change for product category %s: from %s to %s.", product_category.display_name, product_category.property_valuation, new_valuation)
                products_orig_qty_at_date, products = product_obj._prepare_impacted_products(description, product_category=product_category)
                impacted_categories[product_category] = (products, description, products_orig_qty_at_date)

        res = super(ProductCategory, self).write(vals)

        for product_category, (products, description, products_orig_qty_at_date) in impacted_categories.items():
            if product_category.property_valuation == "real_time":
                # Use qty_at_date or qty_available?
                move_vals_list += product_obj._prepare_account_move_stock(product=products, description=description)

        # Create the account moves.
        if move_vals_list:
            account_moves = move_obj.sudo().create(move_vals_list)
            account_moves._post()
        return res
