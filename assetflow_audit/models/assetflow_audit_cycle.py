from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AssetFlowAuditCycle(models.Model):
    _name = 'assetflow.audit.cycle'
    _description = 'Audit Cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True, copy=False)
    
    scope_type = fields.Selection([
        ('department', 'By Department'),
        ('location', 'By Location'),
        ('all', 'All Assets')
    ], string='Scope Type', required=True, default='all', tracking=True)
    
    department_id = fields.Many2one('assetflow.department', string='Department')
    location_id = fields.Many2one('assetflow.location', string='Location')
    
    date_from = fields.Date(string='Start Date', required=True, tracking=True)
    date_to = fields.Date(string='End Date', required=True, tracking=True)
    
    auditor_ids = fields.Many2many('res.users', string='Auditors', required=True, tracking=True)
    
    line_ids = fields.One2many('assetflow.audit.line', 'cycle_id', string='Audit Lines')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('assetflow.audit.cycle') or _('New')
        return super().create(vals_list)
        
    def action_start_audit(self):
        for record in self:
            if not record.auditor_ids:
                raise UserError(_("At least one auditor must be assigned before starting the audit."))
            record.state = 'in_progress'
            
    def action_close_audit(self):
        for record in self:
            # check for missing/damaged to update asset state if needed
            for line in record.line_ids:
                if line.result == 'missing':
                    line.asset_id._change_state('lost', reason=f"Audit {record.name} discrepancy: Missing")
                elif line.result == 'damaged':
                    line.asset_id._change_state('maintenance', reason=f"Audit {record.name} discrepancy: Damaged")
            record.state = 'closed'
            
    def action_generate_lines(self):
        self.ensure_one()
        return {
            'name': _('Generate Audit Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'assetflow.audit.line.generate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_cycle_id': self.id},
        }
