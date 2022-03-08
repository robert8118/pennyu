# -*- coding: utf-8 -*-
{
    'name': "Credit Limit",
    'summary': """
        Credit limit rules by amount, count of invoice and overdue
    """,
    'description': """
        
    """,
    'author': "Arkana",
    'website': "https://arkana.co.id",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'base',
        'account',
        'sale',
    ],
    'data': [
        'views/credit_limit_views.xml',
        'views/res_partner_views.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'demo': [],
    'images': [],
}