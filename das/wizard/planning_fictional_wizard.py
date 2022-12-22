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

from dateutil import rrule
from dateutil.rrule import MONTHLY

from odoo import models, fields, api


class PlanningFictionalWizard(models.TransientModel):
    _name = 'planning.fictional.wizard'
    _description = "Generate Planning fictional on Wizard"

    batch_id = fields.Many2one('das.fictional.batch', string='Batch name')
    start_date = fields.Date(string='Start date', related='batch_id.start_date', readonly=True)
    end_date = fields.Date(string='End date', related='batch_id.end_date', readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", required=True)
    resource_ids = fields.Many2many('hr.employee', string="Job", required=True)

    @api.onchange("department_id")
    def _set_resource_ids_domains(self):
        """Filter resource based on department """
        if self.department_id:
            return {
                'domain': {
                    'resource_ids': [('department_id', '=', self.department_id.id)],
                }
            }

    @api.depends('date', 'resource_ids', 'planning_id')
    def generate_fictional_planning(self):
        """
        Generate monthly fictional planning for all resources
        :rtype: object
        """
        planing_date_obj = self.env['das.planning.date']

        # Get all days of the current period except weekend
        dates = list(rrule.rrule(MONTHLY,
                                     byweekday=[0, 1, 2, 3, 4],
                                     dtstart=self.start_date,
                                     until=self.end_date))

        account_id = self.env.ref('das.das_fictional_account')
        for res in self.resource_ids:
            for d in dates:
                planning_ids = planing_date_obj.search(
                    [('resource_id', '=', res.id), ('date', '=', d.date()), ('account_id', '=', account_id.id)])
                if not planning_ids:
                    total_daily_hours = sum(self.env['das.planning.date'].search(
                        [('resource_id', '=', res.id), ('date', '=', d.date())]).mapped('daily_hours'))
                    self.env['das.planning'].sudo().create({
                        'resource_id': res.id,
                        'account_id': account_id.id,
                        'daily_hours': 8 - total_daily_hours,
                        'start_date': d.date(), 'end_date': d.date()
                    })
