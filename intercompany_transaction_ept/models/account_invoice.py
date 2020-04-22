from odoo import api, models, fields ,_

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    ict_id = fields.Many2one('inter.company.transfer',String ="ICT",copy=False)
    
    @api.model
    def create(self,vals):
        invoice = super(account_invoice,self).create(vals)
        order_id = self.env['sale.order'].search([('name','=',invoice.origin)])
        if not order_id:
            order_id = self.env['purchase.order'].search([('name','=',invoice.origin)])
        if order_id and order_id.ict_id:
            invoice.ict_id = order_id.ict_id.id
        return invoice