from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    nxt_id_erp = fields.Char('Código ERP')