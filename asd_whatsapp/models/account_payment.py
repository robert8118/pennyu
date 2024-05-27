from odoo import models, fields, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    show_whatsapp_button = fields.Boolean(string='Show Whatsapp Button', compute='_show_whatsapp_button')

    def _get_group_access(self, groups=[]):
        group_ids = []
        result = False
        if not groups:
            raise ValidationError(_('groups parameter not found. Please add groups parameter first'))
        for group in groups:
            group_ids.append(self.env.ref(group).id)
        if len(group_ids) == 1:
            filter_query = '= %d' % group_ids[0]
        elif len(group_ids) > 1:
            filter_query = 'IN %s' % (tuple(group_ids),)
        query = """
            SELECT 
                1 
            FROM
                res_groups_users_rel rgur
            WHERE 
                rgur.uid = %(uid)s
                AND rgur.gid %(gid)s """ % {
                    'uid': self._uid,
                    'gid': filter_query
                }
        self.env.cr.execute(query)
        query_result = self.env.cr.fetchone()

        if query_result or self._uid == 1:
            result = True
        else:
            result = False
        return result
    
    def _show_whatsapp_button(self):
        access_value = self._get_group_access(groups=['account.group_account_invoice', 'account.group_account_manager'])
        self.show_whatsapp_button = access_value

    def send_whatsapp_message(self):
        whatsapp_wizard = self.env['whatsapp.wizard'].create({
            'partner_id': self.partner_id.id,
            'account_payment_id': self.id,
            'type': 'payment',
            'mode': 'direct',
        })
        return whatsapp_wizard.send_whatsapp_message()