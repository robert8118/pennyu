# -*- coding: utf-8 -*-
# Copyright 2025 PT Arkana Solusi Digital

from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools

class MailMessage(models.Model):
    _inherit = "mail.message"

    # This method is from BaseModel
    @api.model
    def _search_origin(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        Private implementation of search() method, allowing specifying the uid to use for the access right check.
        This is useful for example when filling in the selection list for a drop-down and avoiding access rights errors,
        by specifying ``access_rights_uid=1`` to bypass access rights check, but not ir.rules!
        This is ok at the security level because this method is private and not callable through XML-RPC.

        :param access_rights_uid: optional user ID to use when checking access rights (not for ir.rules, this is only for ir.model.access)
        :return: a list of record ids or an integer (if count is True)
        """
        self.sudo(access_rights_uid or self._uid).check_access_rights('read')

        # Comment this line to prevent error import expression
        # if expression.is_false(self, args):
        #     # optimization: no need to query, as no record satisfies the domain
        #     return 0 if count else []

        query = self._where_calc(args)
        self._apply_ir_rules(query, 'read')
        order_by = self._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()

        where_str = where_clause and (" WHERE %s" % where_clause) or ''

        if count:
            # Ignore order, limit and offset when just counting, they don't make sense and could
            # hurt performance
            query_str = 'SELECT count(1) FROM ' + from_clause + where_str
            self._cr.execute(query_str, where_clause_params)
            res = self._cr.fetchone()
            return res[0]

        limit_str = limit and ' limit %d' % limit or ''
        offset_str = offset and ' offset %d' % offset or ''
        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str + order_by + limit_str + offset_str
        self._cr.execute(query_str, where_clause_params)
        res = self._cr.fetchall()

        # TDE note: with auto_join, we could have several lines about the same result
        # i.e. a lead with several unread messages; we uniquify the result using
        # a fast way to do it while preserving order (http://www.peterbe.com/plog/uniqifiers-benchmark)
        def _uniquify_list(seq):
            seen = set()
            return [x for x in seq if x not in seen and not seen.add(x)]

        return _uniquify_list([x[0] for x in res])

    # Replace method
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """ Override that adds specific access rights of mail.message, to remove
        ids uid could not see according to our custom rules. Please refer to
        check_access_rule for more details about those rules.

        Non employees users see only message with subtype (aka do not see
        internal logs).

        After having received ids of a classic search, keep only:
        - if author_id == pid, uid is the author, OR
        - uid belongs to a notified channel, OR
        - uid is in the specified recipients, OR
        - uid has a notification on the message, OR
        - uid have read access to the related document is model, res_id
        - otherwise: remove the id
        """
        users_obj = self.env["res.users"]
        thread_obj = self.env["mail.thread"]
        message_obj = self.env["mail.message"]
        # Rules do not apply to administrator
        if self._uid == SUPERUSER_ID:
            return super(MailMessage, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        # Non-employee see only messages with a subtype (aka, no internal logs)
        init_args = args
        is_employee = users_obj.has_group("base.group_user")
        is_portal_users = thread_obj._is_portal_users()
        if not is_employee:
            args = ["&", "&", ("subtype_id", "!=", False), ("subtype_id.internal", "=", False)] + list(args)
        # Perform a super with count as False, to have the ids, not a counter
        ids = super(MailMessage, self)._search(args, offset=offset, limit=limit, order=order, count=False, access_rights_uid=access_rights_uid)
        # Handling access for portal users
        if not ids and is_portal_users:
            ids = message_obj._search_origin(args=init_args, offset=offset, limit=limit, order=order, count=False, access_rights_uid=access_rights_uid)
        if not ids and count:
            return 0
        elif not ids:
            return ids

        pid = self.env.user.partner_id.id
        author_ids, partner_ids, channel_ids, allowed_ids = set([]), set([]), set([]), set([])
        model_ids = {}

        # check read access rights before checking the actual rules on the given ids
        super(MailMessage, self.sudo(access_rights_uid or self._uid)).check_access_rights("read")

        for sub_ids in self._cr.split_for_in_conditions(ids):
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                channel_partner.channel_id as channel_id
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_message_res_partner_needaction_rel" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_message_mail_channel_rel" channel_rel
                ON channel_rel.mail_message_id = m.id
                LEFT JOIN "mail_channel" channel
                ON channel.id = channel_rel.mail_channel_id
                LEFT JOIN "mail_channel_partner" channel_partner
                ON channel_partner.channel_id = channel.id AND channel_partner.partner_id = %%(pid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=pid, ids=list(sub_ids)))
            for id, rmod, rid, author_id, partner_id, channel_id in self._cr.fetchall():
                if author_id == pid:
                    author_ids.add(id)
                elif partner_id == pid:
                    partner_ids.add(id)
                elif channel_id:
                    channel_ids.add(id)
                elif rmod and rid:
                    model_ids.setdefault(rmod, {}).setdefault(rid, set()).add(id)

        allowed_ids = self._find_allowed_doc_ids(model_ids)

        final_ids = author_ids | partner_ids | channel_ids | allowed_ids

        if count:
            return len(final_ids)
        else:
            # re-construct a list based on ids, because set did not keep the original order
            id_list = [id for id in ids if id in final_ids]
            return id_list
