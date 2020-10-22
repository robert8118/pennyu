# -*- coding: utf-8 -*-
{
    'name': 'MRP Shift',
    'version': '11.0.1.0.0',
    'author': 'Amirul',
    'summary': 'Manage shift MO',
    'website': '',
    'category': 'Manufacturing',
    'description': """
    """,
    'data': [
        'data/data.xml',
        'views/mrp_shift_view.xml',
        'views/mrp_production_view.xml',
        'views/mrp_workorder_view.xml',
        'security/ir.model.access.csv'
    ],
    'depends': ['mrp'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
