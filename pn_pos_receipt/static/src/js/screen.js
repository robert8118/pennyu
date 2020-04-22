odoo.define('sa_pos_print.screens', function (require) {
"use strict";

var screen = require('point_of_sale.screens')
var core = require('web.core');
var QWeb = core.qweb;

screen.ReceiptScreenWidget.include({
	print_xml: function() {
        var receipt = QWeb.render('XmlReceipt', this.get_receipt_render_env());
        this.pos.proxy.print_receipt(receipt);
        this.pos.get_order()._printed = true;
    },
});

});