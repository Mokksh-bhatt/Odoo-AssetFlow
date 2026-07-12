# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class AssetflowBooking(models.Model):
    _name = 'assetflow.booking'
    _description = 'Asset Booking'
    _order = 'start_datetime desc, id desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True, domain="[('is_bookable', '=', True)]")
    booked_by_id = fields.Many2one('res.users', string='Booked By', default=lambda self: self.env.user, required=True)
    department_id = fields.Many2one('assetflow.department', string='Department', related='booked_by_id.assetflow_department_id', store=True)
    
    start_datetime = fields.Datetime(string='Start Time', required=True)
    end_datetime = fields.Datetime(string='End Time', required=True)
    
    status = fields.Selection([
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='upcoming', required=True, tracking=True)
    
    purpose = fields.Char(string='Purpose', required=True)
    notes = fields.Text(string='Notes')
    reminder_sent = fields.Boolean(string='Reminder Sent', default=False)
    active = fields.Boolean(string='Active', default=True)

    @api.depends('asset_id', 'start_datetime')
    def _compute_name(self):
        for record in self:
            if record.asset_id and record.start_datetime:
                date_str = record.start_datetime.strftime('%Y-%m-%d %H:%M')
                record.name = f"{record.asset_id.name} - {date_str}"
            else:
                record.name = "New Booking"

    @api.constrains('start_datetime', 'end_datetime', 'asset_id', 'status')
    def _check_overlap(self):
        for record in self:
            if not record.start_datetime or not record.end_datetime:
                continue
            
            if record.end_datetime <= record.start_datetime:
                raise ValidationError(_("End time must be strictly after start time."))
                
            if record.asset_id and not record.asset_id.is_bookable:
                raise ValidationError(_("This asset is not marked as bookable."))
                
            if record.status == 'cancelled':
                continue
                
            # Check overlap using strict inequality
            domain = [
                ('asset_id', '=', record.asset_id.id),
                ('id', '!=', record.id),
                ('status', '!=', 'cancelled'),
                ('start_datetime', '<', record.end_datetime),
                ('end_datetime', '>', record.start_datetime)
            ]
            overlapping = self.search(domain, limit=1)
            if overlapping:
                raise ValidationError(_("The asset is already booked for this time slot (Conflict with %s).", overlapping.name))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.status != 'cancelled':
                self.env['assetflow.notification'].create_notification(
                    user_id=record.booked_by_id.id,
                    notification_type='booking_confirmed',
                    title='Booking Confirmed',
                    body=f"Your booking for {record.asset_id.name} is confirmed for {record.start_datetime}.",
                    res_model='assetflow.booking',
                    res_id=record.id
                )
        return records

    def action_cancel(self):
        for record in self:
            if record.status in ('completed', 'cancelled'):
                raise ValidationError(_("Cannot cancel a completed or already cancelled booking."))
            record.status = 'cancelled'
            self.env['assetflow.notification'].create_notification(
                user_id=record.booked_by_id.id,
                notification_type='booking_cancelled',
                title='Booking Cancelled',
                body=f"Your booking for {record.asset_id.name} has been cancelled.",
                res_model='assetflow.booking',
                res_id=record.id
            )

    def action_complete(self):
        for record in self:
            record.status = 'completed'

    @api.model
    def _update_booking_status(self):
        now = fields.Datetime.now()
        # Upcoming -> Ongoing
        upcoming = self.search([
            ('status', '=', 'upcoming'),
            ('start_datetime', '<=', now),
            ('end_datetime', '>', now)
        ])
        upcoming.write({'status': 'ongoing'})
        
        # Ongoing -> Completed
        ongoing = self.search([
            ('status', 'in', ['upcoming', 'ongoing']),
            ('end_datetime', '<=', now)
        ])
        ongoing.write({'status': 'completed'})

    @api.model
    def _send_reminders(self):
        now = fields.Datetime.now()
        warning_time = now + timedelta(minutes=15)
        upcoming = self.search([
            ('status', '=', 'upcoming'),
            ('reminder_sent', '=', False),
            ('start_datetime', '<=', warning_time),
            ('start_datetime', '>', now)
        ])
        for record in upcoming:
            self.env['assetflow.notification'].create_notification(
                user_id=record.booked_by_id.id,
                notification_type='booking_reminder',
                title='Booking Reminder',
                body=f"Your booking for {record.asset_id.name} is starting in 15 minutes.",
                res_model='assetflow.booking',
                res_id=record.id
            )
            record.reminder_sent = True
