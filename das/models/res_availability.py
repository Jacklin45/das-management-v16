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

from odoo import models, fields


class ResAvailability(models.Model):
    _name = 'res.availability'
    _description = "Resource Availability"

    start_date = fields.Date(string="Start date", readonly=True)
    end_date = fields.Date(string="End date", readonly=True)
    hour = fields.Integer(string="Hour", readonly=True)
    planning_id = fields.Many2one('das.planning', string="Planning", readonly=True)

    resource_id = fields.Many2one('hr.employee', string="Resource", readonly=True)
    department_id = fields.Many2one('hr.department', related='resource_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', related='resource_id.job_id', store=True)
    type_id = fields.Many2one(related='planning_id.account_id.type_id', string="Type")

    def planning_available_resource(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'das.planning',
            'context': {
                'default_resource_id': self.resource_id.id,
                'default_start_date': self.start_date,
                'default_end_date': self.end_date,
                'default_daily_hours': self.hour
            },
            'view_mode': 'form',
            'target': 'current',
            'name': 'Resource planning',
            'views': [
                (self.env.ref('das.view_das_planning_planning_form').id, 'form')
            ]
        }

    def name_get(self):
        result = []
        for record in self:
            name = str(record.hour) + " h/j"
            result.append((record.id, name))
        return result
