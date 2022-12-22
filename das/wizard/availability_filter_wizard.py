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

from datetime import timedelta

from odoo import models, fields


class AvailabilityFilter(models.TransientModel):
    _name = 'availability.filter.wizard'
    _description = "Availability Filter Wizard"

    start_date = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    end_date = fields.Date(string="End Date", required=True, default=fields.Date.today)
    job_ids = fields.Many2many('hr.job', string="Job")

    def get_available_resource(self):
        self.env['res.availability'].sudo().search([]).unlink()
        resources = self.env['hr.employee'].search([])
        for resource in resources:
            availability = {}
            resource_plannings = self.env['das.planning'].search([('resource_id', '=', resource.id)])
            planning_start_hours = resource_plannings.filtered(
                lambda p: p.start_date <= self.start_date <= p.end_date).mapped(
                'daily_hours')
            availability['resource_id'] = resource.id
            availability['start_date'] = self.start_date
            availability['hour'] = 8 - sum(planning_start_hours)

            date = self.start_date
            while date <= self.end_date:
                planning_days_hours = resource_plannings.filtered(lambda p: p.start_date <= date <= p.end_date).mapped(
                    'daily_hours')
                available_hour = 8 - sum(planning_days_hours)
                if available_hour != availability['hour']:
                    availability['end_date'] = date - timedelta(days=1)
                    self.env['res.availability'].sudo().create(availability)
                    availability['start_date'] = date
                    availability['hour'] = available_hour
                date += timedelta(days=1)

            if availability['hour'] != 0:
                availability['end_date'] = self.end_date
                self.env['res.availability'].sudo().create(availability)

        # Delete non available resource
        self.env['res.availability'].sudo().search([('hour', '=', 0)]).unlink()

        # Check resource Job
        domain = []
        if self.job_ids:
            domain.append(('resource_id.job_id', '=', self.job_ids.mapped('name')))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.availability',
            'domain': domain,
            'context': {'search_default_group_by_resource': 1},
            'view_mode': 'tree,form',
            'target': 'current',
            'name': 'Availability',
            'views': [
                (self.env.ref('das.view_res_availability_gantt').id, 'gantt'),
                (self.env.ref('das.view_res_availability_tree').id, 'tree'),
                (self.env.ref('das.view_res_availability_form').id, 'form')
            ]
        }
