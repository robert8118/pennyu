from odoo import api, fields, models


class AgedPayableColumn(models.AbstractModel):
    _inherit = 'account.aged.partner'

    def get_columns_name(self, options):
        columns = super(AgedPayableColumn, self).get_columns_name(options)
        columns.append({'name': 'Due Date', 'class': 'number', 'style': 'white-space:nowrap;'})
        return columns

    @api.model
    def get_lines(self, options, line_id=None):
        lines = super(AgedPayableColumn, self).get_lines(options, line_id)

        lines2 = lines[:]

        def build_dict(seq, key):
            return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

        info_by_id = build_dict(lines, key="id")

        for line in lines:
            if not line.get('unfoldable') and line.get('name').strip() != 'Total':
                sml = self.env['account.move.line'].browse(line['id'])
                idx = info_by_id.get(line['id']).get('index')
                lines2[idx]['columns'].append({'name': sml.date_maturity})

        return lines2

# class AgedPayable(models.AbstractModel):
#     _inherit = 'report.account.report_agedpartnerbalance'
#
#     def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):
#         res, total, lines = super(AgedPayable, self)._get_partner_move_lines(account_type, date_from, target_move, period_length)
#
#         lines2 = lines.copy()
#         for k, v in lines.items():
#             lines2[k].append({'due_date': v[0]['line'].date_maturity})
#         return res, total, lines2
