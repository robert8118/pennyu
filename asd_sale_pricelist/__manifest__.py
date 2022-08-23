{
    'name': "Pennyu - Pricelist",
    'summary': """
        Adding the number of product categories and adding the minimum amount rule on the Pricelist""",
    'author': "PT Arkana Solusi Digital",
    'website': "https://www.arkana.co.id",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'sale', 'product'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_pricelist_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
    ],
}
