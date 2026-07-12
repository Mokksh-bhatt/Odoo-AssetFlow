# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AssetflowApprovalMixin(models.AbstractModel):
    _name = 'assetflow.approval.mixin'
    _description = 'AssetFlow Approval Mixin'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)
    approver_id = fields.Many2one('res.users', string='Approver', tracking=True)
    approval_date = fields.Datetime(string='Approval Date', tracking=True)
    rejection_reason = fields.Text(string='Rejection Reason', tracking=True)

    def _check_can_approve(self):
        """
        Check if the current user has permission to approve/reject.
        Can be overridden by child models to enforce specific logic.
        """
        if not (self.env.user.has_group('assetflow_base.group_assetflow_department_head') or
                self.env.user.has_group('assetflow_base.group_assetflow_asset_manager')):
            raise UserError(_("You do not have permission to approve or reject this request."))

    def action_submit(self):
        """
        Transitions the record from draft to pending approval.
        """
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft records can be submitted."))
            record.state = 'pending'

    def action_approve(self):
        """
        Approves the record, setting the approver and approval date.
        """
        self._check_can_approve()
        for record in self:
            if record.state != 'pending':
                raise UserError(_("Only pending records can be approved."))
            record.write({
                'state': 'approved',
                'approver_id': self.env.user.id,
                'approval_date': fields.Datetime.now()
            })

    def action_reject(self, reason=None):
        """
        Rejects the record with an optional reason.
        """
        self._check_can_approve()
        for record in self:
            if record.state != 'pending':
                raise UserError(_("Only pending records can be rejected."))
            record.write({
                'state': 'rejected',
                'approver_id': self.env.user.id,
                'approval_date': fields.Datetime.now(),
                'rejection_reason': reason or _("No reason provided.")
            })
