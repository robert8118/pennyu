from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    ict_id = fields.Many2one('inter.company.transfer',string = "ICT",copy=False)
    