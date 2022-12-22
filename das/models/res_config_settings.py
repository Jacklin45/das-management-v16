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

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    billable_goal = fields.Integer(string="Billable goal", default=70)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('das.billable_goal', self.billable_goal)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(billable_goal=self.env['ir.config_parameter'].sudo().get_param('das.billable_goal'))
        return res

    @api.constrains('billable_goal')
    def _check_billable_goal(self):
        if self.billable_goal < 0 or self.billable_goal > 100:
            raise ValidationError(_('Purcentage must be between 0 and 100 !'))
