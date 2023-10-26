# -*- coding: utf-8 -*-
from odoo import api, models, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _should_auto_confirm_procurement_mo(self, p):
        return False

    @api.model
    def _run_manufacture(self, procurements):
        """
        Override the method because of the set the MO's as Draft stage and stop create new MO if Draft MO Found
        """
        ctx = dict(self.env.context)
        if ctx.get('draft_production_id') and ctx.get('old_product_id'):
            draft_production = self.env['mrp.production'].search([('id', '=', ctx['draft_production_id'])])
            for procurement, rule in procurements:
                if draft_production:
                    draft_production.workorder_ids.unlink()
                    production_vals = {
                        'product_id': procurement.product_id,
                    }
                    if 'updated_order_qty' in ctx:
                        production_vals['product_qty'] = ctx.get('updated_order_qty', 0)
                    draft_production._update_mo_from_sale(production_vals)
            return True
        return super()._run_manufacture(procurements)

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        move_values = super()._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        ctx = dict(self.env.context)
        if values.get('sale_line_id') and ctx.get('updated_order_qty'):
            move_values['product_uom_qty'] = ctx['updated_order_qty']
        return move_values

    @api.model
    def _run_pull(self, procurements):
        """
            Override method to remove existing move when sale order line is update from confrim sale order
        """
        ctx = dict(self.env.context)
        StockMove = self.env['stock.move']
        if ctx.get('old_product_id'):
            for procurement, rule in procurements:
                if procurement.values and procurement.values.get('sale_line_id'):
                    # on update sale order line remove existing move
                    move = StockMove.search([('sale_line_id', '=', procurement.values['sale_line_id'])])
                    if move:
                        move._action_cancel()
                        move.sudo().unlink()
        return super()._run_pull(procurements)