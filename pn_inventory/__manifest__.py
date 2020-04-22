# -*- coding: utf-8 -*-
{
    'name': 'Pennyu Inventory',
    'version': '11.0.1.0.0',
    'author': 'Portcities Ltd',
    'summary': 'Pennyu Inventory',
    'website': 'https://www.portcities.net',
    'category': 'stock',
    'description': """
    v.1.0 \n
    Author : Yusuf Danny \n
    Pivot view of stock warehouse orderpoint
    """,
    'data': [
        'views/stock_warehouse_orderpoint_view.xml',
        'views/stock_picking_view.xml',
    ],
    'depends': ['delivery'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
