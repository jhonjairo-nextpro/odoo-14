# -*- encoding: utf-8 -*-
from odoo import fields, models, api , _


class ClientProvider(models.Model):
    _name = 'client.provider'
    _description = 'client provider'

    name = fields.Char('Cliente/Proveedor')
    


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_provider = fields.Many2one('client.provider', string="Cliente/ Proveedor")
    code_client_provider = fields.Char('Codigo')

    @api.model
    def create(self, vals):
        Partner = super(ResPartner, self).create(vals)
        if Partner and Partner.client_provider and not Partner.code_client_provider:
            Partner.code_client_provider = Partner.client_provider.name + Partner._get_next_code_client_provider()
        return Partner

    def write(self, values):
        Partner = super(ResPartner, self).write(values)
        if self and self.client_provider and not self.code_client_provider:
            self.code_client_provider = self.client_provider.name + self._get_next_code_client_provider()
        return Partner

    '''
    @api.onchange('client_provider')
    def _onchange_client_provider(self):
        if self.client_provider:
            self.code_client_provider = self.client_provider.name + self._get_next_code_client_provider()
        else:
            self.code_client_provider = False
    '''

    def _get_next_code_client_provider(self):
        return self.env['ir.sequence'].next_by_code('code.client.provider')
