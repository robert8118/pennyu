# -*- coding: utf-8 -*-
{
    'name': 'Pennyu - Sale Order Report Fix',
    'version': '11.0.1.0.0',
    'summary': 'Sale Order Report',
    'description': """
Bug Fixes for module Pennyu - Sale Order Report (pn_sale)
    """,
    'category': 'Generic Modules',
    'author': "Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "http://www.arkana.co.id",
    'depends': [
        'pn_sale',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
