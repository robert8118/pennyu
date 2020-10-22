from odoo import api, fields, models


class MrpShift(models.Model):
    _name = 'mrp.shift'

    name = fields.Char('Nama')
    start_time = fields.Float('Mulai')
    end_time = fields.Float('Selesai')
    note = fields.Char()
    active = fields.Boolean('Aktif', default=True)

    @api.multi
    def name_get(self):
        res = []
        for x in self:
            start_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(x.start_time) * 60, 60))
            end_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(x.end_time) * 60, 60))
            res.append((x.id, '%s (%s - %s)' % (x.name, start_time_string, end_time_string)))
        return res
