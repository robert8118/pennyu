from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # res_partner modul base
    name = fields.Char(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange')
    category_id = fields.Many2many(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    ## Internal Notes
    comment = fields.Text(track_visibility='onchange')
    picking_warn = fields.Selection(track_visibility='onchange')
    picking_warn_msg = fields.Text(track_visibility='onchange')
    invoice_warn = fields.Selection(track_visibility='onchange')
    invoice_warn_msg = fields.Text(track_visibility='onchange')
    sale_warn = fields.Selection(track_visibility='onchange')
    sale_warn_msg = fields.Text(track_visibility='onchange')
    purchase_warn = fields.Selection(track_visibility='onchange')
    purchase_warn_msg = fields.Text(track_visibility='onchange')
    
    ## Sales & Purchases
    ### Sale
    customer = fields.Boolean(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    opt_out = fields.Boolean(track_visibility='onchange')
    property_delivery_carrier_id = fields.Many2one(track_visibility='onchange')
    message_bounce = fields.Integer(track_visibility='onchange')
    property_product_pricelist = fields.Many2one(track_visibility='onchange')
    
    ### Misc
    ref = fields.Char(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    industry_id = fields.Many2one(track_visibility='onchange')
    
    ### Warehouse
    property_stock_customer = fields.Many2one(track_visibility='onchange')
    property_stock_supplier = fields.Many2one(track_visibility='onchange')
    
    
    ### Purchase
    supplier = fields.Boolean(track_visibility='onchange')
    
    ### Point of Sale
    barcode = fields.Char(track_visibility='onchange')

    ## Accounting
    ### Sale
    property_payment_term_id = fields.Many2one(track_visibility='onchange')
    trust = fields.Selection(track_visibility='onchange')
    limit_ids = fields.Many2many(track_visibility='always')
    
    ### Fiscal Information
    property_account_position_id = fields.Many2one(track_visibility='onchange')
    
    ### Purchase
    property_supplier_payment_term_id = fields.Many2one(track_visibility='onchange')
    
    ### Accounting Entries
    property_account_receivable_id = fields.Many2one(track_visibility='onchange')
    property_account_payable_id = fields.Many2one(track_visibility='onchange')
    
    # res_partner modul aos_l10n_id
    blok = fields.Char(track_visibility='onchange')
    nomor = fields.Char(track_visibility='onchange')
    rt = fields.Char(track_visibility='onchange')
    rw = fields.Char(track_visibility='onchange')
    kelurahan_id = fields.Many2one(track_visibility='onchange')
    kecamatan_id = fields.Many2one(track_visibility='onchange')
    kabupaten_id = fields.Many2one(track_visibility='onchange')

    # res_partner modul efaktur
    fp_date = fields.Datetime(track_visibility='onchange')
    is_npwp = fields.Boolean(track_visibility='onchange')
    npwp = fields.Char(track_visibility='onchange')
    
    ktp = fields.Char(track_visibility='onchange')
    cluster = fields.Selection(track_visibility='onchange')
    code_transaction = fields.Selection(track_visibility='onchange')

    # res_partner modul msi_partner
    no_ktp = fields.Char(track_visibility='onchange')
    is_npwp_pribadi = fields.Boolean(track_visibility='onchange')
    nama_npwp_pribadi = fields.Char(track_visibility='onchange')
    alamat_npwp_pribadi = fields.Char(track_visibility='onchange')