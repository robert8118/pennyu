odoo.define('norton_point_of_sale.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var _t  = require('web.core')._t;

    screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var orderlines = order.get_orderlines()
                var discount_product = false;
                // looping each orderline
                if(orderlines != 0){
                    for (var i = 0; i < orderlines.length; i++){
                        //check discount each orderline
                        if(orderlines[i].get_discount() > 0){
                            discount_product = true;
                        }
                    }
                }
                if (discount_product){
                    var user = self.pos.user;
                    if(!user.authorize_discount_pos){
                        var password = self.pos.password_authorize;
                        self.gui.show_popup('password',{
                            'title': _t('Password ?'),
                            confirm: function(pw) {
                                if (!password.includes(pw)) {
                                    self.gui.show_screen('products');
                                    self.gui.show_popup('error',{
                                        'title': _t('Error: Password incorrect'),
                                        'body': _t('your password is incorrect'),
                                    });
                                }
                            },
                            cancel: function(){
                                self.gui.show_screen('products');
                            }
                        });
                    }
                }

            });
        }
    
    });

});