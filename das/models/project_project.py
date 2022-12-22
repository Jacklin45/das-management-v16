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


class ProjectProject(models.Model):
    _inherit = 'project.project'

    account_ids = fields.One2many('das.account', 'project_id', string="Accounts")
    account_count = fields.Integer(string="Account", compute='_compute_account_count')

    def get_project_account(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'das.account',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
            'view_mode': 'tree',
            'target': 'current',
            'name': 'Accounts',
            'views': [
                (self.env.ref('das.view_das_planning_account_tree').id, 'tree'),
                (self.env.ref('das.view_das_planning_account_form').id, 'form')
            ]
        }

    @api.depends('account_ids')
    def _compute_account_count(self):
        for project in self:
            project.account_count = len(project.account_ids)
