from odoo import models, fields, api

class AssetFlowAuditDiscrepancy(models.Model):
    _name = 'assetflow.audit.discrepancy'
    _description = 'Audit Discrepancy'
    _inherit = ['assetflow.approval.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True)
    line_id = fields.Many2one('assetflow.audit.line', string='Audit Line', required=True, ondelete='cascade', tracking=True)
    asset_id = fields.Many2one('assetflow.asset', related='line_id.asset_id', string='Asset', store=True)
    cycle_id = fields.Many2one('assetflow.audit.cycle', related='line_id.cycle_id', string='Audit Cycle', store=True)
    
    issue_type = fields.Selection([
        ('missing', 'Missing Asset'),
        ('damaged', 'Damaged Asset')
    ], string='Issue Type', required=True, tracking=True)
    
    description = fields.Text(string='Description', tracking=True)
    resolution = fields.Text(string='Resolution Notes', tracking=True)
    
    state = fields.Selection(selection_add=[
        ('resolved', 'Resolved')
    ], ondelete={'resolved': 'set default'})
    
    def action_resolve(self):
        for record in self:
            record.state = 'resolved'
