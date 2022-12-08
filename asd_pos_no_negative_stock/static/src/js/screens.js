odoo.define('asd_pos_no_negative_stock.screens', function (require) {
    "use strict";

    const screens = require('point_of_sale.screens');
    let rpc = require('web.rpc');
    let core = require('web.core');
    let _t = core._t;

    screens.ActionpadWidget.include({
        renderElement: function() {
            let self = this;
            this._super();
            this.$('.pay').click(function(){
                let order = self.pos.get_order();
                let orderlines = order.get_orderlines();
                if (orderlines.length === 0) {
                    return;
                } else {
                    const cid = order.pos.company.id;
                    const products = order.orderlines.models.map(o => ({id: o.product.id, name: o.product.display_name, qty: o.quantity}));
                    // Mencegah tampilan screen pindah ke payment sebelum rendering method check_stock_on_pos
                    self.gui.show_screen('products');
                    rpc.query({
                        model: 'stock.picking',
                        method: 'check_stock_on_pos',
                        args: [cid, products]
                    }).then(function (resultStock) {
                        if (!resultStock) {
                            // Tampilkan screen payment jika tidak ada validasi
                            self.gui.show_screen('payment');
                        } else {
                            const title_pos = _t('Point of Sale Info');
                            const title_stock = _t('Stock Info');
                            let body;
                            if (resultStock[0] === 'duplicate_product') {
                                body = _t(`Duplicate product ${resultStock[1]}. Please delete all product ${resultStock[1]} and then re-input the product.`);
                                self.gui.show_popup('error',{
                                    'title': title_pos,
                                    'body': body,
                                });
                            }
                            else if (resultStock[0] === 'qty_pos_zero') {
                                body = _t(`Product ${resultStock[1]} has no quantity. Please input the quantity.`);
                                self.gui.show_popup('error',{
                                    'title': title_pos,
                                    'body': body,
                                });
                            }
                            else if (resultStock[0] === 'qty_stock_zero') {
                                body = _t(`Insufficient stock for product ${resultStock[1]}. Product stock is zero.`);
                                self.gui.show_popup('error',{
                                    'title': title_stock,
                                    'body': body,
                                });
                            }
                            else if (resultStock[0] === 'qty_in_diff_company') {
                                body = _t(`Insufficient stock for product ${resultStock[1]}. Product stock in this company is zero. Please do an internal transfer to this company if you want to continue the transaction.`);
                                self.gui.show_popup('error',{
                                    'title': title_stock,
                                    'body': body,
                                });
                            }
                            else if (resultStock[0] === 'qty_stock_negative') {
                                body = _t(`Insufficient stock for product ${resultStock[1]}. Product stock in this company is ${resultStock[2]}. Please do an internal transfer to this company if you want to continue the transaction.`);
                                self.gui.show_popup('error',{
                                    'title': title_stock,
                                    'body': body,
                                });
                            }
                            else if (resultStock[0] === 'negative_sum') {
                                body = _t(`Insufficient stock for product ${resultStock[1]}. The required quantity is (${resultStock[2]}) but the product stock in this company is (${resultStock[3]}).`);
                                self.gui.show_popup('error',{
                                    'title': title_stock,
                                    'body': body,
                                });
                            }
                        }
                    });
                }
            });
        }
    });
});
