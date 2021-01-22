{
    'name': 'Input Bulk MO',
    'version': '11.0.0.0.1',
    'description': 'Input bulk MO on one form',
    'summary': 'Input bulk MO on one form',
    'author': 'Amirul',
    'license': 'LGPL-3',
    'category': 'Manufacture',
    'depends': ['base', 'mrp', 'pn_mrp_shift', 'stock_user_access'],
    'data': [
        'views/mrp_production_view.xml',
        'wizards/mrp_production_bulk_view.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'installable': True,
}
