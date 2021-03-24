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
