from odoo import models, fields, api, _
from odoo.exceptions import Warning 

class intercompany_trasfer_config(models.Model):    
    _name = "inter.company.transfer.config"
    _rec_name = "sequence_id"
    
    @api.model
    def _default_company(self):
        return self.env.user.company_id.id
    
    sequence_id = fields.Many2one('ir.sequence', 'Sequence')
    auto_confirm_orders = fields.Boolean('Auto Confirm Orders')
    auto_create_invoices = fields.Boolean('Auto Create Invoices')
    auto_validate_invoices = fields.Boolean('Auto Validate Invoices')
    company_id = fields.Many2one('res.company', string='Company',
        readonly=True, compute=_default_company, store=True)
    description = fields.Char("Description")
    filter_refund = fields.Selection([('refund', 'Create a draft credit note'), ('cancel', 'Cancel: create credit note and reconcile')],
        default='refund', string='Refund Method', required=True, help='Refund base on this type. You can not Modify and Cancel if the invoice is already reconciled')
    @api.multi
    def unlink(self):
        raise Warning(_("You can not delete this record"))
