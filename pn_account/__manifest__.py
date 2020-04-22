# -*- coding: utf-8 -*-
{
    'name': 'Pennyu Accounting',
    'version': '11.0.1.0.0',
    'author': 'Portcities Ltd',
    'summary': 'Pennyu Accounting',
    'website': 'https://www.portcities.net',
    'category': 'Accounting',
    'description': """
    v.1.0 \n
    Author : AK \n
    Customize report invoice & vendor bill
    """,
    'data': [
        'views/account_journal_view.xml',
        'views/account_invoice_view.xml',
        'reports/paperformat.xml',
        'reports/account_invoice_report.xml',
    ],
    'depends': ['account', 'report_qweb_element_page_visibility'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
