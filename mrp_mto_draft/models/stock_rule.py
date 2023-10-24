# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo.tools import float_compare

from odoo import SUPERUSER_ID, _
from odoo import api, models
from odoo.addons.stock.models.stock_rule import ProcurementException


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_manufacture(self, procurements):
        """
        Override the method because of the set the MO's as Draft stage and stop create new MO if Draft MO Found
        """
        productions_values_by_company = defaultdict(list)
        errors = []
        for procurement, rule in procurements:
            if float_compare(procurement.product_qty, 0, precision_rounding=procurement.product_uom.rounding) <= 0:
                # If procurement contains negative quantity, don't create a MO that would be for a negative value.
                continue
            bom = rule._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)

            productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))

        if errors:
            raise ProcurementException(errors)

        for company_id, productions_values in productions_values_by_company.items():
            # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            procurement_groups = procurement.values.get('group_id')
            # Finding the Draft MO aif Found Draft MO than system will not create the Draft MO
            mrp_production_ids = set(
                procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids) | \
                                 set(procurement_groups.mrp_production_ids.ids)
            mrp_production_ids = list(mrp_production_ids)
            existing_productions = self.env['mrp.production'].browse(mrp_production_ids)
            draft_productions = existing_productions.filtered(lambda x: x.state == 'draft' and x.product_id == self._context.get('old_product_id'))
            if draft_productions:
                draft_productions.workorder_ids.unlink()
                draft_productions.product_id = procurement.product_id
                draft_productions._create_workorder()
            productions = draft_productions
            if not draft_productions:
                productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(
                    productions_values)
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
            if not draft_productions:
                productions._create_workorder()

            # Comment this line because when MO created from the SO that Time MO should be in Draft stage
            # productions.filtered(self._should_auto_confirm_procurement_mo).action_confirm()

            for production in productions:
                origin_production = production.move_dest_ids and production.move_dest_ids[
                    0].raw_material_production_id or False
                orderpoint = production.orderpoint_id
                if orderpoint and orderpoint.create_uid.id == SUPERUSER_ID and orderpoint.trigger == 'manual':
                    production.message_post(
                        body=_('This production order has been created from Replenishment Report.'),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note')
                elif orderpoint:
                    production.message_post_with_view(
                        'mail.message_origin_link',
                        values={'self': production, 'origin': orderpoint},
                        subtype_id=self.env.ref('mail.mt_note').id)
                elif origin_production:
                    production.message_post_with_view(
                        'mail.message_origin_link',
                        values={'self': production, 'origin': origin_production},
                        subtype_id=self.env.ref('mail.mt_note').id)
        return True
