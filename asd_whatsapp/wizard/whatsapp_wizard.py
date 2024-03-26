from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime as dt

class WhatsAppIntegration(models.TransientModel):
    _name = 'whatsapp.wizard'
    _defaults = {
        'mode': 'edit'
    }

    partner_id = fields.Many2one('res.partner', string='Recipient')
    account_payment_id = fields.Many2one('account.payment')
    send_message = fields.Text(string='Message', compute='_get_message_text', inverse='_set_message_text')
    type = fields.Char()
    mode = fields.Char(default='edit')
    is_edited = fields.Char(default='')
    
    def get_payment_text(self, data):
        payment_id = data.account_payment_id
        payment_date = dt.strptime(payment_id.payment_date, '%Y-%m-%d').date()
        text = f"""Halo {data.partner_id.name if data.partner_id else 'N/A'},%0A%0A

%09Pembayaran anda pada tanggal {payment_date.strftime('%d')}-{payment_date.strftime('%b')}-{payment_date.strftime('%Y')} sejumlah Rp. {payment_id.amount:,} telah kami terima, apabila anda tidak melakukan konfirmasi, maka jumlah pembayaran akan kami anggap sesuai.%0A%0A

Terima kasih."""

        return text
    
    @api.depends('partner_id')
    def _get_message_text(self):
        for data in self:
            if not data.is_edited:
                text = ''
                if data.type == 'payment':
                    if data.mode != 'direct':
                        data.account_payment_id = data.env.context.get('default_account_payment_id', False)
                    text = self.get_payment_text(data)
                data.send_message = text
            else:
                data.send_message = data.is_edited

    @api.depends('send_message')
    def _set_message_text(self):
        for data in self:
            data.is_edited = data.send_message

    def send_whatsapp_message(self):
        user_phone_number = self.partner_id.phone or self.partner_id.mobile
        message_body = self.send_message
        self.is_edited = ''
        if not user_phone_number:
            raise UserError('No WhatsApp number is provided for this customer!')
        
        if user_phone_number[0] == "+":
            phone_number = [number for number in user_phone_number if number.isnumeric()]
            phone_number = "".join(phone_number)
            phone_number = "+" + phone_number
            if 12 <= len(phone_number) <= 15:
                link = "https://web.whatsapp.com/send?phone=" + phone_number
                url_id = link + "&text=" + message_body
                return {
                    'type':'ir.actions.act_url',
                    'url': url_id,
                    'target':'new',
                    'res_id': self.id,
                }
            else:
                raise UserError('WhatsApp does not exists. Please add a valid WhatsApp number!')

        else:
            raise UserError('No country code! Please add a valid WhatsApp number along with country code!')