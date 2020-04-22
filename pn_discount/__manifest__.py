{
    'name': 'Discount System - Pennyu',
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'depends': ['purchase', 'sale'],
    'author': 'Portcities Ltd',
    'summary': 'Multiple Discount System in Sale, Purchase, and Invoice',
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/account_invoice_view.xml',
        ],
    'description': """
    v.1.0.0
        Author : Yusuf \n
        - Custom Discount in Sale Order, Purchase Order and Invoice
    """,
    'qweb': [],
    'website': 'https://www.portcities.net',
    'image': [],
    'auto_install': False,
    'installable': True,
    'application': False,
}
