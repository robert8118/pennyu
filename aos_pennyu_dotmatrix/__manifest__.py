{
	"name": "Pennyu Dot Matrix Printer",
	"version": "11.0.1.0.0",
	"depends": ["vit_dotmatrix", "pn_dotmatrix","stock", "sale_management", "efaktur"],
	"author": "Alphasoft",
	"category": "Utilities",
	'website': 'https://www.alphasoft.co.id',
	'summary': 'Pennyu Dot Matrix',
	"description": """
	v.1.0 \n
    Author : APR \n
    1. inherit modul vit_dotmatrix\n
    2. add proforma on delivery
	""",
	"data": [
		#"view/purchase_order.xml",
		"view/stock_picking.xml",
		#"view/sale_order.xml",
		"data/templates.xml",
		"data/nota_pennyu_templates.xml",
		"data/surat_jalan_templates.xml",
		"security/dotmatrix_security.xml"
	],
	"installable": True,
	"auto_install": False,
    "application": False,
}