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


class DasAccount(models.Model):
    _name = 'das.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "DAS Planning Account"
    _rec_name = 'reference'

    reference = fields.Char(string="Reference", compute='_compute_reference', store=True, readonly=True)
    description = fields.Text(string="Description")
    responsible_id = fields.Many2one('hr.employee', string="Responsible", tracking=True)
    start_date = fields.Date(string="Start date", tracking=True)
    end_date = fields.Date(string="End date", tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    reference_id = fields.Many2one('das.account.reference', string="Account reference")
    category_id = fields.Many2one(related='reference_id.category_id', string='Category', store=True)
    type_id = fields.Many2one(related='reference_id.type_id', string='Type', store=True)
    techno = fields.Char(string="TECHNO", tracking=True)
    project_id = fields.Many2one('project.project', string="Project", required=True, tracking=True)
    key = fields.Char(related='project_id.key', store=True)
    intercontrat = fields.Boolean(string='Intercontrat', default=True, compute='_compute_intercontrat')

    planning_ids = fields.One2many('das.planning', 'account_id', string="Plannings")
    planning_count = fields.Integer(string="Planning count", compute='_compute_count_planning')
    resource_count = fields.Integer(string="Resource count", compute='_compute_count_resource')

    @api.depends('project_id')
    def _compute_intercontrat(self):
        for rec in self:
            if rec.type not in ['FAC', 'MGT', 'RH']:
                rec.intercontrat = True

    @api.depends('key', 'project_id', 'reference_id')
    def _compute_reference(self):
        for rec in self:
            if rec.reference_id:
                if rec.reference_id.reference == "no BC":
                    rec.reference = "[" + str(rec.key) + "] " + str(rec.project_id.name)
                else:
                    rec.reference = "[" + str(rec.key) + "] " + str(rec.project_id.name) + " [" + str(
                        rec.reference_id.reference) + "]"
            else:
                rec.reference = "[" + str(rec.key) + "] " + str(rec.project_id.name)

    @api.onchange('reference_id')
    def set_order_date(self):
        for rec in self:
            if rec.reference_id:
                rec.start_date = rec.reference_id.start_date
                rec.end_date = rec.reference_id.end_date
            else:
                rec.start_date = None
                rec.end_date = None

    @api.depends('planning_ids')
    def _compute_count_planning(self):
        for account in self:
            account.planning_count = len(account.planning_ids)

    def get_account_planning(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'das.planning',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id},
            'view_mode': 'gantt,tree',
            'target': 'current',
            'name': 'Plannings',
            'views': [
                (self.env.ref('das.view_das_planning_planning_gantt').id, 'gantt'),
                (self.env.ref('das.view_das_planning_planning_tree').id, 'tree')
            ]
        }
