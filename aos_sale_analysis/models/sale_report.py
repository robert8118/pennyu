from odoo import fields, models

class SaleReport(models.Model):
    _inherit = 'sale.report'

    customer_invoice_city = fields.Char(string="Invoice City")
    customer_invoice_state = fields.Many2one('res.country.state',string="Invoice State")
    customer_dlv_city = fields.Char(string="Delivery City") 
    customer_dlv_state = fields.Many2one('res.country.state',string="Delivery State") 
    customer_tags = fields.Many2one('res.partner.category', string="Partner Tags")


    def _select(self):
        select_str = super(SaleReport, self)._select()
        select_str += """ ,invoice_addr.city as customer_invoice_city, 
                        invoice_addr.state_id as customer_invoice_state, 
                        deliv_addr.city as customer_dlv_city, 
                        deliv_addr.state_id as customer_dlv_state,
                        categ.id as customer_tags
        """
        return select_str

    def _from(self):
        from_str = super(SaleReport, self)._from()
        from_str += """
                left join res_partner invoice_addr on (partner.id=invoice_addr.parent_id and invoice_addr.type='invoice')
                left join res_partner deliv_addr on (partner.id=deliv_addr.parent_id and deliv_addr.type='delivery')
                left join res_partner_res_partner_category_rel pr_ct on (partner.id=pr_ct.partner_id)
                left join res_partner_category categ on (pr_ct.category_id=categ.id)
        """
        return from_str
    
    def _group_by(self):
        group_by_str = super(SaleReport, self)._group_by()
        group_by_str += """ ,invoice_addr.city, 
                        invoice_addr.state_id, 
                        deliv_addr.city, 
                        deliv_addr.state_id,
                        categ.id
                        """
        return group_by_str