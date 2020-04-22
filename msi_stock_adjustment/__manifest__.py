{
    "name"          : "Stock Adjustment",
    "version"       : "1.0",
    "author"        : "Mutiara Sistem Integrasi",
    "website"       : "https://mutiaraintegrasi.id",
    "category"      : "Stock",
    "license"       : "LGPL-3",
    "support"       : "eko@mutiaraintegrasi.id",
    "summary"       : "Stock Adjustment",
    "description"   : """
        Add account on Stock Adjustment
    """,
    "depends"       : [
        "product",
        "stock",
        "stock_account",
    ],
    "data"          : [
        "view/msi_stock_adjusment.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [
        "static/description/images/main_screenshot.png",
    ],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}