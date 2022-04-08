from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    _description = 'Payment Transaction'

    @api.model
    def create(self, vals):
        res =  super(PaymentTransaction, self).create(vals)
        products = res.sale_order_ids.order_line.mapped('product_id.product_tmpl_id')
        _logger.info(f"""
        
        
        
        PRODUCT
        {products}

        
        
        """)
        ctx = products._context.get('payment_transation')
        _logger.info(f"""
        
        
        
        CONTEXT 0
        {ctx}

        
        
        """)
        products.with_context({'payment_transation': True})
        ctx = products._context.get('payment_transation', False)
        _logger.info(f"""
        
        
        
        CONTEXT 1
        {products._context}
        {ctx}

        
        
        """)
        return res
    