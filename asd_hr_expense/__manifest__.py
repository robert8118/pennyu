# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': "Pennyu - Expenses",
    'summary': """
        Expenses for Pennyu""",
    'author': "PT Arkana Solusi Digital",
    'website': "http://www.arkana.co.id",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': [
        # odoo addons
        'hr_expense'

        # third party addons
        # developed addons
        ],
    'data': [
        # group
        # data
        # global action

        # view
        'views/hr_expense_views.xml',

        # wizard
        # report paperformat
        # report template
        # report action
        # assets
        # onboarding action
        # action menu
        # menu
        # security
    ],
    "installable": True,
    "application": True,
}
