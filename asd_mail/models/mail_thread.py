# -*- coding: utf-8 -*-
# Copyright 2025 PT Arkana Solusi Digital

from lxml import etree

from odoo import models, api
from odoo.tools.safe_eval import safe_eval

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_portal_groups(self):
        groups_obj = self.env["res.groups"]
        groups_domain = [("is_portal", "=", True)]
        groups_ids = groups_obj.search(groups_domain)
        return groups_ids
    
    def _is_portal_users(self):
        portal_groups = self._get_portal_groups()
        if portal_groups:
            portal_users = portal_groups.mapped("users")
            return self.env.user.id in portal_users.ids
        return False

    # Replace method
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MailThread, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='message_ids']"):
                # the 'Log a note' button is employee only
                options = safe_eval(node.get('options', '{}'))
                is_employee = self.env.user.has_group('base.group_user')
                is_portal_users = self._is_portal_users()
                # grant access to the log button if the user is portal user
                options['display_log_button'] = is_employee or is_portal_users
                # save options on the node
                node.set('options', repr(options))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
