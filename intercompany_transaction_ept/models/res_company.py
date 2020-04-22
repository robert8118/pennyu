from odoo import fields, models

class resCompany(models.Model):

    _inherit = "res.company"

    intercompany_user_id = fields.Many2one('res.users',string="Intercompnay User")    
    sale_journal = fields.Many2one('account.journal',string="Sale Journal" )
    purchase_journal = fields.Many2one('account.journal',string="Purchase Journal")
    