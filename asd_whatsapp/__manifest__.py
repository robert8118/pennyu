# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': "Pennyu - WhatsApp",
    'summary': """WhatsApp for Pennyu""",
    "author": "PT Arkana Solusi Digital",
    "website": "https://arkana.co.id",
    'category': 'WhatsApp',
    'version': '0.1',
    'depends': [
        'base',
        'account'
    ],
    'data': [
        'wizard/whatsapp_wizard_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
