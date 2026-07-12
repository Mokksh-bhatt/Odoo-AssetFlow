# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetflowTransferRequest(models.Model):
    _name = 'assetflow.transfer.request'
    _description = 'Asset Transfer Request'
    _inherit = ['mail.thread', 'assetflow.approval.mixin']
    _order = 'create_date desc, id desc'

    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True)
    requester_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True)
    current_holder_id = fields.Many2one('res.users', string='Current Holder', related='asset_id.current_holder_employee_id', readonly=True)
    
    target_employee_id = fields.Many2one('res.users', string='Target Employee', required=True)
    target_department_id = fields.Many2one('assetflow.department', string='Target Department', related='target_employee_id.assetflow_department_id', store=True)
    
    reason = fields.Text(string='Transfer Reason', required=True)

    def action_approve(self):
        super().action_approve()
        for record in self:
            active_allocation = self.env['assetflow.allocation'].search([
                ('asset_id', '=', record.asset_id.id),
                ('status', '=', 'active')
            ], limit=1)
            
            if active_allocation:
                active_allocation.return_condition_notes = "Transferred via Transfer Request."
                active_allocation._close_allocation()
                
            self.env['assetflow.allocation'].sudo().create({
                'asset_id': record.asset_id.id,
                'employee_id': record.target_employee_id.id,
                'allocated_by': self.env.user.id,
            })
            
            self.env['assetflow.notification'].create_notification(
                user_id=record.target_employee_id.id,
                notification_type='transfer_approved',
                title='Transfer Approved',
                body=f"Transfer request for {record.asset_id.name} has been approved. The asset is now assigned to you.",
                res_model='assetflow.transfer.request',
                res_id=record.id
            )

    def action_reject(self):
        super().action_reject()
