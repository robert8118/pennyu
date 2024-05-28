from odoo import models, fields, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    show_whatsapp_button = fields.Boolean(string='Show Whatsapp Button', compute='_show_whatsapp_button')

    def _get_group_access(self, groups=[], groups_name=[]):
        group_ids = []
        result = False
        query = ""
        if not groups:
            raise ValidationError(_('groups parameter not found. Please add groups parameter first'))
        for group in groups:
            group_ids.append(self.env.ref(group).id)
        if len(group_ids) == 1:
            filter_group_id = f'= {group_ids[0]}'
        elif len(group_ids) > 1:
            filter_group_id = f'IN {tuple(group_ids)}'
        if not any(groups_name):
            query = """
                SELECT
                    1
                FROM
                    res_groups_users_rel rgur
                WHERE
                    rgur.uid = %(uid)s
                    AND rgur.gid %(gid)s """ % {
                        'uid': self._uid,
                        'gid': filter_group_id
                    }
        else:
            if len(groups_name) == 1:
                filter_group_name = f"= '{groups_name[0]}'"
            elif len(groups_name) > 1:
                filter_group_name = f"IN {tuple(groups_name)}"
            query = """
                SELECT
                    1
                FROM
                    res_groups_users_rel rgur
                LEFT JOIN res_groups rg ON
                    rg.id = rgur.gid
                WHERE
                    rgur.uid = %(uid)s
                    AND (rgur.gid %(gid)s
                    OR rg.name %(group_name)s) """ % {
                        'uid': self._uid,
                        'gid': filter_group_id,
                        'group_name': filter_group_name
                    }
        self.env.cr.execute(query)
        query_result = self.env.cr.fetchone()

        if not query_result:
            result = False
        else:
            result = True
        return result
    
    def _show_whatsapp_button(self):
        access_value = self._get_group_access(groups=['account.group_account_manager'], groups_name=['Budgeting'])
        if self.state not in ['cancel', 'sent', 'reconciled'] and access_value:
            self.show_whatsapp_button = True
        else:
            self.show_whatsapp_button = False

    def send_whatsapp_message(self):
        whatsapp_wizard = self.env['whatsapp.wizard'].create({
            'partner_id': self.partner_id.id,
            'account_payment_id': self.id,
            'type': 'payment',
            'mode': 'direct',
        })
        return whatsapp_wizard.send_whatsapp_message()