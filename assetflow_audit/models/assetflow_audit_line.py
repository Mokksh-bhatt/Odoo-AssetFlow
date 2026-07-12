from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AssetFlowAuditLine(models.Model):
    _name = 'assetflow.audit.line'
    _description = 'Audit Line'

    cycle_id = fields.Many2one('assetflow.audit.cycle', string='Audit Cycle', required=True, ondelete='cascade')
    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True)
    expected_department_id = fields.Many2one('assetflow.department', related='asset_id.current_holder_department_id', string='Expected Department', store=True)
    expected_location_id = fields.Many2one('assetflow.location', related='asset_id.location_id', string='Expected Location', store=True)
    
    result = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('missing', 'Missing'),
        ('damaged', 'Damaged')
    ], string='Result', default='pending', required=True)
    
    notes = fields.Text(string='Notes')
    
    @api.constrains('result')
    def _check_create_discrepancy(self):
        for line in self:
            if line.result in ['missing', 'damaged']:
                # Check if an open discrepancy already exists
                existing = self.env['assetflow.audit.discrepancy'].search([
                    ('line_id', '=', line.id),
                    ('state', '!=', 'resolved')
                ])
                if not existing:
                    self.env['assetflow.audit.discrepancy'].sudo().create({
                        'line_id': line.id,
                        'name': f"Discrepancy for {line.asset_id.name}",
                        'issue_type': line.result,
                        'description': line.notes or f"Asset marked as {line.result}",
                    })
                    
    def write(self, vals):
        for line in self:
            if line.cycle_id.state == 'closed':
                raise UserError(_("Cannot modify lines of a closed audit cycle."))
        return super().write(vals)
