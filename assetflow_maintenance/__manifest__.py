{
    'name': 'AssetFlow Maintenance',
    'version': '1.0',
    'category': 'Asset Management',
    'summary': 'Asset maintenance requests and tracking',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_notification', 'assetflow_allocation'],
    'data': [
        'security/ir.model.access.csv',
        'security/maintenance_rules.xml',
        'data/maintenance_cron.xml',
        'views/maintenance_views.xml',
        'views/maintenance_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
