from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_origin_invoice_return_picking(self, picking_id):
        picking_obj, invoice_obj = self.env["stock.picking"], self.env["account.invoice"]
        # Get origin return picking
        picking_origin_name = picking_id.origin.replace("Return of", "").strip()
        picking_origin_domain = [("name", "=", picking_origin_name)]
        picking_origin = picking_obj.search(picking_origin_domain, limit=1)
        # Get invoice origin return picking
        picking_origin_have_origin = picking_origin.mapped("move_lines.origin_returned_move_id.picking_id")
        if not any(picking_origin_have_origin):
            invoice_origin_name = f"{picking_origin.group_id.name}: {picking_origin_name}"
            invoice_origin_domain = [("origin", "=", invoice_origin_name)]
        else:
            invoice_origin_domain = [("name", "=", picking_origin.origin)]
        invoice_origin_id = invoice_obj.search(invoice_origin_domain, limit=1)
        return invoice_origin_id

    def auto_invoice(self, picking_id=None, return_status=False):
        picking_id = self or picking_id
        # skip auto create invoice if not have group_id
        if not picking_id.group_id:
            return False
        # init variable
        invoice_obj, invoice_line_obj = self.env["account.invoice"], self.env["account.invoice.line"]
        picking_type_code = picking_id.picking_type_id.code
        origin = picking_id.origin
        if picking_type_code in ["incoming", "outgoing"]:
            group_name = picking_id.group_id.name
            # Handling PO with group SO
            if not origin.startswith("PO") and (group_name.startswith("SO") or origin.startswith("SO")):
                order_type = "sale"
            elif group_name.startswith("PO") or origin.startswith("PO"):
                order_type = "purchase"
        data = {
            "invoice_id": invoice_obj,
            "picking_id": picking_id,
            "order_type": order_type,
            "return_type": False,
        }
        # handling return transfer
        if return_status:
            invoice_origin = self._get_origin_invoice_return_picking(picking_id=picking_id)
            if invoice_origin.state == "draft":
                picking_id.decrease_qty_invoice(invoice_origin, order_type)
                # Skip auto create invoice if origin status draft
                return False
            data.update({
                "return_type": "incoming" if picking_type_code == "incoming" else "outgoing",
                "name": origin,
                "invoice_id": invoice_origin,
            })
        # get order_id
        order_obj = self.env["sale.order"] if order_type == "sale" else self.env["purchase.order"]
        order_domain = [("name", "=", picking_id.group_id.name)]
        order_id = order_obj.search(order_domain, limit=1)
        data.update({"order_id": order_id})
        # prepare data and create invoice header
        invoice_data = self._prepare_data_account_invoice(data=data)
        inv = invoice_obj.create(invoice_data)
        # prepare data and create invoice line
        data_line = {
            "order_type": order_type,
            "order_id": order_id,
            "picking_id": picking_id,
            "invoice_id": inv,
        }
        for move_line in picking_id.move_lines:
            if move_line.quantity_done:
                data_line.update({"move_line": move_line})
                invoice_data_line = self._prepare_data_account_invoice_line(data_line=data_line)
                inv_line = invoice_line_obj.create(invoice_data_line)
                if picking_id.picking_type_id.code == "outgoing":
                    move_line.sale_line_id.update({"invoice_lines": [(4, inv_line.id, 0)]})
        inv.compute_taxes()
        return inv
        
    def _prepare_data_account_invoice(self, **kwargs):
        journal_obj, account_obj = self.env["account.journal"], self.env["account.account"]
        data = kwargs.get("data")
        order_type, return_type, picking_id, invoice_id, order_id = data["order_type"], data["return_type"], data["picking_id"], data["invoice_id"], data["order_id"]
        # clear key which not in account.invoice field
        data = {key: data[key] for key in data if key == "name"}
        # init variable
        internal_type = "receivable" if order_type == "sale" else "payable"
        invoice_type = "out_invoice" if order_type == "sale" else "in_invoice"
        if return_type:
            invoice_type = "out_refund" if order_type == "sale" else "in_refund"        
        company_id = order_id.company_id.id
        # get journal_id
        journal_domain = [
            ("company_id", "=", company_id),
            ("type", "=", order_type)
        ]
        journal_id = journal_obj.search(journal_domain, limit=1)
        # get account_id
        account_domain = [
            ("internal_type", "=", internal_type),
            ("company_id", "=", company_id),
            ("deprecated", "=", False)
        ]
        account_id = account_obj.search(account_domain, limit=1)
        # update data dict
        if order_type == "sale":
            data.update({"team_id": order_id.team_id.id})
        elif order_type == "purchase":
            data.update({"reference": order_id.partner_ref})
        data.update({
            "type": invoice_type,
            "origin": f"{order_id.name}: {picking_id.name}" if not return_type else invoice_id.number,
            "payment_term_id": order_id.payment_term_id.id,
            "company_id": company_id,
            "journal_id": journal_id[:1].id,
            "account_id": account_id[:1].id,
            "user_id": order_id.user_id.id if order_type == "sale" else self._uid,
            "date_invoice": fields.Date.today(),
            "release_to_pay": "yes",
            "partner_id": (order_id.partner_invoice_id.id or order_id.partner_id.id) if order_type == "sale" else picking_id.partner_id.id,
            "partner_shipping_id": order_id.partner_shipping_id.id if order_type == "sale" else False,
        })
        return data
        
    def _prepare_data_account_invoice_line(self, **kwarg):
        account_obj = self.env["account.account"]
        data_line = kwarg.get("data_line")
        order_type, order_id, move_line, invoice_id = data_line["order_type"], data_line["order_id"], data_line["move_line"], data_line["invoice_id"]
        # replace data_line
        data_line = {
            "invoice_id": invoice_id.id,
            "product_id": move_line.product_id.id,
            "quantity": move_line.quantity_done,
            "uom_id": move_line.product_uom.id
        }
        # set variable
        order_line = move_line.sale_line_id if order_type == "sale" else move_line.purchase_line_id
        # get account_id
        account_code = "400100" if order_type == "sale" else "202100"
        account_domain = [
            ("code", "=", account_code),
            ("company_id", "=", invoice_id.company_id.id),
        ]
        account_id = account_obj.search(account_domain, limit=1).id
        data_line.update({
            "name": f"{order_id.name}: {move_line.product_id.display_name}",
            "account_analytic_id": order_id.analytic_account_id.id if order_type == "sale" else order_line.account_analytic_id.id,
            "account_id": account_id,
            "price_unit": order_line.price_unit / move_line.product_uom.factor * order_line.product_uom.factor,
            "invoice_line_tax_ids": [(6, 0, order_line.tax_id.mapped("id"))] if order_type == "sale" else [(6, 0, order_line.taxes_id.mapped("id"))],
            "purchase_line_id": order_line.id if order_type == "purchase" else False,
            "sale_line_id": order_line.id if order_type == "sale" else False,
            "discount": order_line.discount if order_type == "sale" else 0,
        })
        return data_line
