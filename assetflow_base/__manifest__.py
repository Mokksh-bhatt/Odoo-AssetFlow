# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow Base',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Core foundation for AssetFlow ERP',
    'description': """
        Base module for AssetFlow ERP.
        Provides core models (Departments, Categories, Employee extension)
        and essential mixins (Approval, Sequence) that other modules depend on.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/department_category_rules.xml',
        
        'data/assetflow_sequences.xml',
        
        'views/assetflow_menus.xml',
        'views/department_views.xml',
        'views/category_views.xml',
        'views/res_users_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
