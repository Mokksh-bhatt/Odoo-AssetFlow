{
    'name': 'AssetFlow Dashboard',
    'version': '1.0',
    'category': 'Asset Management',
    'summary': 'AssetFlow Dashboard',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_allocation', 'assetflow_booking', 'assetflow_maintenance'],
    'data': [
        'views/dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'assetflow_dashboard/static/src/js/dashboard.js',
            'assetflow_dashboard/static/src/xml/dashboard_templates.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
