from odoo import api, fields, models, _
from datetime import datetime

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
            ctx['initial_balance'] = grouped_accounts[account_id]['initial_bal']['balance']
        ctx.update({
            'from_report': True
        })
        self = self.with_context(ctx)
        res = super(report_account_general_ledger, self).view_all_journal_items(options, params)
        return res
