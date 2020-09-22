from odoo import models
import math

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def get_company(self):
        return {
            'name': self.company_id.name or '-',
            'street': self.company_id.street or '-',
            'city': self.company_id.city or '-',
            'country': self.company_id.country_id.name or '-',
            'phone': self.company_id.phone or '-',
            'vat': self.company_id.vat or '-'
        }

    def get_partner(self):
        return {
            'display_name': self.partner_id.display_name or '-',
            'street': self.partner_id.street or '-',
            'street2': self.partner_id.street2 or '-',
            'blok': self.partner_id.blok or '-',
            'nomor': self.partner_id.nomor or '-',
            'rt': self.partner_id.rt or '-',
            'rw': self.partner_id.rw or '-',
            'kelurahan': self.partner_id.kelurahan_id.name or '-',
            'kecamatan': self.partner_id.kecamatan_id.name or '-',
            'kabupaten': self.partner_id.kabupaten_id.name or '-',
            'city': self.partner_id.city or '-',
            'state': self.partner_id.state_id.name or '-',
            'zip': self.partner_id.zip or '-',
            'country': self.partner_id.country_id.name or ' ',
            'vat': self.partner_id.vat or ' ',
            'is_npwp_pribadi': self.partner_id.is_npwp_pribadi or ' ',
            'nama_npwp_pribadi': self.partner_id.nama_npwp_pribadi or ' ',
            'alamat_npwp_pribadi': self.partner_id.alamat_npwp_pribadi or ' ',
            'npwp': self.partner_id.npwp or ' ',
        }

    def get_shipping(self):
        return {
            'display_name': self.partner_id.display_name or '-',
            'street': self.partner_id.street or '-',
            'street2': self.partner_id.street2 or '-',
            'blok': self.partner_id.blok or '-',
            'nomor': self.partner_id.nomor or '-',
            'rt': self.partner_id.rt or '-',
            'rw': self.partner_id.rw or '-',
            'kelurahan': self.partner_id.kelurahan_id.name or '-',
            'kecamatan': self.partner_id.kecamatan_id.name or '-',
            'kabupaten': self.partner_id.kabupaten_id.name or '-',
            'city': self.partner_id.city or '-',
            'state': self.partner_id.state_id.name or '-',
            'zip': self.partner_id.zip or '-',
            'country': self.partner_id.country_id.name or '-',
            'vat': self.partner_id.vat or '-',
            'npwp': self.partner_id.npwp or ' ',
        }


    def get_bank(self):
        bank = self.env['account.journal'].search([('company_id', '=', self.company_id.id),('display_on_footer', '=', True)])
        list_b = ''
        for b in bank:
            if b == bank[-1]:
                list_b += b.bank_id.name + ' ' + b.bank_acc_number
            else:
                list_b += b.bank_id.name + ' ' + b.bank_acc_number + ' '
        return list_b

    def get_data(self):
        line_inv = []
        i = 1
        length_p = 50
        length_u = 10
        for line in self.invoice_line_ids:
            product_1 = line.product_id.name.replace("'",'')
            product_2 = product_1.replace('"','')
            product_name1 = line.name.replace("'",'')
            space_length_name = (length_p - len(product_name1)) + len(product_name1)
            space_length_p = (length_p - len(product_1)) + len(product_1)
            space_length_u = (length_u - len(line.uom_id.name)) + len(line.uom_id.name)
            line_inv.append({
                'no': i,
                'product': product_1[:length_p],
                'product_name': product_name1[18:],
                'qty': line.quantity,
                'prod_name': line.name,
                'uom': line.uom_id.name,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_unit - line.display_discount,
                'discount': line.discount,
                'price_total': line.price_total,
                'space_length_p': space_length_p,
                'space_length_u': space_length_u
            })
            i += 1
        return line_inv

    def get_datas(self):
        """function for split dotmatrix for maximum 4 lines"""
        line_inv = []
        i = 1
        j = 1
        length_p = 50
        length_u = 10
        split = []
        count_lines = float(len(self.invoice_line_ids))
        count_lines = int(math.ceil(count_lines/8))
        index = 1
        # set value of invoice line in list
        for line in self.invoice_line_ids:
            product_1 = line.product_id.name.replace("'",'')
            product_2 = product_1.replace('"','')
            product_name1 = line.name.replace("'",'')
            product_name2 = product_name1.replace('"','')
            space_length_name = (length_p - len(product_name1)) + len(product_name1)
            space_length_p = (length_p - len(product_1)) + len(product_1)
            space_length_u = (length_u - len(line.uom_id.name)) + len(line.uom_id.name)
            line_inv.append({
                'no': i,
                'product': product_2[:length_p],
                'product_name': product_name1[18:],
                'qty': line.quantity,
                'uom': line.uom_id.name,
                'prod_name': line.name,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'discount': line.discount,
                'price_total': line.price_total,
                'space_length_p': space_length_p,
                'space_length_u': space_length_u
            })
            i += 1
        # condition for spliting lines
        if line_inv:
            z = []
            if not split:
                # set the 4 lines in page 1
                z.append(line_inv[0])
                z.append(line_inv[1])
                z.append(line_inv[2])
                z.append(line_inv[3])
                z.append(line_inv[4])
                z.append(line_inv[5])
                z.append(line_inv[6])
                z.append(line_inv[7])
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                split.append({'row': j, 'line': z, 'count': count_lines})
                total_line = 0
            if split:
                # set the rest lines in other page with maximum 4 lines
                for sp in split:
                    if count_lines != sp['row']:
                        line = []
                        for vals in line_inv:
                            if index == 9:
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                index = 1
                                total_line = 0
                                break
                            total_line += vals['price_total']
                            line.append(vals)
                            index += 1
                        j += 1
                        split.append({'row': j, 'line': line, 'count': count_lines})
        return split

    def terbilang_with_tag(self):
        return '#'+self.total_terbilang(self.amount_total)+'#'
