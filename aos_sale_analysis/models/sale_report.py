from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    customer_invoice_city = fields.Char(string="Invoice City")
    customer_invoice_state = fields.Many2one(
        'res.country.state', string="Invoice State")
    customer_dlv_city = fields.Char(string="Delivery City")
    customer_dlv_state = fields.Many2one(
        'res.country.state', string="Delivery State")
    # customer_tags = fields.Many2one('res.partner.category', string="Partner Tags")
    customer_tags = fields.Many2many(
        'res.partner.category', related='partner_id.category_id', string="Partner Tags")
    deliv_state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting another Operation'), (
        'confirmed', 'Waiting'), ('assigned', 'Ready'), ('done', 'Done'), ('cancel', 'Cancelled')], string="Delivery Status")

    def _select(self):
        select_str = super(SaleReport, self)._select()
        select_str += """ ,invoice_addr.city as customer_invoice_city, 
                        invoice_addr.state_id as customer_invoice_state, 
                        deliv_addr.city as customer_dlv_city, 
                        deliv_addr.state_id as customer_dlv_state,
                        deliv.state as deliv_state
        """
        return select_str

    def _from(self):
        from_str = super(SaleReport, self)._from()
        from_str += """
                left join res_partner invoice_addr on (s.partner_invoice_id=invoice_addr.id)
                left join res_partner deliv_addr on (s.partner_shipping_id=deliv_addr.id)
                left join stock_picking deliv on (s.id=deliv.sale_id and deliv.state not in ('cancel','draft'))
        """
        return from_str

    def _group_by(self):
        group_by_str = super(SaleReport, self)._group_by()
        group_by_str += """ ,invoice_addr.city, 
                        invoice_addr.state_id, 
                        deliv_addr.city, 
                        deliv_addr.state_id,
                        deliv.state
                        """
        return group_by_str
