from odoo import models, fields, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    show_whatsapp_button = fields.Boolean(string='Show Whatsapp Button', compute='_show_whatsapp_button')

    def _get_group_access(self, groups=[], groups_name=[]):
        group_ids = []
        result = False
        rgur_table = 'res_groups_users_rel'
        group_table = 'res_groups'
        query = "SELECT 1 "
        from_query = ""
        where_query = ""
        params = {'uid': self._uid}

        if not groups:
            raise ValidationError(_('groups parameter not found. Please add groups parameter first'))
        for group in groups:
            group_ids.append(self.env.ref(group).id)
        if len(group_ids) == 1:
            filter_group_id = f'= {group_ids[0]}'
        elif len(group_ids) > 1:
            filter_group_id = f'IN {tuple(group_ids)}'
        params.update({'gid': filter_group_id})

        if not any(groups_name):
            from_query = f" FROM {rgur_table} "
            where_query = f"""
                WHERE
                    {rgur_table}.uid = %(uid)s
                    AND {rgur_table}.gid %(gid)s
            """ % params
        else:
            if len(groups_name) == 1:
                filter_group_name = f"= '{groups_name[0]}'"
            elif len(groups_name) > 1:
                filter_group_name = f"IN {tuple(groups_name)}"
            params.update({'group_name': filter_group_name})

            from_query = f"""
                FROM
                    {rgur_table}
                LEFT JOIN {group_table} ON
                    {group_table}.id = {rgur_table}.gid
            """
            where_query = f"""
                WHERE
                    {rgur_table}.uid = %(uid)s
                    AND ({rgur_table}.gid %(gid)s
                    OR {group_table}.name %(group_name)s)
            """ % params

        query += from_query + where_query
        self.env.cr.execute(query)
        query_result = self.env.cr.fetchone()

        if not query_result:
            result = False
        else:
            result = True
        return result
    
    def _show_whatsapp_button(self):
        access_value = self._get_group_access(groups=['account.group_account_manager'], groups_name=['Budgeting'])
        allowed_state = self.state not in ['cancel', 'sent', 'reconciled']
        if allowed_state and access_value:
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