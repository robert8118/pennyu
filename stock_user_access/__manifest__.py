# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'User Warehouse',
    'summary': 'User Warehouse',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Stock',
    'author': 'Arkana, Joenan',
    'website': 'https://www.arkana.co.id',
    'description': """User Warehouse""",
    'depends': [
        'stock',
    ],
    'data': [
        'security/security.xml',
        'views/user_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
