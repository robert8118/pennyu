# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Invoice Amount',
    'summary': 'Amount Invoiced in Sale Order',
    'license': 'LGPL-3',
    'version': '11.0',
    'category': 'Sales',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Show Amount Invoiced in Sale Order""",
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_view.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
