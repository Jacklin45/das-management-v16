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

{
    'name': 'ePlanning-IT',
    'summary': 'Manage ePlanning IT',
    'description': """
This apps helps to manage ePlanning IT.
=====================
""",
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'depends': ['das_base', 'das_project', 'das_hr', 'web_gantt'],
    'data': [
        # Data
        'data/ir_cron.xml',
        'data/data_fictional_planning.xml',
        # Security
        'security/ir.model.access.csv',
        # 'security/das_security.xml',
        # Wizards
        'wizard/planning_division_wizard.xml',
        'wizard/availability_filter_wizard.xml',
        'wizard/planning_fictional_wizard.xml',
        # Views
        'views/das_category_views.xml',
        'views/das_category_type_views.xml',
        'views/das_locality_views.xml',
        'views/das_account_views.xml',
        'views/das_account_reference.xml',
        'views/das_planning_views.xml',
        'views/das_planning_date_views.xml',
        'views/das_fictional_views.xml',
        'views/das_fictional_batch_views.xml',
        'views/das_analyse_views.xml',
        'views/res_availability_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_employee_views.xml',
        'views/project_project_views.xml',
        'views/das_planning_menus.xml',
        # Menus

    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'das/static/src/**/*',
            'das/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
