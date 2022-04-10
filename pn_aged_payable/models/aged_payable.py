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
            # replace 'id': False dengan minus agar bisa di sort dengan enumerate
            x = -1
            seq_final = seq[:]
            for l in seq_final:
                if not l.get('id'):
                    l['id'] = x
                    x += -1
            return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq_final))

        info_by_id = build_dict(lines, key="id")

        for line in lines:
            idx = info_by_id.get(line['id']).get('index')
            if not line.get('unfoldable') and line.get('name').strip() != 'Total':
                sml = self.env['account.move.line'].browse(line['id'])
                lines2[idx]['due_date'] = sml.date_maturity
                old_cols = lines[idx]['columns']
                lines2[idx]['columns'] = [{'name': sml.date_maturity}]
                lines2[idx]['columns'].extend(old_cols)
            else:
                old_cols = lines[idx]['columns']
                lines2[idx]['columns'] = [{'name': ''}]
                lines2[idx]['columns'].extend(old_cols)

        def sort_by_due_date(i):
            return i['due_date']

        idx_forbid_to_changed = [i for i, v in enumerate(lines2) if
                                 v.get('unfoldable') or v.get('name').strip() == 'Total']
        range_idx_need_to_sort = []
        for i, v in enumerate(idx_forbid_to_changed):
            if i != len(idx_forbid_to_changed) - 1:
                if not idx_forbid_to_changed[i + 1] - 1 == v:
                    range_idx_need_to_sort.append([v + 1, idx_forbid_to_changed[i + 1]])

        for i in range_idx_need_to_sort:
            sorted_list = lines2[i[0]:i[1]]
            sorted_list.sort(key=sort_by_due_date, reverse=True)
            lines2[i[0]:i[1]] = sorted_list

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
