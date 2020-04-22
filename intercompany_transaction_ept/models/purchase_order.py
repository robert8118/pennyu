from odoo import fields, api, models ,_

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    ict_id = fields.Many2one('inter.company.transfer',string = "ICT",copy=False)
    
