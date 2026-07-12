/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class AssetFlowDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            data: {
                total_assets: 0,
                available_assets: 0,
                allocated_assets: 0,
                maintenance_assets: 0,
                total_bookings: 0,
                open_maintenance: 0
            }
        });

        onWillStart(async () => {
            this.state.data = await this.orm.call("assetflow.asset", "get_dashboard_data", []);
        });
    }

    openAssets(state = null) {
        let domain = [];
        if (state) {
            domain = [['state', '=', state]];
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Assets",
            res_model: "assetflow.asset",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            target: "current",
        });
    }
}
AssetFlowDashboard.template = "assetflow_dashboard.Dashboard";

registry.category("actions").add("assetflow_dashboard_action", AssetFlowDashboard);
