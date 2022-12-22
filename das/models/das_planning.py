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

from datetime import datetime, timedelta

from odoo import models, fields, api, _

NB_HOURS_PER_DAY = 8


class DasPlanning(models.Model):
    _name = 'das.planning'
    _description = "DAS Planning"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'account_label'

    resource_id = fields.Many2one('hr.employee', string="Resource", required=True, tracking=True, index=True)
    resource_id_active = fields.Boolean('hr.employee', related='resource_id.active',
                                        store=True)
    resource_departure_date = fields.Date(string="Departure date", related='resource_id.departure_date')
    resource_departure_reason_id = fields.Many2one(string="Departure reason", related='resource_id.departure_reason_id')

    account_id = fields.Many2one('das.account', string="Account", required=True, tracking=True, index=True)
    start_date = fields.Date(string="Start date", default=fields.Date.today, required=True, tracking=True)
    end_date = fields.Date(string="End date", default=fields.Date.today, required=True, tracking=True)
    date_delta = fields.Integer(string="Number of days beetwen two dates", compute='_compute_date_delta', store=True)
    daily_hours = fields.Integer(string="Daily hours", default=8, tracking=True)
    total_hours = fields.Integer(string="Total hours", compute='_compute_total_hours', store=True, readonly=True)
    account_label = fields.Char(string="Account label", compute='_compute_account_label')
    active = fields.Boolean(string="Active", default=True, tracking=True)

    department_id = fields.Many2one('hr.department', related='resource_id.department_id', store=True)
    type_id = fields.Many2one(related='account_id.type_id', string="Type", store=True)
    job = fields.Char(related='resource_id.job_id.name', string="Job", store=True)
    resource_reference = fields.Char(related='resource_id.reference', string="Resource reference", store=True)
    color = fields.Integer(related='account_id.category_id.color', store=True)
    planning_date = fields.One2many('das.planning.date', inverse_name='planning_id', string="Date Planning")

    project_id = fields.Many2one('project.project', string='Project', related='account_id.project_id', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', tracking=True)

    globals_leaves_ids = fields.One2many(string="Global leave of current month",
                                         related='resource_id.resource_calendar_id.global_leave_ids')
    is_no_counting = fields.Boolean(string="Is no counting", related='account_id.type_id.is_no_counting', readonly=True)

    @api.onchange("project_id")
    def _set_project_domains(self):
        """Filter task and account based on project """
        if self.project_id:
            return {
                'domain': {
                    'task_id': [('project_id', '=', self.project_id.id)],
                    'account_id': [('project_id', '=', self.project_id.id)]
                }
            }

    @api.depends('resource_id', 'daily_hours', 'account_id')
    def _compute_account_label(self):
        """
        Add daily hours in account reference to show in planning Gantt view
        :rtype: object
        """
        for rec in self:
            rec.account_label = _("%s h/d %s") % (rec.daily_hours, rec.account_id.key)

    @api.depends('daily_hours', 'start_date', 'end_date')
    def _compute_total_hours(self):
        for rec in self:
            if rec.start_date:
                day = rec.start_date
                days_counter = 0
                while day <= rec.end_date:
                    if day.weekday() < 5:
                        days_counter += 1
                    day += timedelta(days=1)
                rec.total_hours = rec.daily_hours * days_counter

    @api.depends('start_date', 'end_date')
    def _compute_date_delta(self):
        for planning in self:
            planning.date_delta = (planning.end_date - planning.start_date).days + 1

    @api.onchange('daily_hours', 'account_id', 'account_id.type_id.is_no_counting')
    def _check_daily_hours(self):
        """Check immediately (onchange) a valid daily working hours"""
        for planning in self:
            if self.account_id and not self.account_id.type_id.is_no_counting and not 0 <= planning.daily_hours <= NB_HOURS_PER_DAY:
                planning.daily_hours = NB_HOURS_PER_DAY
                return {'warning': {
                    'title': _('Warning'),
                    'message': _("Sorry, Daily working hours is between 0 to 8 !"),
                }}

    @api.onchange('resource_id', 'account_id', 'account_id.type_id.is_no_counting', 'start_date', 'end_date',
                  'daily_hours')
    def _check_planning(self):
        """
        Check planning
        :rtype: object
        """
        date = self.start_date
        if date:
            total_daily_hours = []
            fictive_total_daily_hours = []
            result = NB_HOURS_PER_DAY
            while date <= self.end_date:
                plainning_ids = self.env['das.planning'].search(
                    [('resource_id', '=', self.resource_id.id)]).filtered(
                    lambda p: p.start_date <= self.start_date <= p.end_date and p.account_id.type_id.id != self.env.ref(
                        'das.das_fictional_type').id)
                fictive_planning_ids = self.env['das.planning'].search(
                    [('resource_id', '=', self.resource_id.id), ('id', '!=', self._origin.id)]).filtered(
                    lambda p: p.start_date <= self.start_date <= p.end_date and p.account_id.type_id.id == self.env.ref(
                        'das.das_fictional_type').id)
                total_daily_hours.append(sum(plainning_ids.mapped('daily_hours')))
                fictive_total_daily_hours.append(sum(fictive_planning_ids.mapped('daily_hours')))
                date += timedelta(days=1)

            if fictive_planning_ids:
                result = max(fictive_total_daily_hours)
            if plainning_ids:
                result += max(total_daily_hours)
            if self.account_id and not self.account_id.type_id.is_no_counting and not 0 <= self.daily_hours <= result:
                self.daily_hours = result
                return {'warning': {
                    'title': _('Warning'),
                    'message': _("Remaining working hours : %sh") % result,
                }}

    def _create_planning_date(self):
        """
        Create planning date
        :rtype: object
        """
        date = self.start_date
        while date <= self.end_date:
            leave_ids = self.env['resource.calendar.leaves'].search(
                [('date_from', '>=', date), ('date_to', '<=', date)])
            if date.weekday() < 5 and not leave_ids:
                self.env['das.planning.date'].sudo().create({
                    'date': date,
                    'planning_id': self.id
                })
            date += timedelta(days=1)

    def _update_current_day(self):
        """
        Update current day if fictive exists
        :rtype: object
        """
        planning_ids = self.env['das.planning'].search(
            [('resource_id', '=', self.resource_id.id), ('id', '!=', self._origin.id)]).filtered(
            lambda p: p.start_date <= self.start_date <= p.end_date and p.account_id.type_id.id != self.env.ref(
                'das.das_fictional_type').id)
        fictive_planning_ids = self.env['das.planning'].search(
            [('resource_id', '=', self.resource_id.id), ('id', '!=', self._origin.id)]).filtered(
            lambda p: p.start_date <= self.start_date <= p.end_date and p.account_id.type_id.id == self.env.ref(
                'das.das_fictional_type').id)
        planning_hours = sum(planning_ids.mapped('daily_hours')) if planning_ids else 0
        if fictive_planning_ids:
            result = NB_HOURS_PER_DAY - planning_hours - self.daily_hours + self._context.get('unlink_daily_hours', 0)
            if result > 0:
                fictive_planning_ids.daily_hours = result
            else:
                fictive_planning_ids.unlink()

    # def unlink(self):
    #     for rec in self:
    #         rec.with_context(unlink_daily_hours=rec.daily_hours)._update_current_day()
    #     res = super(DasPlanning, self).unlink()
    #     return res

    @api.model
    def create(self, vals):
        res = super(DasPlanning, self).create(vals)
        res._create_planning_date()
        res._update_current_day()
        return res

    def write(self, vals):
        res = super(DasPlanning, self).write(vals)
        self.env['das.planning.date'].sudo().search([('planning_id', '=', self.id)]).unlink()
        if self.active:
            self._create_planning_date()
            self._update_current_day()
        return res

    @api.model
    def gantt_unavailability(self, start_date, end_date, scale, group_bys=None, rows=None):
        """ Color weekends and leaves to Grey"""

        if scale != "year":
            local_format = "%Y-%m-%d %H:%M:%S"
            unavailabilities = []

            # Grey Weekends
            date = datetime.strptime(start_date, local_format)
            while date <= datetime.strptime(end_date, local_format):
                if date.weekday() == 5:
                    start = date.replace(hour=0, minute=0, second=0) - timedelta(hours=3)
                    stop = (date + timedelta(days=1)).replace(hour=23, minute=59, second=59) - timedelta(hours=3)
                    unavailabilities.append(
                        {'start': start.strftime(local_format), 'stop': stop.strftime(local_format)})
                date += timedelta(days=1)

            # Grey HR leaves
            leaves = self.env['resource.calendar.leaves'].search([])
            for leave in leaves:
                start = leave.date_from.replace(hour=0, minute=0, second=0) - timedelta(hours=3)
                stop = leave.date_to.replace(hour=23, minute=59, second=59) - timedelta(hours=3)
                unavailabilities.append(
                    {'start': start.strftime(local_format), 'stop': stop.strftime(local_format)})

            sorted_unavailabilities = sorted(unavailabilities, key=lambda d: d['start'])
            for row in rows:
                row['unavailabilities'] = sorted_unavailabilities

        return rows
