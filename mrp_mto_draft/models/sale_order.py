# -*- coding: utf-8 -*-
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        self.picking_ids.filtered(lambda x: x.state == 'waiting').move_lines.write({'state': 'draft'})
        return res

    def lock_so(self):
        """Lock Documents Function."""
        self.action_done()
        procurement_groups = self.env['procurement.group'].search([('sale_id', 'in', self.ids)])
        mrp_production_ids = set(
            procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids) | \
                            set(procurement_groups.mrp_production_ids.ids)
        mrp_production_ids = list(mrp_production_ids)
        productions = self.env['mrp.production'].search([('id', 'in', mrp_production_ids), ('state', '=', 'draft')])
        productions.action_confirm()
        self.picking_ids.filtered(lambda x: x.state == 'draft').action_confirm()
        for line in self.order_line:
            line.product_updatable = False


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_protected_fields(self):
        """Remove 'name', 'tax' from protected fields."""
        fields = super()._get_protected_fields()
        exclude_fields = ['name', 'tax_id']
        fields = [item for item in fields if item not in exclude_fields]
        return fields

    @api.depends('product_id', 'order_id.state', 'qty_invoiced', 'qty_delivered')
    def _compute_product_updatable(self):
        super()._compute_product_updatable()
        for line in self:
            line.product_updatable = True

    def write(self, vals):
        old_product_id = self.product_id.id
        procurement_groups = self.env['procurement.group'].search([('sale_id', '=', self.order_id.id)])
        mrp_production_ids = set(
            procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids) | \
                            set(procurement_groups.mrp_production_ids.ids)
        mrp_production_ids = list(mrp_production_ids)
        production = self.env['mrp.production'].search([('id', 'in', mrp_production_ids), ('state', '=', 'draft'), ('product_id', '=', old_product_id)], limit=1)
        ctx = {'old_product_id': old_product_id, 'draft_production_id': production.id}
        if 'product_uom_qty' in vals:
            ctx['updated_order_qty'] = vals.get('product_uom_qty', 0)
        res = super(SaleOrderLine, self.with_context(ctx)).write(vals)
        if production:
            self.move_ids.write({'created_production_id': production.id})
            production._onchange_move_finished_product()
        return res
