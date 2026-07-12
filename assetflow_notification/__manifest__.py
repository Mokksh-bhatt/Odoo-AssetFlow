# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow Notification',
    'version': '1.0',
    'category': 'AssetFlow',
    'summary': 'AssetFlow Notification Service',
    'description': """
        Thin, low-level notification service every domain module can call into, 
        plus a personal notification feed UI for AssetFlow.
    """,
    'author': 'Mokksh Bhatt',
    'depends': ['assetflow_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/notification_rules.xml',
        'views/notification_views.xml',
        'views/notification_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
