from odoo import models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def send_whatsapp_message(self):
        whatsapp_wizard = self.env['whatsapp.wizard'].create({
            'partner_id': self.partner_id.id,
            'account_payment_id': self.id,
            'type': 'payment',
            'mode': 'direct',
        })
        return whatsapp_wizard.send_whatsapp_message()