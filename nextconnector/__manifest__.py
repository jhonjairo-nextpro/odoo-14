# -*- coding: utf-8 -*-
{
    'name': "Next-Connector",

    'summary': "Connect CRM With ERP",

    'description': "Connect CRM With ERP",

    'author': "Next-pro",
    'website': "http://www.nextpro.pe",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'application': True,
    'version': '1.2',
    'images': [
        'static/description/logo_empresa.jpg',
    ],

    # any module necessary for this one to work correctly
    'depends': ['base',"sale","base_automation","contacts"],

    # always loaded
    'data': [
        # vistas de formulario/ listas
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/popup_message_wizard.xml',
        'views/sales_rep_view.xml',
        
        
        'views/nextconnector_menu_import.xml',
        'views/nextconnector_menu_master_data.xml',
        'views/account_payment_term_views.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/template_date_view.xml',
        'views/product_template_view.xml',
        'views/account_tax_view.xml', 
        'views/account_journal_view.xml',   
        'views/template_query_view.xml',
        'views/template_query_view.xml',
        'views/res_config_settings.xml',
        'views/process_queue_view.xml',
        'views/res_users_view.xml',
        'views/res_partner_category_view.xml',
        'views/res_company_view.xml',
        

        #data
        'data/nextconnector_template_data.xml',
        'data/nextconnector_template_query.xml',
        'data/nextconnector_template_res_partner_balance_query.xml',
        'data/nextconnector_template_data_pending_invoice.xml',
        'data/nextconnector_ir_cron.xml',
        'data/nextconnector_automated_actions.xml',
        

        # seguridad
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': True
}