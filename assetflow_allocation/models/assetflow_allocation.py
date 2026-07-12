# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetflowAllocation(models.Model):
    _name = 'assetflow.allocation'
    _description = 'Asset Allocation'
    _order = 'allocation_date desc, id desc'

    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True)
    employee_id = fields.Many2one('res.users', string='Assigned To', required=True)
    department_id = fields.Many2one('assetflow.department', string='Department', related='employee_id.assetflow_department_id', store=True)
    allocated_by = fields.Many2one('res.users', string='Allocated By', default=lambda self: self.env.user, required=True)
    allocation_date = fields.Datetime(string='Allocation Date', default=fields.Datetime.now, required=True)
    expected_return_date = fields.Datetime(string='Expected Return')
    actual_return_date = fields.Datetime(string='Actual Return', readonly=True)
    return_condition_notes = fields.Text(string='Return Condition Notes')
    
    status = fields.Selection([
        ('active', 'Active'),
        ('returned', 'Returned')
    ], string='Status', default='active', required=True, tracking=True)
    
    active = fields.Boolean(string='Active Record', default=True)

    def init(self):
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS assetflow_allocation_unique_active 
            ON assetflow_allocation (asset_id) WHERE status = 'active';
        """)

    @api.constrains('asset_id', 'status')
    def _check_single_active_allocation(self):
        for record in self:
            if record.status == 'active':
                domain = [
                    ('asset_id', '=', record.asset_id.id),
                    ('status', '=', 'active'),
                    ('id', '!=', record.id)
                ]
                existing = self.search(domain, limit=1)
                if existing:
                    holder_name = existing.employee_id.name if existing.employee_id else "another user"
                    raise ValidationError(_(
                        "Asset '%s' is already actively allocated to %s. "
                        "Please request a transfer instead."
                    ) % (record.asset_id.name, holder_name))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.status == 'active' and record.asset_id:
                record.asset_id.write({
                    'current_holder_employee_id': record.employee_id.id,
                    'current_holder_department_id': record.department_id.id if record.department_id else False,
                })
                if record.asset_id.state != 'allocated':
                    record.asset_id._change_state('allocated', reason='New allocation to %s' % record.employee_id.name)
                
                self.env['assetflow.notification'].create_notification(
                    user_id=record.employee_id.id,
                    notification_type='asset_assigned',
                    title='Asset Assigned',
                    body=f"Asset {record.asset_id.name} has been allocated to you.",
                    res_model='assetflow.allocation',
                    res_id=record.id
                )
        return records

    def action_return(self):
        for record in self:
            if record.status != 'active':
                raise ValidationError(_("Only active allocations can be returned."))
            if not record.return_condition_notes:
                raise ValidationError(_("Return Condition Notes are required before returning the asset."))
                
            record._close_allocation()
            
            record.asset_id.write({
                'current_holder_employee_id': False,
                'current_holder_department_id': False,
            })
            record.asset_id._change_state('available', reason='Asset returned from %s' % record.employee_id.name)
            
            if record.expected_return_date and record.actual_return_date > record.expected_return_date:
                self.env['assetflow.notification'].create_notification(
                    user_id=record.allocated_by.id or record.employee_id.id,
                    notification_type='overdue_return',
                    title='Asset Returned Overdue',
                    body=f"Asset {record.asset_id.name} was returned late.",
                    res_model='assetflow.allocation',
                    res_id=record.id
                )

    def _close_allocation(self):
        for record in self:
            if record.status == 'active':
                record.status = 'returned'
                record.actual_return_date = fields.Datetime.now()
