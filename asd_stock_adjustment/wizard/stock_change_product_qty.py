from odoo import api, models, fields, tools, _

class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    def _get_journal_stock_adjustment(self):
        journal_obj = self.env["account.journal"]
        journal_domain = [
            ("active", "=", True),
            ("type", "=", "general"),
            ("code", "=", "STJ"),
            ("company_id", "=", self.env.user.company_id.id),
        ]
        journal_id = journal_obj.search(journal_domain, limit=1)
        
        return journal_id
    
    def _prepare_move_line_stock_adjustment(self, product_id, th_quantity, th_cost):
        diff_qty = self.new_quantity - product_id.qty_available
        diff_cost = diff_qty * th_cost
        line_vals = {
            "name": f"INV:INV: {product_id.name}",
            "company_id": self.env.user.company_id.id,
            "quantity": diff_qty,
        }
        debit_line_vals = line_vals.copy()
        credit_line_vals = line_vals.copy()

        if self.new_quantity > th_quantity:
            debit_line_vals.update({
                "account_id": product_id.categ_id.property_stock_account_input_categ_id.id,
                "debit": diff_cost,
            })
            credit_line_vals.update({
                "account_id": product_id.categ_id.property_stock_adjustment_in.id,
                "credit": diff_cost,
            })
        else:
            debit_line_vals.update({
                "account_id": product_id.categ_id.property_stock_adjustment_out.id,
                "debit": diff_cost * -1,
                "quantity": diff_qty * -1,
            })
            credit_line_vals.update({
                "account_id": product_id.categ_id.property_stock_account_output_categ_id.id,
                "credit": diff_cost * -1,
                "quantity": diff_qty * -1,
            })
        aml_values = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

        return aml_values

    def _action_start_line(self):
        am_obj = self.env["account.move"]
        product_id = self.product_id.with_context(location=self.location_id.id, lot_id=self.lot_id.id)
        th_quantity = product_id.qty_available
        th_cost = product_id.standard_price

        am_stock_adjusment = am_obj.create({
            "ref": "Stock Adjustment",
            "journal_id": self._get_journal_stock_adjustment().id,
            "company_id": self.env.user.company_id.id,
            "line_ids": self._prepare_move_line_stock_adjustment(product_id=product_id, th_quantity=th_quantity, th_cost=th_cost),
        })
        am_stock_adjusment.post()

        res = {
            "product_qty": self.new_quantity,
            "location_id": self.location_id.id,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_id.uom_id.id,
            "theoretical_qty": th_quantity,
            "prod_lot_id": self.lot_id.id,
        }

        return res