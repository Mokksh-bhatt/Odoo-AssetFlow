from odoo import models, fields, tools

class AssetFlowReportUtilization(models.Model):
    _name = 'assetflow.report.asset.utilization'
    _description = 'Asset Utilization Report'
    _auto = False

    asset_id = fields.Many2one('assetflow.asset', string='Asset', readonly=True)
    category_id = fields.Many2one('assetflow.category', string='Category', readonly=True)
    allocation_days = fields.Integer(string='Days Allocated', readonly=True)
    idle_days = fields.Integer(string='Days Idle', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    a.id as id,
                    a.id as asset_id,
                    a.category_id as category_id,
                    COALESCE((
                        SELECT SUM(DATE(COALESCE(al.actual_return_date, CURRENT_TIMESTAMP)) - DATE(al.allocation_date))
                        FROM assetflow_allocation al
                        WHERE al.asset_id = a.id
                    ), 0) as allocation_days,
                    COALESCE(CURRENT_DATE - DATE(a.create_date), 0) - COALESCE((
                        SELECT SUM(DATE(COALESCE(al.actual_return_date, CURRENT_TIMESTAMP)) - DATE(al.allocation_date))
                        FROM assetflow_allocation al
                        WHERE al.asset_id = a.id
                    ), 0) as idle_days
                FROM assetflow_asset a
            )
        """ % (self._table,))
