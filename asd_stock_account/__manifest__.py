# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pennyu WMS Accounting",
    "summary": """Inventory, Logistic, Valuation, Accounting""",
    "description": """
        1. Automatic creation of stock journals whenever there is a change in the Inventory Valuation configuration in Product Categories
    """,
    "author": "Arkana Solusi Digital",
    "website": "https://github.com/robert8118/pennyu",
    "category": "Hidden",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        # odoo addons
        "stock_account"

        # third party addons
        # developed addons
    ],
    # always loaded
    "data": [
        # group
        # data
        # global action
        # view
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
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
