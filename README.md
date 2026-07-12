# 🏢 Odoo AssetFlow 

<p align="center">
  <strong>A comprehensive, modular Asset Management, Tracking, and Maintenance suite built for Odoo ERP.</strong><br>
  <em>Developed for the Odoo Hackathon</em>
</p>

---

## 👥 Contributors
- **Mokksh**
- **Meet Sharma**

---

## 🚀 About The Project

**AssetFlow** is a complete end-to-end asset lifecycle management solution designed directly within the Odoo ecosystem. It eliminates spreadsheets and disconnected tools by centralizing asset tracking, allocation, maintenance scheduling, and auditing into a single, cohesive workflow.

By separating the system into highly decoupled modules, businesses can install only the exact features they need—scaling from simple inventory tracking to advanced enterprise resource booking and maintenance auditing.

---

## 🧩 Module Architecture (Project Structure)

The project is heavily modularized to follow Odoo best practices. The addons are located in the root directory (and the `addons/` folder).

| Module Name | Purpose |
|-------------|---------|
| ⚙️ **`assetflow_base`** | Core configurations, security groups, and shared utilities. Must be installed first. |
| 💻 **`assetflow_asset`** | The primary asset registry (equipment, hardware, furniture). Handles basic CRUD and statuses. |
| 🔔 **`assetflow_notification`** | Automated email and UI alerts for asset status changes, upcoming maintenance, and overdue returns. |
| 📅 **`assetflow_booking`** | Allows employees to request and reserve temporary assets (like projectors, laptops, or vehicles) for specific dates. |
| 🧑‍💻 **`assetflow_allocation`** | Permanent or long-term assignment of assets to specific employees or departments. |
| 🔧 **`assetflow_maintenance`** | Ticketing system for repairs, preventive maintenance scheduling, and vendor tracking. |
| 📋 **`assetflow_audit`** | Periodic physical verification and compliance logging. Ensures digital records match physical reality. |
| 📊 **`assetflow_dashboard`** | A beautiful, centralized Kanban/Graph view for admins to monitor asset health and allocation metrics at a glance. |
| 📑 **`assetflow_reports`** | PDF and Excel report generation for audits, financial tracking, and depreciation summaries. |

---

## 🛠️ Installation & Setup

### Recommended Generation & Installation Order
To prevent dependency errors during installation in Odoo, please install the modules in the following strict order:

1. `assetflow_base`
2. `assetflow_asset`
3. `assetflow_notification`
4. `assetflow_booking`
5. `assetflow_allocation`
6. `assetflow_maintenance`
7. `assetflow_audit`
8. `assetflow_dashboard`
9. `assetflow_reports`

### Running the Environment
1. Clone this repository to your local machine.
2. Ensure you have Odoo installed and running.
3. Add the project directory to your `odoo.conf` file under the `addons_path` setting.
   - Example: `addons_path = /usr/lib/python3/dist-packages/odoo/addons, /path/to/Odoo-AssetFlow`
4. Restart your Odoo server.
5. Log in as an Administrator, activate **Developer Mode**, and click **Update Apps List**.
6. Search for `assetflow` and install the modules in the order listed above.

---

## 🧪 Testing & Workflows
This repository includes helpful automation scripts for testing and deployment:
- `test_workflow.py`: A Python script for testing automated flows and module dependencies.
- `update_odoo.ps1`: A PowerShell script to quickly restart Odoo and force-update the modules during development.
- `odoo_modified.conf`: A template configuration file specifically tailored for this project.

---

## 📄 Documentation
Detailed technical requirements, architectural blueprints, and our future roadmap can be found inside the `docs/` folder.
