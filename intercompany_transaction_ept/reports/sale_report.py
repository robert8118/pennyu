from odoo import models,fields

class SaleReport(models.Model):
    _inherit = "sale.report"
    
    ict_id = fields.Many2one('inter.company.transfer',string="Ict")
    
    def _select(self):
        qry = super(SaleReport,self)._select()
        
        qry += ', s.ict_id as ict_id '
        return qry

    def _group_by(self):
        qry = super(SaleReport,self)._group_by()
        qry += ', s.ict_id '
        return qry