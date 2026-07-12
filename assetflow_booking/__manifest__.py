# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow Booking',
    'version': '1.0',
    'category': 'AssetFlow',
    'summary': 'AssetFlow Booking Module',
    'description': """
        Time-slot booking of shared/bookable assets with strict overlap prevention.
    """,
    'author': 'Mokksh Bhatt',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_notification'],
    'data': [
        'security/ir.model.access.csv',
        'security/booking_rules.xml',
        'data/booking_cron.xml',
        'views/booking_views.xml',
        'views/booking_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
