from odoo import api, fields, models


class AgedPayableColumn(models.AbstractModel):
    _inherit = 'account.aged.partner'

    def get_columns_name(self, options):
        due_date_cols = {'name': 'Due Date', 'class': 'text', 'style': 'white-space:nowrap;'}

        columns = super(AgedPayableColumn, self).get_columns_name(options)
        columns2 = columns[:]
        columns2.insert(1, due_date_cols)
        return columns2

    @api.model
    def get_lines(self, options, line_id=None):
        lines = super(AgedPayableColumn, self).get_lines(options, line_id)

        lines2 = lines[:]

        def build_dict(seq, key):
            return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

        info_by_id = build_dict(lines, key="id")

        for line in lines:
            idx = info_by_id.get(line['id']).get('index')
            if not line.get('unfoldable') and line.get('name').strip() != 'Total':
                sml = self.env['account.move.line'].browse(line['id'])
                old_cols = lines[idx]['columns']
                lines2[idx]['columns'] = [{'name': sml.date_maturity}]
                lines2[idx]['columns'].extend(old_cols)
            else:
                old_cols = lines[idx]['columns']
                lines2[idx]['columns'] = [{'name': ''}]
                lines2[idx]['columns'].extend(old_cols)

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
