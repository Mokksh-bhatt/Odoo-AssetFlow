# AssetFlow Technical Architecture

## Addons
- assetflow_base
- assetflow_asset
- assetflow_allocation
- assetflow_booking
- assetflow_maintenance
- assetflow_audit
- assetflow_notification
- assetflow_dashboard
- assetflow_reports

## Core Design
- Modular Odoo addons
- Shared approval mixin
- Shared sequence mixin
- Central asset state machine
- Role-based security
- Record rules
- Cron jobs
- Notification layer
- Reporting layer

## Core Models
- assetflow.department
- assetflow.category
- assetflow.category.field
- assetflow.asset
- assetflow.location
- assetflow.allocation
- assetflow.transfer.request
- assetflow.booking
- assetflow.maintenance.request
- assetflow.audit.cycle
- assetflow.audit.line
- assetflow.audit.discrepancy
- assetflow.notification

## Key Architecture Decisions
- Single _change_state() method for asset lifecycle
- Approval mixin reused across workflows
- mail.thread for chatter
- ir.cron for reminders and overdue detection
- SQL-backed reporting models
- Record rules enforce data visibility
- Odoo-native module structure

## Security
Groups:
- Employee
- Department Head
- Asset Manager
- Admin

Enforced with:
- ir.model.access.csv
- ir.rule
- Server-side validation

## Workflows
- Asset lifecycle
- Allocation & transfer
- Booking
- Maintenance
- Audit cycle
