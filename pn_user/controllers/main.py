# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
""" file Controlers External User"""

from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.http import request

class HomePage(Home):
    """controller route redirect into dashboard for portal user sales"""

    @http.route()
    def index(self, *args, **kw):
        user_login = request.env['res.users'].sudo().browse(request.session.uid)
        if user_login.has_group('pn_user.group_portal_rws'):
            return http.local_redirect('/web', query=request.params, keep_hash=True)
        if user_login.has_group('pn_user.group_portal_sales'):
            return http.local_redirect('/web', query=request.params, keep_hash=True)
        if user_login.has_group('pn_user.group_portal_transporter'):
            return http.local_redirect('/web', query=request.params, keep_hash=True)
        if user_login.has_group('pn_user.group_stock_inv_user'):
            return http.local_redirect('/web', query=request.params, keep_hash=True)
        return super(HomePage, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        user_login = request.env['res.users'].sudo().browse(request.session.uid)
        if user_login.has_group('pn_user.group_portal_rws'):
            return redirect if redirect else '/web'
        if user_login.has_group('pn_user.group_portal_sales'):
            return redirect if redirect else '/web'
        if user_login.has_group('pn_user.group_portal_transporter'):
            return redirect if redirect else '/web'
        if user_login.has_group('pn_user.group_stock_inv_user'):
            return redirect if redirect else '/web'
        return super(HomePage, self)._login_redirect(uid, redirect=redirect)
