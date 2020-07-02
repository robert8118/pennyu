# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class MailActivityMixin(models.AbstractModel):
    """inherit mail activity mixin to pass restriction warning cant write,
    adding group portal user sales"""
    _inherit = "mail.activity.mixin"


    activity_ids = fields.One2many(
        'mail.activity', 'res_id', 'Activities',
        auto_join=True,
        groups='base.group_user,pn_user.group_portal_rws,pn_user.group_portal_sales,pn_user.group_portal_transporter,pn_user.group_stock_inv_user,pn_user.group_cust_sale_user,pn_user.group_cust_stock_user',
        domain=lambda self: [('res_model', '=', self._name)])
    activity_state = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned')], string='State',
        compute='_compute_activity_state',
        groups='base.group_user,pn_user.group_portal_rws,pn_user.group_portal_sales,pn_user.group_portal_transporter,pn_user.group_stock_inv_user,pn_user.group_cust_sale_user,pn_user.group_cust_stock_user',
        help='Status based on activities\nOverdue: Due date is already passed\n'
             'Today: Activity date is today\nPlanned: Future activities.')
    activity_user_id = fields.Many2one(
        'res.users', 'Responsible',
        related='activity_ids.user_id',
        search='_search_activity_user_id',
        groups='base.group_user,pn_user.group_portal_rws,pn_user.group_portal_sales,pn_user.group_portal_transporter,pn_user.group_stock_inv_user,pn_user.group_cust_sale_user,pn_user.group_cust_stock_user')
    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Next Activity Type',
        related='activity_ids.activity_type_id',
        search='_search_activity_type_id',
        groups='base.group_user,pn_user.group_portal_rws,pn_user.group_portal_sales,pn_user.group_portal_transporter,pn_user.group_stock_inv_user,pn_user.group_cust_sale_user,pn_user.group_cust_stock_user')
    activity_date_deadline = fields.Date(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,  # store to enable ordering + search
        groups='base.group_user,pn_user.group_portal_rws,pn_user.group_portal_sales,pn_user.group_portal_transporter,pn_user.group_stock_inv_user,pn_user.group_cust_sale_user,pn_user.group_cust_stock_user')
    activity_summary = fields.Char(
        'Next Activity Summary',
        related='activity_ids.summary',
        search='_search_activity_summary',
        groups='base.group_user,pn_user.group_portal_rws,pn_user.group_portal_sales,pn_user.group_portal_transporter,pn_user.group_stock_inv_user,pn_user.group_cust_sale_user,pn_user.group_cust_stock_user')
