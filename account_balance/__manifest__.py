# -*- coding: utf-8 -*-
{
    'name': "Account Balance",

    'summary': """
        Show account balance per journal items
    """,

    'description': """
        
    """,

    'author': "Arkana",
    'website': "https://www.arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_reports',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}