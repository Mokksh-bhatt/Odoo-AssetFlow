# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow Maintenance',
    'version': '1.0',
    'category': 'AssetFlow',
    'summary': 'AssetFlow Maintenance Module',
    'description': """
        Manage preventive and corrective maintenance for assets.
    """,
    'author': 'Mokksh Bhatt',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_notification'],
    'data': [
        'security/ir.model.access.csv',
        'security/maintenance_rules.xml',
        'data/maintenance_cron.xml',
        'views/maintenance_views.xml',
        'views/maintenance_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
