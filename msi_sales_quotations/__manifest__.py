# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Quotations Addon',



    'summary': 'Sales Quotations',

    'sequence': 32,
    'images': [''],
    'depends': ['base','sale','stock','account'],
    'data': [
        'data/sequence.xml',

        'views/msi_account_invoice.xml',
        'views/msi_advance_settlement.xml',
        'views/msi_advance_permanent.xml',
        'views/msi_rekap_giro.xml',
        'views/msi_collection.xml',
        'views/msi_payment_double_approval.xml',
    ],
    "application": True,

}
