# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow Asset',
    'version': '19.0.1.0.0',
    'category': 'AssetFlow',
    'summary': 'Asset Registry and Lifecycle',
    'depends': ['assetflow_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/asset_rules.xml',
        'data/asset_sequence.xml',
        'views/asset_views.xml',
        'views/location_views.xml',
        'views/asset_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
