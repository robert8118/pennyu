from odoo import api, fields, models, _
from datetime import datetime, timedelta

class report_account_general_ledger(models.AbstractModel):
    _inherit = 'account.general.ledger'

    def view_all_journal_items(self, options, params):
        ctx = self.set_context(options)
        if params.get('id'):
            account_id = int(params.get('id').split('_')[1])
            account_id = self.env['account.account'].browse(account_id)
            ctx['account_ids'] = account_id
            self = self.with_context(ctx)
            company_id = self.env.user.company_id
            dt_from = options['date'].get('date_from')
            grouped_accounts = self.with_context(date_from_aml=dt_from, date_from=dt_from and company_id.compute_fiscalyear_dates(datetime.strptime(dt_from,"%Y-%m-%d"))['date_from'] or None).group_by_account_id(options, False)
            initial_date = datetime.strptime(dt_from, '%Y-%m-%d') - timedelta(days=1)
            initial_date = initial_date.strftime('%Y-%m-%d')
            new_options = options.copy()
            new_options['date'] = options['date'].copy()
            new_options['date'].update({
                'date_from': initial_date,
                'date_to': initial_date,
            })
            initial_move_lines = self.with_context(date_from_aml=initial_date, date_from=initial_date and company_id.compute_fiscalyear_dates(datetime.strptime(initial_date, "%Y-%m-%d"))['date_from'] or None).group_by_account_id(new_options, False)
            initial_move_lines = initial_move_lines[account_id]['lines']
            if initial_move_lines :
                initial_move_lines = initial_move_lines.filtered(lambda l: l.date < dt_from)
            if initial_move_lines :
                initial_move_lines = sorted(initial_move_lines, key=lambda a: (a.move_id.date, a.id))
                initial_line_id = initial_move_lines[-1].id
            else :
                initial_line_id = False
            ctx['initial_balance'] = grouped_accounts[account_id]['initial_bal']['balance']
            ctx['initial_line_id'] = initial_line_id
        ctx.update({
            'from_report': True
        })
        self = self.with_context(ctx)
        res = super(report_account_general_ledger, self).view_all_journal_items(options, params)
        return res
