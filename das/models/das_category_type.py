# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2022 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


class DasCategoryType(models.Model):
    _name = 'das.category.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "DAS Category Type"
    _rec_name = 'type'

    type = fields.Char(string="Type", required=True, tracking=True)
    is_intercontrat = fields.Boolean(string="Is intercontrat", default=False, tracking=True)
    is_no_counting = fields.Boolean(string="Is no counting")
    description = fields.Text(string="Description", tracking=True)

    # For smart button
    category_ids = fields.One2many('das.category', 'type_id', string="Category")
    category_count = fields.Integer(string="Account count", compute='_compute_category_count')

    @api.depends('category_ids')
    def _compute_category_count(self):
        for category in self:
            category.category_count = len(category.category_ids)

    def get_category_type(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'das.category',
            'domain': [('type_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
            'name': 'Category',
            'views': [
                (self.env.ref('das.view_das_planning_category_type_tree').id, 'tree'),
                (self.env.ref('das.view_das_planning_category_type_form').id, 'form')
            ]
        }
