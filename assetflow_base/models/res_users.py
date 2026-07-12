# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    assetflow_department_id = fields.Many2one(
        'assetflow.department', 
        string='Department', 
        help='Department to which this user belongs.'
    )
    employee_code = fields.Char(
        string='Employee Code', 
        help='Unique internal code for the employee.'
    )
    assetflow_role = fields.Char(
        string='AssetFlow Role', 
        compute='_compute_assetflow_role', 
        store=False,
        help='Computed role based on assigned security groups.'
    )

    def _compute_assetflow_role(self):
        """
        Computes a display-only role based on the highest privilege group 
        the user belongs to in AssetFlow.
        """
        for user in self:
            if user.has_group('assetflow_base.group_assetflow_admin'):
                user.assetflow_role = 'Admin'
            elif user.has_group('assetflow_base.group_assetflow_asset_manager'):
                user.assetflow_role = 'Asset Manager'
            elif user.has_group('assetflow_base.group_assetflow_department_head'):
                user.assetflow_role = 'Department Head'
            elif user.has_group('assetflow_base.group_assetflow_employee'):
                user.assetflow_role = 'Employee'
            else:
                user.assetflow_role = 'None'
