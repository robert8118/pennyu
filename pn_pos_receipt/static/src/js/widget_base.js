odoo.define('pn_pos_receipt.widget_base', function (require) {
    "use strict";

var pos_widget = require('point_of_sale.BaseWidget');
var field_utils = require('web.field_utils');
var utils = require('web.utils');
var round_di = utils.round_decimals;

pos_widget.include({
    format_currency_no_comma: function(amount,precision){
        var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 0};
        amount = this.format_currency_no_symbol_no_comma(amount,precision);

        if (currency.position === 'after') {
            return amount + ' ' + (currency.symbol || '');
        } else {
            return (currency.symbol || '') + ' ' + amount;
        }
    },

    format_currency_no_symbol_no_comma: function(amount, precision) {
        var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
        var decimals = 0;

        if (precision && this.pos.dp[precision] !== undefined) {
            decimals = this.pos.dp[precision];
        }

        if (typeof amount === 'number') {
            amount = round_di(amount,decimals).toFixed(decimals);
            amount = field_utils.format.float(round_di(amount, decimals), {digits: [69, decimals]});
        }

        return amount;
    },
});

});