from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_return_type(self, pick_type_code, **kwargs):
        return_type = False
        if kwargs.get("is_return"):
            if pick_type_code == "incoming":
                return_type = "incoming"
            elif pick_type_code == "outgoing":
                return_type = "outgoing"
        return return_type
    
    def _get_order_type(self, picking_id, **kwargs):
        pick_type, order_type = False, False
        # incoming_return: do_return, return_of_gr_return
        # outgoing_return: gr_return, return_of_do_return
        if kwargs.get("is_return"):
            if picking_id.picking_type_id.code == "incoming":
                pick_type = "incoming_return"
            elif picking_id.picking_type_id.code == "outgoing":
                pick_type = "outgoing_return"
        else:
            if picking_id.picking_type_id.code == "incoming":
                pick_type = "incoming"
            elif picking_id.picking_type_id.code == "outgoing":
                pick_type = "outgoing"
        
        purchase_transfer = ["incoming", "incoming_return", "outgoing_return"]
        sale_transfer = ["outgoing", "outgoing_return", "incoming_return"]
        if picking_id.group_id.sale_id:
            if pick_type in sale_transfer:
                order_type = "sale"
        else:
            if pick_type in purchase_transfer:
                order_type = "purchase"
        return order_type
    
    def _get_order_data(self, order_type, picking_id):
        order_obj, order_id = False, False

        if order_type == "sale":
            order_obj = self.env["sale.order"]
        elif order_type == "purchase":
            order_obj = self.env["purchase.order"]

        order_domain = [("name", "=", picking_id.group_id.name)]
        order_id = order_obj.search(order_domain, limit=1)
        return order_id

    def _get_origin_invoice_return_picking(self, picking_id):
        invoice_origin_id = False
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
        invoice_obj, invoice_line_obj = self.env["account.invoice"], self.env["account.invoice.line"]
        invoice_id = invoice_obj
        if self:
            picking_id = self
        else:
            picking_id = picking_id
        
        if not picking_id.group_id:
            # skip auto create invoice if not group_id
            return False
        data = {}
        order_type = self._get_order_type(picking_id=picking_id, is_return=return_status)
        return_type = self._get_return_type(pick_type_code=picking_id.picking_type_id.code, is_return=return_status)

        if return_status:
            data.update({"name": picking_id.origin})
            invoice_origin = self._get_origin_invoice_return_picking(picking_id=picking_id)

            if invoice_origin.state == "draft":
                picking_id.decrease_qty_invoice(invoice_origin, order_type)
                # Skip auto create invoice if origin status draft
                return False
            invoice_id += invoice_origin

        data.update({
            "order_type": order_type,
            "return_type": return_type,
            "picking_id": picking_id,
            "invoice_id": invoice_id,
        })
        invoice_data = self._prepare_data_account_invoice(data=data)
        invoice_data.update({
            "date_invoice": fields.Date.today(),
            "release_to_pay": "yes",
            "partner_id": invoice_data.get("partner_id") or picking_id.partner_id.id,
        })
        inv = invoice_obj.create(invoice_data)

        data_line = {
            "order_type": order_type,
            "picking_id": picking_id,
            "invoice_id": inv,
        }
        for move_line in picking_id.move_lines:
            if move_line.quantity_done:
                data_line.update({"move_line": move_line})
                invoice_data_line = self._prepare_data_account_invoice_line(data_line=data_line)
                inv_line = invoice_line_obj.create(invoice_data_line)
                if picking_id.picking_type_id.code == "outgoing":
                    move_line.sale_line_id.update({
                        "invoice_lines": [(4, inv_line.id, 0)]
                    })
        inv.compute_taxes()
        return inv
        
    def _prepare_data_account_invoice(self, **kwargs):
        journal_obj, account_obj = self.env["account.journal"], self.env["account.account"]
        data = kwargs.get("data")
        order_type, return_type, picking_id, invoice_id = data["order_type"], data["return_type"], data["picking_id"], data["invoice_id"]
        sale_group_id = picking_id.group_id.sale_id
        # clear key which not in account.invoice field
        data = {key: data[key] for key in data if key == "name"}

        if order_type == "purchase":
            if not return_type or return_type == "incoming":
                invoice_type = "in_invoice"
            elif return_type == "outgoing":
                invoice_type = "in_refund"
            internal_type = "payable"
        elif order_type == "sale":
            if not return_type or return_type == "outgoing":
                invoice_type = "out_invoice"
            elif return_type == "incoming":
                invoice_type = "out_refund"
            internal_type = "receivable"

        order_id = self._get_order_data(order_type=order_type, picking_id=picking_id)
        # Handling return of Delivery Order (DO) return
        return_of_do_return = order_type == "purchase" and not order_id and sale_group_id
        if return_of_do_return:
            order_id = sale_group_id
        if not order_id:
            raise ValidationError(_("order_id not found"))
        
        origin = f"{order_id.name}: {picking_id.name}" if not return_type else invoice_id.number
        payment_term_id = order_id.payment_term_id.id
        company_id = order_id.company_id.id
        user_id = order_id.user_id.id if order_type == "sale" else self._uid
        
        journal_domain = [
            ("company_id", "=", company_id),
            ("type", "=", order_type)
        ]
        journal_id = journal_obj.search(journal_domain, limit=1)
        
        account_domain = [
            ("internal_type", "=", internal_type),
            ("company_id", "=", company_id),
            ("deprecated", "=", False)
        ]
        account_id = account_obj.search(account_domain, limit=1)
        
        data.update({
            "order_id": order_id,
            "type": invoice_type,
            "origin": origin,
            "payment_term_id": payment_term_id,
            "company_id": company_id,
            "journal_id": journal_id[:1].id,
            "account_id": account_id[:1].id,
            "user_id": user_id,
        })
        
        if order_type == "purchase":
            if sale_group_id and order_id != sale_group_id:
                data.update({
                        "reference": order_id.partner_ref
                    })
        elif order_type == "sale":
            data.update({
                "partner_id": order_id.partner_invoice_id.id or order_id.partner_id.id,
                "partner_shipping_id": order_id.partner_shipping_id.id,
                "team_id": order_id.team_id.id
            })
        return data
        
    def _prepare_data_account_invoice_line(self, **kwarg):
        account_obj = self.env["account.account"]
        data_line = kwarg.get("data_line")
        order_type, move_line, invoice_id, picking_id = data_line["order_type"], data_line["move_line"], data_line["invoice_id"], data_line["picking_id"]
        order_id = self._get_order_data(order_type=order_type, picking_id=picking_id)
        # replace data_line
        data_line = {
            "invoice_id": invoice_id.id,
            "product_id": move_line.product_id.id,
            "quantity": move_line.quantity_done,
            "uom_id": move_line.product_uom.id
        }

        if order_type == "purchase":
            account_code = "202100"
            order_line = move_line.purchase_line_id
            tax_ids = [(6, 0, order_line.taxes_id.mapped("id"))]
            analytic_account_id = order_line.account_analytic_id.id
            data_line.update({
                "purchase_line_id": order_line.id,
            })
        elif order_type == "sale":
            account_code = "400100"
            order_line = move_line.sale_line_id
            tax_ids = [(6, 0, order_line.tax_id.mapped("id"))]
            analytic_account_id = order_id.analytic_account_id.id
            data_line.update({
                "sale_line_id": order_line.id,
                "discount": order_line.discount
            })

        product_name = f"{order_id.name}: {move_line.product_id.display_name}"
        account_domain = [
            ("code", "=", account_code),
            ("company_id", "=", invoice_id.company_id.id),
        ]
        account_id = account_obj.search(account_domain, limit=1).id

        price_unit = order_line.price_unit / move_line.product_uom.factor * order_line.product_uom.factor

        data_line.update({
            "name": product_name,
            "account_analytic_id": analytic_account_id,
            "account_id": account_id,
            "price_unit": price_unit,
            "invoice_line_tax_ids": tax_ids,
        })

        return data_line
