# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetflowAssetStateLog(models.Model):
    _name = 'assetflow.asset.state.log'
    _description = 'Asset State Log'
    _order = 'create_date desc'

    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True, ondelete='cascade')
    old_state = fields.Char(string='Old State', required=True)
    new_state = fields.Char(string='New State', required=True)
    reason = fields.Text(string='Reason')
    changed_by = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user)
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now)
