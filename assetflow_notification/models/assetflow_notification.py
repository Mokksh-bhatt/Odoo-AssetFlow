# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetflowNotification(models.Model):
    _name = 'assetflow.notification'
    _description = 'AssetFlow Notification'
    _order = 'create_date desc, id desc'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade', index=True)
    title = fields.Char(string='Title', required=True)
    body = fields.Text(string='Body')
    
    notification_type = fields.Selection([
        ('asset_assigned', 'Asset Assigned'),
        ('maintenance_approved', 'Maintenance Approved'),
        ('maintenance_rejected', 'Maintenance Rejected'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_reminder', 'Booking Reminder'),
        ('transfer_approved', 'Transfer Approved'),
        ('overdue_return', 'Overdue Return'),
        ('audit_discrepancy', 'Audit Discrepancy')
    ], string='Notification Type', required=True)
    
    res_model = fields.Char(string='Related Document Model')
    res_id = fields.Integer(string='Related Document ID')
    
    is_read = fields.Boolean(string='Read', default=False, index=True)
    create_date = fields.Datetime(string='Created On', default=fields.Datetime.now, readonly=True)

    @api.model
    def create_notification(self, user_id, notification_type, title, body, res_model=None, res_id=None):
        """
        Helper method to create a new notification.
        Intended to be called by other modules.
        """
        if not user_id:
            raise ValidationError(_("A valid user_id is required to create a notification."))
            
        if not notification_type:
            raise ValidationError(_("A valid notification_type is required."))
            
        valid_types = [key for key, val in self._fields['notification_type'].selection]
        if notification_type not in valid_types:
            raise ValidationError(_("Invalid notification_type provided."))
            
        vals = {
            'user_id': user_id,
            'notification_type': notification_type,
            'title': title,
            'body': body,
        }
        
        if res_model and res_id:
            vals['res_model'] = res_model
            vals['res_id'] = res_id
            
        # sudo() ensures system-wide events can deliver notifications 
        # to a user's inbox regardless of the triggerer's permissions
        return self.sudo().create(vals)
        
    def action_mark_as_read(self):
        """Action to mark notifications as read from the UI."""
        for record in self:
            record.is_read = True

    def action_view_related_record(self):
        """Opens the related record form view if res_model and res_id are set."""
        self.ensure_one()
        if self.res_model and self.res_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.res_model,
                'res_id': self.res_id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False
