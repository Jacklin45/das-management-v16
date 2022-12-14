# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DasFictionalBatch(models.Model):
    _name = 'das.fictional.batch'
    _description = 'Create fictional batch'

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"), ]
