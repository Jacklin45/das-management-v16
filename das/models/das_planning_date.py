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

import time
from datetime import datetime, date, timedelta

from lxml import etree

from odoo import models, fields, api


class DasPlanningDate(models.Model):
    _name = 'das.planning.date'
    _description = "DAS Planning Date"
    _rec_name = 'account_label'

    date = fields.Date(string="Date", default=fields.Date.today)
    planning_id = fields.Many2one('das.planning', string="Planning", ondelete="cascade")
    active = fields.Boolean('Active', related='planning_id.active', default=True, store=True)

    department_id = fields.Many2one('hr.department', related='planning_id.department_id', store=True)
    resource_id = fields.Many2one('hr.employee', index=True, related='planning_id.resource_id', store=True)
    resource_id_active = fields.Boolean('hr.employee', related='planning_id.resource_id.active',
                                        store=True)
    resource_departure_date = fields.Date(string="Departure date", related='resource_id.departure_date')
    color = fields.Integer(related='planning_id.color', store=True)
    daily_hours = fields.Integer(related='planning_id.daily_hours', store=True)
    is_intercontrat = fields.Boolean(related='account_id.type_id.is_intercontrat')
    job_id = fields.Char(related='resource_id.job_id.name', string="Job", store=True)
    job_id_type = fields.Char(related='resource_id.job_id.type_id.type', string="Job type", store=True)
    task_id = fields.Many2one('project.task', related='planning_id.task_id', store=True)
    account_label = fields.Char(related='planning_id.account_label', store=True)

    #                    ------------- for getting data file  ------------- #
    account_id = fields.Many2one(related='planning_id.account_id', string='Account', store=True)
    type_id = fields.Many2one(related='planning_id.account_id.type_id', store=True)
    is_no_counting = fields.Boolean(related='planning_id.account_id.type_id.is_no_counting', string='Is no counting')
    category_id = fields.Many2one(related='planning_id.account_id.category_id', string='Category', store=True)
    project_id = fields.Many2one(related='planning_id.project_id', string='Project', store=True)
    partner_id = fields.Many2one(related='planning_id.project_id.partner_id', string='Partner', store=True)
    resource_name = fields.Char(string="Resource Name", compute="_compute_resource_name", store=True)
    planned_days = fields.Float(string="JPL", compute="_compute_planned_days", digits=(12, 3), store=True)
    fac_hours = fields.Float(string='FAC', compute='_compute_type_hours', digits=(12, 3), store=True)
    pnf_hours = fields.Float(string='PNF', compute='_compute_type_hours', digits=(12, 3), store=True)
    int_hours = fields.Float(string='INT', compute='_compute_type_hours', digits=(12, 3), store=True)
    rh_hours = fields.Float(string='RH', compute='_compute_type_hours', digits=(12, 3), store=True)
    avv_hours = fields.Float(string='AVV', compute='_compute_type_hours', digits=(12, 3), store=True)
    mgt_hours = fields.Float(string='MGT', compute='_compute_type_hours', digits=(12, 3), store=True)
    prv_hours = fields.Float(string='PRV', compute='_compute_type_hours', digits=(12, 3), store=True)
    ic = fields.Float(string='IC', compute='_compute_ic', digits=(12, 3), store=True)
    # / --------- daily -------- #

    daily_planned = fields.Float(string='Planned day', compute='_compute_daily', digits=(12, 3), store=True)
    daily_not_planned = fields.Float(string='JNPL', compute='_compute_daily', digits=(12, 3), store=True)
    hours_not_planned = fields.Float(string='NPL', compute='_compute_daily', store=True)

    globals_leaves_ids = fields.One2many(string="Global leave of current month",
                                         related='planning_id.globals_leaves_ids')
    is_global_leave = fields.Boolean(string='Global leave', compute='_compute_required', store=True)
    req = fields.Float(string='REQ', compute='_compute_required', store=True)
    jreq = fields.Float(string='JREQ', compute='_compute_required', digits=(12, 3), store=True)
    available_hour = fields.Float(string='Available hour', compute='_compute_daily', store=True)
    available_day = fields.Float(string='Available day', compute='_compute_daily', digits=(12, 3), store=True)

    # --------- daily -------- / #
    refresh = fields.Integer(string="Refresh", compute='_compute_refresh')
    total_resource = fields.Integer(string='Total resource', related='resource_id.total_resource', store=True)
    date_timestamp = fields.Integer(string="Date timestamp", readonly=True, compute='_compute_date_timestamp',
                                    store=True)
    today = fields.Date(string="Today", default=fields.Date.today, readonly=True)

    @api.depends('resource_id')
    def _compute_resource_name(self):
        for rec in self:
            rec.resource_name = str(rec.resource_id.name) + " " + str(rec.resource_id.first_name)

    @api.depends()
    def _compute_refresh(self):
        for rec in self:
            rec.refresh = 0 if rec.refresh else 1

    @api.depends('daily_hours', 'is_no_counting')
    def _compute_planned_days(self):
        for rec in self:
            rec.planned_days = 0 if rec.is_no_counting else rec.daily_hours / 8

    @api.depends('type_id', 'daily_hours', 'is_no_counting')
    def _compute_type_hours(self):
        for rec in self:
            rec.fac_hours = rec.daily_hours / 8 if rec.type_id.type == 'FAC' and not rec.is_no_counting else 0
            rec.pnf_hours = rec.daily_hours / 8 if rec.type_id.type == 'PNF' and not rec.is_no_counting else 0
            rec.int_hours = rec.daily_hours / 8 if rec.type_id.type == 'INT' and not rec.is_no_counting else 0
            rec.rh_hours = rec.daily_hours / 8 if rec.type_id.type == 'RH' and not rec.is_no_counting else 0
            rec.avv_hours = rec.daily_hours / 8 if rec.type_id.type == 'AVV' and not rec.is_no_counting else 0
            rec.mgt_hours = rec.daily_hours / 8 if rec.type_id.type == 'MGT' and not rec.is_no_counting else 0
            rec.prv_hours = rec.daily_hours / 8 if rec.type_id.type == 'PRV' and not rec.is_no_counting else 0

    @api.depends('is_intercontrat', 'date', 'resource_id', 'planning_id', 'daily_planned', 'is_no_counting')
    def _compute_ic(self):
        for rec in self:
            resource_date = self.env['das.planning.date'].sudo().search(
                [('is_intercontrat', '=', True), ('is_no_counting', '=', False), ('date', '=', rec.date),
                 ('resource_id', '=', rec.resource_id.id),
                 ('planning_id', '!=', rec.planning_id.id)])

            if rec.is_intercontrat and not rec.is_no_counting:
                total_ic = 0
                for date in resource_date:
                    total_ic = total_ic + date.planned_days

                rec.ic = total_ic + rec.planned_days if not resource_date else total_ic + rec.planned_days
                for id in resource_date:
                    id.ic = 0
            else:
                rec.ic = 0

    def get_compute_daily(self):
        # self.search([])._compute_type_hours()
        self.search([])._compute_daily()

    def get_compute_ic(self):
        # self.search([])._count_current_global_leave()
        self.search([])._compute_ic()

    @api.depends('planning_id', 'globals_leaves_ids', 'is_no_counting', 'is_global_leave')
    def _compute_required(self):
        for rec in self:
            global_leaves = []
            for leave in rec.globals_leaves_ids:
                if leave.date_from:
                    date_start = leave.date_from
                    date_end = leave.date_to
                    while date_start <= date_end:
                        global_leaves.append(date_start.date())
                        date_start += timedelta(days=1)

            rec.is_global_leave = True if rec.date in global_leaves else False
            calendar_hour = rec.resource_id.resource_calendar_id.hours_per_day
            rec.req = 0 if rec.is_no_counting or rec.is_global_leave else calendar_hour
            # day required
            rec.jreq = 0 if rec.is_no_counting or rec.is_global_leave else rec.req / 8
            self.env['das.planning.date'].search(
                [('date', '=', rec.date), ('resource_id', '=', rec.resource_id.id),
                 ('planning_id', '!=', rec.planning_id.id)]).write(
                {'req': 0, 'jreq': 0})

    @api.depends('planning_id', 'date', 'resource_id', 'daily_hours', 'is_no_counting')
    def _compute_daily(self):
        for rec in self:
            planning_days = self.env['das.planning.date'].sudo().search(
                [("date", "=", rec.date), ('resource_id', '=', rec.resource_id.id)])
            calendar_hour = rec.resource_id.resource_calendar_id.hours_per_day

            total_hours = 0
            for planning in planning_days:
                total_hours = total_hours + (0 if planning.is_no_counting else planning.daily_hours)

            # Planned on day
            rec.daily_planned = total_hours / 8
            # Day not planned
            rec.daily_not_planned = 0 if rec.is_no_counting else round((calendar_hour - total_hours) / 8)
            # Hours not planned
            rec.hours_not_planned = 0 if rec.is_no_counting else (calendar_hour - total_hours)
            # hours required
            # available hour
            rec.available_hour = 0 if rec.is_no_counting else calendar_hour - total_hours
            # available day
            rec.available_day = 0 if rec.is_no_counting else rec.jreq - rec.daily_planned
            self.env['das.planning.date'].search(
                [('date', '=', rec.date), ('resource_id', '=', rec.resource_id.id),
                 ('planning_id', '!=', rec.planning_id.id)]).write(
                {'daily_not_planned': 0, 'hours_not_planned': 0, 'daily_planned': 0,
                 'available_hour': 0, 'available_day': 0})

    def get_first_date_of_current_month(self, year, month):
        first_date = date(year, month, 1)
        return first_date.strftime("%Y-%m-%d")

    def get_last_date_of_month(self, year, month):
        curent_month = month if month == 12 else (month + 1)
        last_date = date(year, curent_month, 1) + timedelta(days=-1)
        return last_date.strftime("%Y-%m-%d")

    def _calc_total_days_current_month(self, start_date, end_date):
        total_days_current_month = 0
        from_date = datetime.strptime(str(start_date), '%Y-%m-%d')
        to_date = datetime.strptime(str(end_date), '%Y-%m-%d')
        while from_date <= to_date:
            if from_date.weekday() < 5:
                total_days_current_month += 1
            from_date += timedelta(days=1)
        return total_days_current_month

    @api.depends('date')
    def _compute_date_timestamp(self):
        for rec in self:
            rec.date_timestamp = (time.mktime(rec.date.timetuple())) // (60 * 60 * 24)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(DasPlanningDate, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                              toolbar=toolbar, submenu=submenu)

        if view_type == 'dashboard':
            doc = etree.XML(result['arch'])
            billable_goal_days = doc.xpath("//formula[@name='billable_goal']")
            to_fill_days = doc.xpath("//formula[@name='to_fill_days']")

            if billable_goal_days and to_fill_days:
                billable_goal = self.env['ir.config_parameter'].sudo().get_param('das.billable_goal')

                # For billable_goal_days
                value_billable_goal_days = "(record.resources * record.nb_working_days * " + str(
                    billable_goal) + "/ 100)"
                value_label = " | " + str(billable_goal) + " %"
                billable_goal_days[0].set("value_label", value_label)
                billable_goal_days[0].set("value", value_billable_goal_days)

                # For to_fill_days
                value = value_billable_goal_days + " - record.total_billable_days"
                to_fill_days[0].set("value", value)

                result['arch'] = etree.tostring(doc, encoding='unicode')

        return result

    def get_resource_not_planned(self):
        self.search([])._compute_resource_not_planned()

    # Check res not planned and create it
    @api.depends('date', 'resource_id', 'planning_id')
    def _compute_resource_not_planned(self):
        local_format = "%Y-%m-%d"
        resource_id = self.env['hr.employee']
        resources = self.env['hr.employee'].search([]).mapped('id')
        plannings = self.search([('date', '>=', date.today())]).mapped('resource_id.id')
        date_planned = set(self.search([('date', '>=', date.today())]).mapped('date'))
        end_date = max(self.search([('date', '>=', date.today())]).mapped('date'))
        res_not_planned = set([id for id in resources if id not in plannings])
        date_from = datetime.strptime(str(date.today()), local_format)
        date_to = datetime.strptime(str(end_date), local_format)
        list_date_not_planned = []
        while date_from <= date_to:
            if date_from.weekday() < 5 and date_from not in date_planned:
                list_date_not_planned.append(date_from.date())
            date_from += timedelta(days=1)

        for res in resources:
            for date_not_planned in list_date_not_planned:
                if not self.search([('resource_id', '=', resource_id.browse(res).id), ('date', '=', date_not_planned)]):
                    self.env['das.planning'].sudo().create(
                        {'resource_id': resource_id.browse(res).id, 'account_id': self.env['das.account'].sudo().search(
                            [('reference', '=', '[fic_project] Fictional project [Fic Account ref]')]).id,
                         'daily_hours': 0,
                         'start_date': date_not_planned, 'end_date': date_not_planned})
