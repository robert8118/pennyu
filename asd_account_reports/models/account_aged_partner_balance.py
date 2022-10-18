from odoo import api, fields, models


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = 'account.aged.partner'

    def get_columns_name(self, options):
        due_date_cols = {'name': 'Due Date', 'class': 'text', 'style': 'white-space:nowrap;'}
        inv_date_cols = {'name': 'Inv. Date', 'class': 'date', 'style': 'white-space:nowrap;'}
        source_cols = {'name': 'Source Document', 'class': 'text', 'style': 'white-space:nowrap;text-align:center;'}
        salesperson_cols = {'name': 'Salesperson', 'class': 'text', 'style': 'white-space:nowrap;text-align:center;'}

        columns = super(ReportAccountAgedPartner, self).get_columns_name(options)
        columns2 = columns[:]
        columns2.insert(1, inv_date_cols)
        columns2.insert(2, source_cols)
        columns2.insert(3, salesperson_cols)
        columns2.insert(4, due_date_cols)
        return columns2

    @api.model
    def get_lines(self, options, line_id=None):
        lines = super(ReportAccountAgedPartner, self).get_lines(options, line_id)

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
                # Add some columns data (Invoice Date and Source Document) if sml.invoice_id == True 
                if sml.invoice_id:
                    lines2[idx]['columns'] = [{'name': sml.invoice_id.date_invoice}, {'name': sml.invoice_id.origin}, {'name': sml.invoice_id.user_id.name}]
                # Add an empty column with the amount according to the empty data column
                else:
                    lines2[idx]['columns'] = [{'name': ''}, {'name': ''}, {'name': ''}]
                # Add Due Date column data
                lines2[idx]['columns'].extend([{'name': sml.date_maturity}])
                lines2[idx]['columns'].extend(old_cols)
            else:
                old_cols = lines[idx]['columns']
                # Add an empty column with the amount according to the empty data column
                lines2[idx]['columns'] = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
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
