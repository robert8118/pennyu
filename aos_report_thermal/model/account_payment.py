from odoo import models, api, fields
from datetime import datetime, date, time, timedelta
import math
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    def getToday(self):
        dateToday = datetime.datetime.now()
        dateToday.strftime("%d/%m/%y %H:%M:%S")
        return dateToday

# 
#     @api.multi
#     def generate_report(self):
#          x = self._.get('active_ids',[])
#          #payslip_ids this will be your selected payslip ids in list view.
#          print(x)
#          return self.env.ref('aos_report_thermal.action_report_payment_admin').report_action(self, config=False)