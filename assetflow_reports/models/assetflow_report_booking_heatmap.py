from odoo import models, fields, tools

class AssetFlowReportBookingHeatmap(models.Model):
    _name = 'assetflow.report.booking.heatmap'
    _description = 'Booking Heatmap Report'
    _auto = False

    asset_id = fields.Many2one('assetflow.asset', string='Asset', readonly=True)
    day_of_week = fields.Selection([
        ('0', 'Sunday'), ('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'),
        ('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday')
    ], string='Day of Week', readonly=True)
    hour_of_day = fields.Integer(string='Hour of Day', readonly=True)
    booking_count = fields.Integer(string='Booking Count', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    min(b.id) as id,
                    b.asset_id as asset_id,
                    EXTRACT(DOW FROM b.start_datetime)::varchar as day_of_week,
                    EXTRACT(HOUR FROM b.start_datetime)::integer as hour_of_day,
                    count(b.id) as booking_count
                FROM assetflow_booking b
                GROUP BY b.asset_id, EXTRACT(DOW FROM b.start_datetime), EXTRACT(HOUR FROM b.start_datetime)
            )
        """ % (self._table,))
