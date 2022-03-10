from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class CreditLimit(models.Model):
    _name = "credit.limit"
    _description = "Customer Credit Limit"

    @api.multi
    @api.depends('partner_ids')
    def _is_global(self):
        for rec in self :
            is_global = True
            if rec.partner_ids :
                is_global = False
            rec.is_global = is_global

    name = fields.Char(required=True)
    type = fields.Selection(
        string='Rule by',
        selection=[
            ('amount', 'Amount'),
            ('count', 'Invoice Count'),
            ('overdue', 'Over Due'),
        ], required=True)
    amount = fields.Float(
        string='Max Amount',
        digits=dp.get_precision('Product Price'),
        required=False)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=False,
        default=lambda self: self.env.user.company_id.currency_id)
    count = fields.Integer(
        string='Max Invoice Count',
        required=False)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=False,
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(
        string='Active',
        default=True)
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_limit_rel',
        'limit_id',
        'partner_id',
        string='Customer')
    is_global = fields.Boolean(
        string='Is Global?',
        compute='_is_global',
        help='Apply for all customer',
        store=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')

    @api.constrains('partner_ids')
    def _check_double_limit(self):
        for rec in self :
            for p in rec.partner_ids :
                other_limit_ids = self.search([
                    ('partner_ids','in',p.ids),
                    ('id','!=',rec.id),
                    ('type','=',rec.type),
                ])
                if other_limit_ids :
                    raise ValidationError(_(f'Credit limit with same type for customer {p.display_name} already exist: {", ".join(other_limit_ids.mapped("display_name"))}'))

    @api.onchange('company_id')
    def onchange_company(self):
        self.partner_ids = False
