from odoo import fields, models


class LogsSRI(models.Model):
    _name = "shipping.agencies"

    name = fields.Char(string="Nombre")
    code = fields.Char(string="Código")
