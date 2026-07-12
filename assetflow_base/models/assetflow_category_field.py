# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetflowCategoryField(models.Model):
    _name = 'assetflow.category.field'
    _description = 'AssetFlow Category Field'

    name = fields.Char(string='Field Name', required=True)
    category_id = fields.Many2one(
        'assetflow.category', 
        string='Category', 
        required=True, 
        ondelete='cascade'
    )
    field_type = fields.Selection([
        ('char', 'Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Checkbox'),
        ('date', 'Date')
    ], string='Field Type', required=True, default='char')
    required = fields.Boolean(
        string='Required', 
        default=False, 
        help="Check this if this field is mandatory for assets in this category."
    )

    _sql_constraints = [
        (
            'name_category_uniq', 
            'unique (name, category_id)', 
            'The field name must be unique per category!'
        )
    ]
