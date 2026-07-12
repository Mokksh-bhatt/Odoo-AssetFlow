# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetflowLocation(models.Model):
    _name = 'assetflow.location'
    _description = 'Asset Location'

    name = fields.Char(string='Location Name', required=True)
    code = fields.Char(string='Location Code', required=True)
    department_id = fields.Many2one('assetflow.department', string='Department')
    active = fields.Boolean(default=True)
