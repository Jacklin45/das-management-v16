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


class DasAccountReference(models.Model):
    _name = 'das.account.reference'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "DAS Account Reference"
    _rec_name = 'reference'

    reference = fields.Char(string="Purchase Order", required=True, tracking=True)
    budget = fields.Float(string="Budget", tracking=True)
    to_pay_mga = fields.Float(string="To pay mga", compute='_compute_pay_mga', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda x: x.env.company.currency_id)
    tjm_currency_id = fields.Many2one('res.currency', string='Currency',
                                      default=lambda x: x.env.ref('base.EUR').id)
    locality_id = fields.Many2one('das.locality', string="Locality")
    tjm = fields.Monetary(string="TJM", currency_field='tjm_currency_id', tracking=True)
    rate_mga = fields.Monetary(string="Rate MGA", currency_field='tjm_currency_id', default=4000, tracking=True)
    currency_mga = fields.Many2one(string='Currency mga', comodel_name='res.currency',
                                   default=lambda x: x.env.company)
    payment_condition = fields.Char(string="Payment condition", tracking=True)
    category_id = fields.Many2one('das.category', string="Category", tracking=True)
    type_id = fields.Many2one(related='category_id.type_id', string='Type', store=True)
    start_date = fields.Date(string="Start date", tracking=True)
    end_date = fields.Date(string="End date", tracking=True)

    @api.depends('budget', 'tjm', 'rate_mga')
    def _compute_pay_mga(self):
        for rec in self:
            rec.to_pay_mga = rec.budget * rec.tjm * rec.rate_mga

    _sql_constraints = [
        ('name_uniq', 'unique (reference)', "Tag name already exists!"), ]
