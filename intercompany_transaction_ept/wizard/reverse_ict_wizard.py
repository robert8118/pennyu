from odoo import api, fields, models,_
from odoo.exceptions import Warning

class ReverseICT(models.TransientModel):
    _name = "reverse.ict.wizard"
    
    ict_id = fields.Many2one('inter.company.transfer', string="ICT")
    reverse_line_ids = fields.One2many('reverse.ict.wizard.line', 'reverse_ict_id', string="Reverse ICT Lines")
    
    @api.multi
    def create_reverse_ict(self):
        reverse_ict_line_obj = self.env['inter.company.transfer.line']
        reverse_ict = self.ict_id.copy(default={'type':'ict_reverse', 'ict_id':self._context.get('active_id')})
        
        product_lines = []
        for line in self.reverse_line_ids:
            reverse_ict_line = reverse_ict_line_obj.create({
                        'transfer_id':reverse_ict.id,
                        'product_id':line.product_id.id,
                        'quantity':line.quantity or 1,
                        'price':line.price,
                    })
            
            product_lines.append(reverse_ict_line.id)

        reverse_ict.write({'line_ids':[(6, 0, product_lines)], 'ict_id':self.ict_id.id})
        return True


class ReverseICTLines(models.TransientModel):

    _name = "reverse.ict.wizard.line"
    
    reverse_ict_id = fields.Many2one("reverse.ict.wizard", string="Reverse ICT")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float("Quantity", default=1)
    price = fields.Float('Price')
    qty_delivered = fields.Float(string="Delivered Qty", store=True)
    
    
    @api.one
    @api.constrains('quantity', 'qty_delivered')
    def _check_quantity(self):
        
        if self.quantity > self.qty_delivered:
            raise Warning(_('You can not enter quantity which was greater than original quantity'))

    
  

    
    
