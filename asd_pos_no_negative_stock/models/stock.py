from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def check_stock_on_pos(self, company_id, products):
        product_id_list = []
        for p in products:
            if p['id'] in product_id_list:
                return ['duplicate_product', p['name']]
            product_id_list.append(p['id'])
            if p['qty'] == 0:
                return ['qty_pos_zero', p['name']]
        product_ids = self.env['product.product'].search([('id', 'in', product_id_list)])
        for product in product_ids:
            # Validasi hanya untuk produk dengan flag allow_negative_stock == False
            if not product.allow_negative_stock:
                if not product.stock_quant_ids or product.qty_available == 0:
                    return ['qty_stock_zero', product.name, product.qty_available]
                if product.qty_available or product.stock_quant_ids:
                    if product.stock_quant_ids:
                        # Cari qty dengan product terkait dan company_id terkait
                        qtys = self.env['stock.quant'].search([('product_id', '=', product.id), ('company_id', '=', company_id)]).mapped('quantity')
                    # Jika tidak ada stok pada company_id terkait
                    if not qtys:
                        return ['qty_in_diff_company', product.name]
                    total_qty = sum(qtys)
                    if total_qty < 0:
                        return ['qty_stock_negative', product.name, product.qty_available]
                    elif total_qty == 0:
                        return ['qty_stock_zero', product.name, product.qty_available]
                    else:
                        for p in products:
                            if p['id'] == product.id:
                                delta = total_qty - p['qty']
                                if delta < 0:
                                    return ['negative_sum', product.name, p['qty'], qtys]
