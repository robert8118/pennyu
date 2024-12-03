# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pennyu - Disable create master data",
    "summary": """Disable the create master data feature when creating/updating Sale Order data""",
    "description": """
        The following create master data is disabled: Products, Analytics accounts
    """,
    "author": "PT Arkana Solusi Digital",
    "website": "https://arkana.co.id",
    "category": "Sale",
    "version": "0.1",
    "depends": ["asb_sale"],
    "data": [
        "views/sale_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
