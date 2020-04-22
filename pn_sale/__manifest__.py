# -*- coding: utf-8 -*-
{
    'name': 'Pennyu - Sale Order Report',
    'version': '11.0.1.0.0',
    'summary': 'Sale Order Report',
    'description': """
    v 1.0
        author : Alvin Adji \n
        * Create new Template for Sale Order Report

    """,
    'category': 'Generic Modules',
    'author': "Portcities Ltd",
    'website': "http://www.portcities.net",
    'depends': [
        'sale',
    ],
    'data': [
        'data/sale_report_paper_format.xml',
        'views/sale_order_view.xml',
        'report/sale_report.xml',
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
