# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetflowMaintenance(models.Model):
    _name = 'assetflow.maintenance'
    _description = 'Asset Maintenance'
    _inherit = ['assetflow.approval.mixin']
    _order = 'request_date desc, id desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True)
    technician_id = fields.Many2one('res.users', string='Technician')
    department_id = fields.Many2one('assetflow.department', string='Department', related='requested_by.assetflow_department_id', store=True)

    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, required=True)
    scheduled_date = fields.Datetime(string='Scheduled Date')
    completion_date = fields.Datetime(string='Completion Date')
    
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective')
    ], string='Maintenance Type', required=True, default='corrective')
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='low')
    
    description = fields.Text(string='Description', required=True)
    work_performed = fields.Text(string='Work Performed')
    
    estimated_cost = fields.Float(string='Estimated Cost', default=0.0)
    actual_cost = fields.Float(string='Actual Cost', default=0.0)
    
    state = fields.Selection(selection_add=[
        ('completed', 'Completed')
    ], ondelete={'completed': 'set default'})
    
    previous_asset_state = fields.Char(string='Previous Asset State', readonly=True)
    active = fields.Boolean(string='Active', default=True)

    @api.depends('asset_id', 'request_date')
    def _compute_name(self):
        for record in self:
            if record.asset_id and record.request_date:
                date_str = record.request_date.strftime('%Y-%m-%d')
                record.name = f"MNT-{record.asset_id.name}-{date_str}"
            else:
                record.name = "New Maintenance"

    @api.constrains('completion_date', 'request_date')
    def _check_dates(self):
        for record in self:
            if record.completion_date and record.request_date and record.completion_date < record.request_date:
                raise ValidationError(_("Completion Date cannot be earlier than Request Date."))

    @api.constrains('estimated_cost', 'actual_cost')
    def _check_costs(self):
        for record in self:
            if record.estimated_cost < 0:
                raise ValidationError(_("Estimated Cost cannot be negative."))
            if record.actual_cost < 0:
                raise ValidationError(_("Actual Cost cannot be negative."))

    def action_submit(self):
        super().action_submit()
        for record in self:
            record.previous_asset_state = record.asset_id.state
            record.asset_id._change_state('maintenance', reason="Maintenance requested.")

    def action_approve(self):
        super().action_approve()
        for record in self:
            self.env['assetflow.notification'].create_notification(
                user_id=record.requested_by.id,
                notification_type='maintenance_approved',
                title='Maintenance Approved',
                body=f"Your maintenance request for {record.asset_id.name} has been approved.",
                res_model='assetflow.maintenance',
                res_id=record.id
            )

    def action_reject(self):
        super().action_reject()
        for record in self:
            prev_state = record.previous_asset_state or 'available'
            record.asset_id._change_state(prev_state, reason="Maintenance rejected.")
            self.env['assetflow.notification'].create_notification(
                user_id=record.requested_by.id,
                notification_type='maintenance_rejected',
                title='Maintenance Rejected',
                body=f"Your maintenance request for {record.asset_id.name} was rejected.",
                res_model='assetflow.maintenance',
                res_id=record.id
            )

    def action_complete(self):
        for record in self:
            if record.state != 'approved':
                raise ValidationError(_("Only approved maintenance requests can be completed."))
            if not record.completion_date:
                raise ValidationError(_("Completion Date is required."))
            if not record.work_performed:
                raise ValidationError(_("Work Performed notes are required."))
            if record.actual_cost < 0:
                raise ValidationError(_("Actual cost cannot be negative."))
                
            record.state = 'completed'
            record.asset_id._change_state('available', reason="Maintenance completed.")
            
            self.env['assetflow.notification'].create_notification(
                user_id=record.requested_by.id,
                notification_type='maintenance_approved',
                title='Maintenance Completed',
                body=f"Maintenance for {record.asset_id.name} has been marked as completed.",
                res_model='assetflow.maintenance',
                res_id=record.id
            )

    @api.model
    def _cron_overdue_maintenance(self):
        now = fields.Datetime.now()
        overdue_records = self.search([
            ('state', '=', 'approved'),
            ('scheduled_date', '<', now)
        ])
        for record in overdue_records:
            target_user = record.technician_id or record.requested_by
            self.env['assetflow.notification'].create_notification(
                user_id=target_user.id,
                notification_type='overdue_maintenance',
                title='Overdue Maintenance',
                body=f"Maintenance for {record.asset_id.name} scheduled on {record.scheduled_date} is overdue.",
                res_model='assetflow.maintenance',
                res_id=record.id
            )
