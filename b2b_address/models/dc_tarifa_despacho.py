from odoo import fields, models


class TarifaDespacho(models.Model):

    _name = 'dc.tarifa.despacho'
    _description = 'DC Tarifa de despacho'

    state_id = fields.Many2one('res.country.state', string='Departamento', domain="[('country_id', '=', 'PE')]")
    city_id = fields.Many2one('res.city', string='Provincia', domain="[('state_id', '=', state_id)]")
    district_id = fields.Many2one('l10n_pe.res.city.district', string='Distrito', domain="[('city_id', '=', city_id)]")
    district_code = fields.Char(related='district_id.code', string='Codigo de distrito', readonly=False)

    warehouse_id = fields.Many2many('stock.warehouse', string="Bodega origen")
    precio_base_kg = fields.Float('Precio base 1 Kg')
    precio_kg_adicional = fields.Float('Precio Kg adicional')

    precio_base_kg_valorado = fields.Float('Precio base 1 Kg Valorado')
    precio_kg_adicional_valorado = fields.Float('Precio Kg adicional Valorado')
    carrier_id = fields.Many2one('delivery.carrier', 'Metodo de envio')

    
    


    ambito = fields.Selection(string="Ambito",
        selection=[
            ("periferico","PERIFERICO")
            ,("urbano","URBANO")
            ,("zona_alejada","ZONA ALEJADA")
        ]
        , default="periferico"
    )

    ubigeo = fields.Char('Ubigeo')

    free_ship_amount_order = fields.Float('Monto para envio gratis')

    lead_time = fields.Float('Lead Time')
    