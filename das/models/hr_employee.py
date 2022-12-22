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


class HrResource(models.Model):
    _inherit = 'hr.employee'

    planning_ids = fields.One2many('das.planning', inverse_name='resource_id', string="Plannings")
    planning_count = fields.Integer(string="Planning count", compute='_compute_count_planning')

    @api.depends('planning_ids')
    def _compute_count_planning(self):
        for resource in self:
            resource.planning_count = len(resource.planning_ids)

    def get_resource_planning(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'das.planning',
            'domain': [('resource_id', '=', self.id)],
            'context': {'default_resource_id': self.id},
            'view_mode': 'gantt,tree',
            'target': 'current',
            'name': 'Plannings',
            'views': [
                (self.env.ref('das.view_das_planning_planning_gantt').id, 'gantt'),
                (self.env.ref('das.view_das_planning_planning_tree').id, 'tree')
            ]
        }
