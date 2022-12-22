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
from odoo.exceptions import ValidationError


class DasAnalysis(models.Model):
    _name = 'das.analysis'
    _description = "Das analysis"
    _rec_name = 'department_id'

    department_id = fields.Many2one('hr.department', string="Department")
    total_hours = fields.Float(string='Total hours', compute='compute_analyse_pdo', default=0, readonly=True)
    total_hours_fact = fields.Float(string='Billable total hours', compute='compute_analyse_pdo', default=0,
                                    readonly=True)
    tot_account = fields.Float(string="All Account", compute='compute_analyse_pdo', default=0, readonly=True)
    tot_account_fact = fields.Float(string="All billable account", compute='compute_analyse_pdo', default=0,
                                    readonly=True)
    analyse = fields.Float(string='Analyse %', compute='compute_analyse_pdo', default=0, readonly=True)

    productivity = fields.Char(string='productivity %', compute='compute_analyse_pdo', default=' ', readonly=True)
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')

    @api.depends('department_id')
    def compute_analyse_pdo(self):
        for rec in self:
            accounts = self.env['das.account'].search([('department_id', '=', rec.department_id.id)])
            billable_accounts = self.env['das.account'].search([('department_id', '=', rec.department_id.id),
                                                                ('category_id.type_id', '=',
                                                                 "FAC")])

            rec.tot_account = len(accounts)
            rec.tot_account_fact = len(billable_accounts)

            if accounts:
                rec.analyse = len(billable_accounts) / len(accounts)
            else:
                raise ValidationError('no project')

            rec.total_hours = sum(self.env['das.planning'].search([
                ('account_id', 'in', accounts.mapped('id'))]).mapped('total_hours'))
            rec.total_hours_fact = sum(self.env['das.planning'].search([
                ('account_id', 'in', billable_accounts.mapped('id'))]).mapped('total_hours'))

            if rec.analyse > 0.65:
                rec.productivity = 'Success, we achieved {}%'.format(round(rec.analyse * 100, 2))
            else:
                rec.productivity = 'Failure, we achieved {}%'.format(round(rec.analyse * 100, 2))
