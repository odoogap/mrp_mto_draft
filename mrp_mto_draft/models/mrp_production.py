from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_from_so_configuration_product = fields.Boolean(string="From SO Configuration Product",
                                                    compute='_compute_from_so_congiguration_product')

    def _compute_from_so_congiguration_product(self):
        for mo in self:
            is_from_so_configuration_product = False
            if mo.sale_order_count and mo.product_id.product_add_mode == 'configurator':
                is_from_so_configuration_product = True
            mo.is_from_so_configuration_product = is_from_so_configuration_product

    def _update_mo_from_sale(self, vals):
        if 'product_qty' in vals and not vals.get('product_qty', 0):
            self.action_cancel()
        else:
            self.write(vals)
            self._onchange_product_id()
            self._onchange_product_qty()
            self.move_raw_ids = [(5,)]
            self._onchange_move_raw()
            self._create_workorder()