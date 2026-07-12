# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetflowAssetCategoryValue(models.Model):
    _name = 'assetflow.asset.category.value'
    _description = 'Asset Category Value'

    asset_id = fields.Many2one('assetflow.asset', string='Asset', required=True, ondelete='cascade')
    category_field_id = fields.Many2one('assetflow.category.field', string='Field', required=True)
    value_char = fields.Char(string='Text Value')
    value_integer = fields.Integer(string='Integer Value')
    value_float = fields.Float(string='Float Value')
    value_boolean = fields.Boolean(string='Boolean Value')
    value_date = fields.Date(string='Date Value')
