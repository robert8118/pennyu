# -*- coding: utf-8 -*-
from odoo import http

# class AccountBalance(http.Controller):
#     @http.route('/account_balance/account_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_balance/account_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_balance.listing', {
#             'root': '/account_balance/account_balance',
#             'objects': http.request.env['account_balance.account_balance'].search([]),
#         })

#     @http.route('/account_balance/account_balance/objects/<model("account_balance.account_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_balance.object', {
#             'object': obj
#         })