from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    _description = 'Payment Transaction'

    @api.model
    def create(self, vals):
        res =  super(PaymentTransaction, self).create(vals)
        for order in res.sale_order_ids:
            _logger.info(f"""


            ORDER
            {order.name}

            
            """)
        return res
    