# -*- coding: utf-8 -*-
{
    'name': "B2B Address",

    'summary': "B2B Address",

    'description': "B2B Address",

    'author': "Next-pro",
    'website': "http://www.nextpro.pe",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'application': True,
    'version': '1.7',
    'images': [
    ],

    # any module necessary for this one to work correctly
    'depends': ['base', "sale", "nextconnector", "contacts", "website_sale_delivery", "delivery"],

    # always loaded
    'data': [
        # vistas de formulario/ listas
        'views/website_payment.xml',
        'views/res_partner_view.xml',
        'views/website_show_view.xml',
        'views/sale_order_view.xml',
        'views/delivery_carrier_view.xml',
        'views/dc_tarifa_despacho_view.xml',
        'views/res_city_view.xml',
        'views/res_city_district_view.xml',
        'views/shipping_agencies.xml',

        # templates
        'templates/b2b_address.xml',
        'templates/b2b_portal_my_details.xml',
        'templates/b2b_address_edit.xml',
        'templates/info_retira_cliente.xml',

        # data

        # seguridad
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': True
}
