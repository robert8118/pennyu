# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': "Pennyu - Store Grade",
    'summary': """Store Grade for Pennyu""",
    'description': """Store class to restrict branch company sales""",
    "author": "PT Arkana Solusi Digital",
    "website": "https://arkana.co.id",
    'category': 'Contacts',
    'version': '0.1',
    'depends': [
        # odoo addons
        'contacts',
        'sale',

        # third party addons
        # developed addons
        ],
    'data': [
        # group
        # data
        # global action

        # view
        'views/res_partner_views.xml',
        'views/store_grade_views.xml',

        # wizard
        # report paperformat
        # report template
        # report action
        # assets
        # onboarding action
        # action menu
        # menu

        # security
        # 'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
}
