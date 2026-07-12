{
    'name': 'AssetFlow Reports',
    'version': '1.0',
    'category': 'Asset Management',
    'summary': 'Operational Analytics',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_allocation', 'assetflow_booking', 'assetflow_maintenance', 'assetflow_audit'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_views.xml',
        'views/report_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
