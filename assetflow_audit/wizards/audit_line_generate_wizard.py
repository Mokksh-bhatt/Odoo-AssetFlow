from odoo import models, fields, api

class AuditLineGenerateWizard(models.TransientModel):
    _name = 'assetflow.audit.line.generate.wizard'
    _description = 'Generate Audit Lines Wizard'

    cycle_id = fields.Many2one('assetflow.audit.cycle', string='Audit Cycle', required=True)
    
    def generate_lines(self):
        self.ensure_one()
        cycle = self.cycle_id
        
        domain = [('active', '=', True)]
        if cycle.scope_type == 'department' and cycle.department_id:
            domain.append(('current_holder_department_id', '=', cycle.department_id.id))
        elif cycle.scope_type == 'location' and cycle.location_id:
            domain.append(('location_id', '=', cycle.location_id.id))
            
        assets = self.env['assetflow.asset'].search(domain)
        
        existing_assets = cycle.line_ids.mapped('asset_id')
        assets_to_add = assets - existing_assets
        
        lines_vals = []
        for asset in assets_to_add:
            lines_vals.append({
                'cycle_id': cycle.id,
                'asset_id': asset.id,
                'result': 'pending',
            })
            
        if lines_vals:
            self.env['assetflow.audit.line'].create(lines_vals)
            
        return {'type': 'ir.actions.act_window_close'}
