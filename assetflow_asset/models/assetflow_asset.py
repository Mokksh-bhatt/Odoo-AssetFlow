# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetflowAsset(models.Model):
    _name = 'assetflow.asset'
    _description = 'Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    asset_tag = fields.Char(string='Asset Tag', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    serial_number = fields.Char(string='Serial Number', index=True)
    category_id = fields.Many2one('assetflow.category', string='Category', required=True)
    
    state = fields.Selection([
        ('available', 'Available'),
        ('allocated', 'Allocated'),
        ('maintenance', 'Maintenance'),
        ('lost', 'Lost'),
        ('disposed', 'Disposed')
    ], string='State', default='available', required=True, tracking=True)
    
    current_holder_employee_id = fields.Many2one('res.users', string='Current Holder')
    current_holder_department_id = fields.Many2one('assetflow.department', string='Current Department')
    location_id = fields.Many2one('assetflow.location', string='Location')
    is_bookable = fields.Boolean(string='Is Bookable', default=False)
    
    qr_code = fields.Char(string='QR Code')
    condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('broken', 'Broken')
    ], string='Condition', default='good')
    acquisition_date = fields.Date(string='Acquisition Date')
    acquisition_cost = fields.Float(string='Acquisition Cost')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id if self.env.company else False)
    
    state_log_ids = fields.One2many('assetflow.asset.state.log', 'asset_id', string='State Log')
    category_value_ids = fields.One2many('assetflow.asset.category.value', 'asset_id', string='Dynamic Attributes')
    active = fields.Boolean(default=True)
    image = fields.Binary(string='Image')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('asset_tag', _('New')) == _('New'):
                vals['asset_tag'] = self.env['ir.sequence'].next_by_code('assetflow.asset') or _('New')
        return super().create(vals_list)

    def _change_state(self, new_state, reason=None):
        for record in self:
            if record.state == new_state:
                continue
            
            # Prevent illegal transitions (simplified for this exercise)
            if record.state == 'disposed':
                raise ValidationError(_("Cannot change state of a disposed asset."))
                
            old_state = record.state
            record.state = new_state
            
            self.env['assetflow.asset.state.log'].create({
                'asset_id': record.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason,
                'changed_by': self.env.user.id
            })
