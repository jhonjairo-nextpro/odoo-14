from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.stock_move_ids.product_qty',
        'product_variant_ids.stock_move_ids.state',
    )
    @api.depends_context('company', 'location', 'warehouse')
    def _compute_quantities(self):
        _logger.info("""
        
        
        {self.env.context}
        
        
        """)
        super(ProductTemplate, self)._compute_quantities()
        # res = self._compute_quantities_dict()
        # for template in self:
        #     template.qty_available = res[template.id]['qty_available']
        #     template.virtual_available = res[template.id]['virtual_available']
        #     template.incoming_qty = res[template.id]['incoming_qty']
        #     template.outgoing_qty = res[template.id]['outgoing_qty']
