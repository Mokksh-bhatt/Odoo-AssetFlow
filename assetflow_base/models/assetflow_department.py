# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetflowDepartment(models.Model):
    _name = 'assetflow.department'
    _description = 'AssetFlow Department'
    _inherit = ['mail.thread']
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'

    name = fields.Char(string='Department Name', required=True, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the department without removing it.")
    
    parent_id = fields.Many2one(
        'assetflow.department', 
        string='Parent Department', 
        index=True, 
        ondelete='restrict'
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'assetflow.department', 
        'parent_id', 
        string='Child Departments'
    )
    department_head_id = fields.Many2one(
        'res.users', 
        string='Department Head', 
        tracking=True,
        help="The user designated as the head of this department."
    )

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        """
        Ensures that there are no recursive loops in the department hierarchy.
        """
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive departments.'))
