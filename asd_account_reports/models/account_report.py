# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
from odoo import models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from datetime import timedelta, datetime, date

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'
    
    def apply_date_filter(self, options):
        if not options.get('date'):
            return options
        options_filter = options['date'].get('filter')
        if not options_filter:
            return options
        today = date.today()
        dt_from = options['date'].get('date_from') is not None and today or False
        if options_filter == 'custom':
            dt_from = options['date'].get('date_from', False)
            dt_to = options['date'].get('date_to', False) or options['date'].get('date', False)
            options['date']['string'] = self.format_date(dt_to, dt_from, options)
            return options
        if options_filter == 'today':
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(datetime.now())
            dt_from = dt_from and company_fiscalyear_dates['date_from'] or False
            dt_to = today
        elif options_filter == 'this_month':
            dt_from = dt_from and today.replace(day=1) or False
            dt_to = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            # Handling issues with different year filters
            # if dt_from and dt_from.year != dt_to.year:
            #     dt_to_temp = dt_to.replace(year=dt_from.year)
            #     dt_to = dt_to_temp
        elif options_filter == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            dt_to = (today.replace(month=quarter * 3, day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            dt_from = dt_from and dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year) or False
        elif options_filter == 'this_year':
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(datetime.now())
            dt_from = dt_from and company_fiscalyear_dates['date_from'] or False
            dt_to = company_fiscalyear_dates['date_to']
        elif options_filter == 'last_month':
            dt_to = today.replace(day=1) - timedelta(days=1)
            dt_from = dt_from and dt_to.replace(day=1) or False
        elif options_filter == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            quarter = quarter - 1 if quarter > 1 else 4
            dt_to = (today.replace(month=quarter * 3, day=1, year=today.year if quarter != 4 else today.year - 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            dt_from = dt_from and dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year) or False
        elif options_filter == 'last_year':
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(datetime.now().replace(year=today.year - 1))
            dt_from = dt_from and company_fiscalyear_dates['date_from'] or False
            dt_to = company_fiscalyear_dates['date_to']
        if dt_from:
            options['date']['date_from'] = dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
            options['date']['date_to'] = dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            options['date']['date'] = dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # Handling the issue of incorrect year labels
        if options_filter in ["this_month"] and dt_from.year != dt_to.year:
            dt_to_temp = dt_to.replace(year=dt_from.year)
            dt_to = dt_to_temp
        options['date']['string'] = self.format_date(dt_to, dt_from, options)
        return options