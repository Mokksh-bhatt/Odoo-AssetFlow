# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetflowCategory(models.Model):
    _name = 'assetflow.category'
    _description = 'AssetFlow Asset Category'
    _inherit = ['mail.thread']

    name = fields.Char(string='Category Name', required=True, tracking=True)
    active = fields.Boolean(default=True, help="Set to false to hide the category without removing it.")
    field_ids = fields.One2many(
        'assetflow.category.field', 
        'category_id', 
        string='Custom Fields',
        help="Dynamic fields applied to assets of this category."
    )
