# -*- coding: utf-8 -*-
{
    'name': 'Partner Addon',
    'version': '11.0.1.0.0',
    'author': 'MSI',
    'summary': 'partner',
    'website': 'https://www.mutiaraintegrasi.idt',
    'category': 'stock',
    'description': """
    v.1.0 \n
    Author : Eko \n
    Pivot view of stock warehouse orderpoint
    """,
    'data': [
        'views/msi_partner.xml',
    ],
    'depends': ['delivery'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
