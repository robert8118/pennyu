from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def decrease_qty_invoice(self, ai, pick_from):
        for move in self.move_lines:
            if move.quantity_done:
                if pick_from == 'purchase':
                    ail = ai.invoice_line_ids.filtered(lambda x: x.purchase_line_id == move.purchase_line_id)
                elif pick_from == 'sale':
                    ail = ai.invoice_line_ids.filtered(lambda x: x.sale_line_id == move.sale_line_id)
                if ail:
                    ail.quantity -= move.quantity_done

    def auto_invoice(self, picking_id=None, return_status=False):
        if self:
            sp_id = self
        else:
            sp_id = picking_id
        if sp_id.group_id:
            data = {}
            purchase_status = (sp_id.picking_type_id.code == 'incoming' and not return_status) or (
                    sp_id.picking_type_id.code == 'outgoing' and return_status)
            sale_status = (sp_id.picking_type_id.code == 'outgoing' and not return_status) or (
                    sp_id.picking_type_id.code == 'incoming' and return_status)

            if return_status:
                sp_origin_name = sp_id.origin.replace('Return of', '').strip()
                sp_origin = self.env['stock.picking'].search([('name', '=', sp_origin_name)], limit=1)
                ai = self.env['account.invoice'].search(
                    [('origin', '=', f'{sp_origin.group_id.name}: {sp_origin_name}')], limit=1)
                if ai.state == 'draft':
                    pick_from = 'purchase' if purchase_status else 'sale'
                    sp_id.decrease_qty_invoice(ai, pick_from)
                    return False

            if return_status:
                data.update({
                    'name': sp_id.origin
                })

            if purchase_status:
                po = self.env['purchase.order'].search([('name', '=', sp_id.group_id.name)], limit=1)
                origin = f'{po.name}: {sp_id.name}' if not return_status else ai.number
                payment_term_id = po.payment_term_id.id
                company_id = po.company_id.id
                journal_id = self.env['account.journal'].search(
                    [('type', '=', 'purchase'),
                     ('company_id', '=', company_id)], limit=1)
                journal_id = journal_id[:1].id
                account_id = self.env['account.account'].search(
                    [('internal_type', '=', 'payable'),
                     ('company_id', '=', company_id),
                     ('deprecated', '=', False)], limit=1)
                account_id = account_id[:1].id
                inv_type = 'in_invoice' if not return_status else 'in_refund'
                user_id = self._uid
                data.update({
                    'reference': po.partner_ref
                })
            elif sale_status:
                so = self.env['sale.order'].search([('name', '=', sp_id.group_id.name)], limit=1)
                origin = f'{so.name}: {sp_id.name}' if not return_status else ai.number
                payment_term_id = so.payment_term_id.id
                company_id = so.company_id.id
                journal_id = self.env['account.journal'].search(
                    [('type', '=', 'sale'),
                     ('company_id', '=', company_id)], limit=1)
                journal_id = journal_id[:1].id
                account_id = self.env['account.account'].search(
                    [('internal_type', '=', 'receivable'),
                     ('company_id', '=', company_id),
                     ('deprecated', '=', False)], limit=1)
                account_id = account_id[:1].id
                inv_type = 'out_invoice' if not return_status else 'out_refund'
                user_id = so.user_id.id
                data.update({
                    'partner_id': so.partner_invoice_id.id or so.partner_id.id,
                    'partner_shipping_id': so.partner_shipping_id.id,
                    'team_id': so.team_id.id
                })
            data.update({
                'type': inv_type,
                'date_invoice': fields.Date.today(),
                'release_to_pay': 'yes',
                'partner_id': data.get('partner_id') or sp_id.partner_id.id,
                'payment_term_id': payment_term_id,
                'account_id': account_id,
                'journal_id': journal_id,
                'company_id': company_id,
                'origin': origin,
                'user_id': user_id,
            })
            inv = self.env['account.invoice'].create(data)
            for move in sp_id.move_lines:
                if move.quantity_done:
                    data_line = {
                        'invoice_id': inv.id,
                        'product_id': move.product_id.id,
                        'quantity': move.quantity_done,
                        'uom_id': move.product_uom.id
                    }
                    
                    if purchase_status:
                        product_name = '%s: %s' % (po.name, move.product_id.display_name)
                        account_id = self.env['account.account'].search(
                            [('code', '=', '202100'), ('company_id', '=', company_id)], limit=1).id
                        price_unit = move.purchase_line_id.price_unit / move.product_uom.factor * move.purchase_line_id.product_uom.factor
                        tax_ids = [(6, 0, move.purchase_line_id.taxes_id.mapped('id'))]
                        analytic_account_id = move.purchase_line_id.account_analytic_id.id

                        data_line.update({
                            'purchase_line_id': move.purchase_line_id.id,
                        })

                    elif sale_status:
                        product_name = '%s: %s' % (so.name, move.product_id.display_name)
                        account_id = self.env['account.account'].search(
                            [('code', '=', '400100'), ('company_id', '=', company_id)], limit=1).id
                        price_unit = move.sale_line_id.price_unit / move.product_uom.factor * move.sale_line_id.product_uom.factor

                        tax_ids = [(6, 0, move.sale_line_id.tax_id.mapped('id'))]
                        analytic_account_id = so.analytic_account_id.id

                        data_line.update({
                            'sale_line_id': move.sale_line_id.id,
                            'discount': move.sale_line_id.discount
                        })

                    data_line.update({
                        'name': product_name,
                        'account_id': account_id,
                        'price_unit': price_unit,
                        'account_analytic_id': analytic_account_id,
                        'invoice_line_tax_ids': tax_ids,
                    })

                    inv_line = self.env['account.invoice.line'].create(data_line)
                    if sp_id.picking_type_id.code == 'outgoing':
                        move.sale_line_id.update({
                            'invoice_lines': [(4, inv_line.id, 0)]
                        })

            inv.compute_taxes()
            return inv
        else:
            return False

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for rec in self :
            return_status = False
            if rec.origin :
                if 'Return' in rec.origin :
                    return_status = True
            if rec.location_id.usage in ('customer','supplier') or rec.location_dest_id.usage in ('customer','supplier'):
                rec.auto_invoice(return_status=return_status)
        return res


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    # def process(self):
    #     res = super(StockBackorderConfirmation, self).process()
    #     return_status = False
    #     if self.pick_ids.origin:
    #         if 'Return' in self.pick_ids.origin :
    #             return_status = True
    #     if self.pick_ids.location_id.usage in ('customer','supplier') or self.pick_ids.location_dest_id.usage in ('customer','supplier'):
    #         self.env['stock.picking'].auto_invoice(picking_id=self.pick_ids, return_status=return_status)
    #     return res

    # def process_cancel_backorder(self):
    #     res = super(StockBackorderConfirmation, self).process_cancel_backorder()
    #     return_status = False
    #     if self.pick_ids.origin:
    #         if 'Return' in self.pick_ids.origin:
    #             return_status = True
    #     if self.pick_ids.location_id.usage in ('customer','supplier') or self.pick_ids.location_dest_id.usage in ('customer','supplier'):
    #         self.env['stock.picking'].auto_invoice(picking_id=self.pick_ids, return_status=return_status)
    #     return res


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    # def process(self):
    #     res = super(StockImmediateTransfer, self).process()
    #     return_status = False
    #     if self.pick_ids.origin:
    #         if 'Return' in self.pick_ids.origin:
    #             return_status = True
    #     if self.pick_ids.location_id.usage in ('customer','supplier') or self.pick_ids.location_dest_id.usage in ('customer','supplier'):
    #         self.env['stock.picking'].auto_invoice(picking_id=self.pick_ids, return_status=return_status)
    #     return res
