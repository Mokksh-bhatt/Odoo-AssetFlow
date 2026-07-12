# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow Allocation',
    'version': '19.0.1.0.0',
    'category': 'AssetFlow',
    'summary': 'AssetFlow Allocation and Transfer Module',
    'description': """
        Allocation of assets to employees/departments with hard conflict prevention, 
        plus the transfer-request remedy workflow.
    """,
    'author': 'Mokksh Bhatt',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_notification'],
    'data': [
        'security/ir.model.access.csv',
        'security/allocation_rules.xml',
        'views/allocation_views.xml',
        'views/transfer_request_views.xml',
        'views/allocation_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
