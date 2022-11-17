# -*- coding: utf-8 -*-

{
    'name': 'DAS Project',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
DAS Project  
==============
""",
    'depends': ['das_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
