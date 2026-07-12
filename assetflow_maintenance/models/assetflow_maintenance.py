from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class AssetFlowMaintenance(models.Model):
    _name = 'assetflow.maintenance'
    _description = 'Maintenance Request'
    _inherit = ['assetflow.approval.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True, tracking=True)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True, tracking=True)
    department_id = fields.Many2one('assetflow.department', related='requested_by.assetflow_department_id', string='Department', store=True)
    technician_id = fields.Many2one('res.users', string='Technician', tracking=True)
    
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, required=True, tracking=True)
    scheduled_date = fields.Date(string='Scheduled Date', tracking=True)
    completion_date = fields.Date(string='Completion Date', tracking=True)
    
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective')
    ], string='Maintenance Type', required=True, default='corrective', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', required=True, default='low', tracking=True)
    
    estimated_cost = fields.Float(string='Estimated Cost', tracking=True)
    actual_cost = fields.Float(string='Actual Cost', tracking=True)
    
    description = fields.Text(string='Description', required=True)
    work_performed = fields.Text(string='Work Performed', tracking=True)
    
    active = fields.Boolean(default=True)
    previous_asset_state = fields.Char(string='Previous State', copy=False)
    
    state = fields.Selection(selection_add=[
        ('completed', 'Completed')
    ], ondelete={'completed': 'set default'})
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('assetflow.maintenance') or _('New')
        return super().create(vals_list)
        
    @api.constrains('asset_id', 'state', 'active')
    def _check_one_active_maintenance(self):
        for record in self:
            if record.state not in ['completed', 'rejected'] and record.active:
                domain = [
                    ('asset_id', '=', record.asset_id.id),
                    ('id', '!=', record.id),
                    ('state', 'not in', ['completed', 'rejected']),
                    ('active', '=', True)
                ]
                count = self.search_count(domain)
                if count > 0:
                    raise ValidationError(_("There is already an active maintenance request for this asset."))
                    
    @api.constrains('completion_date', 'request_date')
    def _check_dates(self):
        for record in self:
            if record.completion_date and record.request_date and record.completion_date < record.request_date:
                raise ValidationError(_("Completion date cannot be before request date."))
                
    @api.constrains('estimated_cost', 'actual_cost')
    def _check_costs(self):
        for record in self:
            if record.estimated_cost < 0 or record.actual_cost < 0:
                raise ValidationError(_("Costs cannot be negative."))
                
    @api.constrains('state', 'completion_date', 'work_performed')
    def _check_completion_requirements(self):
        for record in self:
            if record.state == 'completed':
                if not record.completion_date or not record.work_performed:
                    raise ValidationError(_("Completion Date and Work Performed are required to complete maintenance."))
                    
    # Approval Mixin Overrides
    def _on_submit(self):
        for record in self:
            record.previous_asset_state = record.asset_id.state
            record.asset_id._change_state('maintenance', f"Maintenance request {record.name} submitted.")
            
    def _on_approve(self):
        for record in self:
            self.env['assetflow.notification'].create_notification(
                record.requested_by.id,
                'maintenance_approved',
                'Maintenance Approved',
                f"Maintenance request {record.name} approved.",
                record._name,
                record.id
            )
            
    def _on_reject(self):
        for record in self:
            if record.previous_asset_state:
                record.asset_id._change_state(record.previous_asset_state, f"Maintenance request {record.name} rejected. Restoring state.")
            self.env['assetflow.notification'].create_notification(
                record.requested_by.id,
                'maintenance_rejected',
                'Maintenance Rejected',
                f"Maintenance request {record.name} rejected.",
                record._name,
                record.id
            )
            
    def action_complete(self):
        for record in self:
            if record.state != 'approved':
                raise UserError(_("Only approved requests can be completed."))
            if not record.completion_date or not record.work_performed:
                raise UserError(_("Please provide Completion Date and Work Performed before completing."))
            record.asset_id._change_state('available', f"Maintenance request {record.name} completed.")
            record.state = 'completed'
            # no predefined notification type for maintenance_completed, just use maintenance_approved or don't send one. Wait, let's use 'maintenance_approved'
            self.env['assetflow.notification'].create_notification(
                record.requested_by.id,
                'maintenance_approved',
                'Maintenance Completed',
                f"Maintenance request {record.name} completed.",
                record._name,
                record.id
            )
            
    @api.model
    def _cron_check_maintenance(self):
        today = date.today()
        # Overdue maintenance reminders
        overdue_requests = self.search([
            ('state', 'in', ['pending', 'approved']),
            ('scheduled_date', '<', today)
        ])
        for req in overdue_requests:
            self.env['assetflow.notification'].create_notification(
                req.technician_id.id or req.requested_by.id,
                'maintenance_approved',
                'Overdue Maintenance',
                f"Maintenance request {req.name} is overdue.",
                req._name,
                req.id
            )
            
        # Preventive maintenance reminders (e.g. 7 days from now)
        preventive_date = fields.Date.to_string(fields.Date.add(today, days=7))
        upcoming = self.search([
            ('state', 'in', ['draft', 'pending', 'approved']),
            ('scheduled_date', '=', preventive_date),
            ('maintenance_type', '=', 'preventive')
        ])
        for req in upcoming:
            self.env['assetflow.notification'].create_notification(
                req.technician_id.id or req.requested_by.id,
                'maintenance_approved',
                'Preventive Maintenance',
                f"Upcoming preventive maintenance {req.name} in 7 days.",
                req._name,
                req.id
            )
