from odoo import models, api

class AssetFlowAsset(models.Model):
    _inherit = 'assetflow.asset'

    @api.model
    def get_dashboard_data(self):
        total_assets = self.search_count([])
        available_assets = self.search_count([('state', '=', 'available')])
        allocated_assets = self.search_count([('state', '=', 'allocated')])
        maintenance_assets = self.search_count([('state', '=', 'maintenance')])
        
        total_bookings = self.env['assetflow.booking'].search_count([('status', 'in', ['pending', 'approved'])])
        open_maintenance = self.env['assetflow.maintenance'].search_count([('state', 'in', ['draft', 'pending'])])
        
        return {
            'total_assets': total_assets,
            'available_assets': available_assets,
            'allocated_assets': allocated_assets,
            'maintenance_assets': maintenance_assets,
            'total_bookings': total_bookings,
            'open_maintenance': open_maintenance,
        }
