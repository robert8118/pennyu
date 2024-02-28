from odoo import api, models, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    user_id = fields.Many2one('res.users', string='Active User', default=lambda self: self.env.user)
    can_see_sale_price = fields.Boolean('Read Sale Price', compute='_can_see_sale_price', default=False)

    @api.depends('user_id')
    def _can_see_sale_price(self):
        for rec in self:
            is_share = self.env.user.share
            rec.can_see_sale_price = True if not is_share else False

