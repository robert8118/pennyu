{
	"name": "Pennyu Dot Matrix Printer",
	"version": "11.0.1.0.0",
	"depends": ["vit_dotmatrix"],
	"author": "Portcities Ltd",
	"category": "Utilities",
	'website': 'https://www.portcities.net',
	'summary': 'Pennyu Dot Matrix',
	"description": """
	v.1.0 \n
    Author : APR \n
    1. inherit modul vit_dotmatrix\n
    2. disable template for SO and PO\n
    3. change template of invoice into pdf format\n
	""",
	"data": [
		"view/purchase_order.xml",
		"view/stock_picking.xml",
		"view/sale_order.xml",
		"data/templates.xml"
	],
	"installable": True,
	"auto_install": False,
    "application": False,
}