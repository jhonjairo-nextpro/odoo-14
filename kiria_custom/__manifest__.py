# -*- coding: utf-8 -*-
{
    'name': 'Kiria Custom',
    'version': '14.0.2',
    'author': 'Kelvis Pernia / Andy Quijada',
    'license': 'AGPL-3',
    'category': 'Custom',
    'description': """
Crear código de cliente y proveedor Automaticamente / Crear automaticamente codigo producto referencia interna 
Generar estructura del codigo del lote / Generar estructura de lote en Fabricacion
============
""",
    'depends': [
        'stock',
        'base',
        'contacts',
        'l10n_latam_base',
        'product',
        'mrp',
        'purchase',
        'sale',
        'product_expiry'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data_default.xml',
        'views/res_partner.xml',
        'views/product_views.xml',
        'views/client_provider_views.xml',
        'data/sequence_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
