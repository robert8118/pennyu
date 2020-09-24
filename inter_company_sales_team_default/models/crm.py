from odoo import models, fields, tools, api, _
from odoo.exceptions import AccessError, UserError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        '''Cek sales team apakah sesuai company SO atau tidak. Jika tidak sesuai diganti dgn yg sesuai'''
        team_id = super(CrmTeam, self)._get_default_team_id(user_id)
        # ambil company tujuan dari context
        if self._context.get('force_company') and team_id.company_id and team_id.company_id.id != self._context.get('force_company'):
            team_id = self.env['crm.team'].sudo().search([
                ('company_id', 'child_of', [self._context.get('force_company')])], limit=1)
        if not team_id:
            team_id = self.env['crm.team'].sudo().search(
                [('company_id', '=', False)], limit=1)
        return team_id
