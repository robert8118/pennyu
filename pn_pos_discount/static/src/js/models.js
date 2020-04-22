odoo.define('pn_pos_discount.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

     // load models for only password
     models.load_models([
        {
            model: 'res.users',
            fields: ['authorize_password'],
            domain : function(self){
                    return [['authorize_discount_pos','=', true]];
                },
            loaded: function(self,password_authorize){
                var temp = [];
                for(var i=0; i<password_authorize.length; i++){
                    temp.push(password_authorize[i].authorize_password);
                }
                self.password_authorize = temp;
            },
        }
    ]);
});