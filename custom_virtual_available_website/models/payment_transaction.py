from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    _description = 'Payment Transaction'

    @api.model
    def create(self, vals):
        res =  super(PaymentTransaction, self).create(vals)
        products = res.sale_order_ids.order_line.mapped('product_id.product_template_id')
        _logger.info(f"""
        
        
        

        {products}

        
        
        """)
        ctx = products.self._context.get('payment_transation')
        _logger.info(f"""
        
        
        

        {ctx}

        
        
        """)
        return res
    