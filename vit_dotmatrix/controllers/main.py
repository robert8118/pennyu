import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET

import logging
import re

import werkzeug.utils
import werkzeug.wrappers

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import odoo
from odoo import  http
from odoo.http import request

logger = logging.getLogger(__name__)

class BaseWebsite(http.Controller):

    @http.route('/myweb/index', type='http', auth="public", website=True)
    def index(self, **kw):
        return "index"