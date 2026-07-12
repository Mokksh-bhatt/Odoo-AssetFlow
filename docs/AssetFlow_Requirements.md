# AssetFlow Requirements Analysis

This document summarizes the requirements extracted from the problem statement.

## Contents
- Functional Requirements
- Non-Functional Requirements
- Hidden Judging Expectations
- Business Rules
- Edge Cases
- Constraints
- Feature Priorities

> Source: Claude analysis based on the hackathon specification.

### Functional Requirements
- Master data setup (Departments, Categories, Employee Directory)
- Authentication
- Asset Lifecycle Management
- Allocation & Transfer
- Resource Booking
- Maintenance Workflow
- Audit Cycles
- Dashboard & KPIs
- Reports & Analytics
- Notifications & Activity Logs

### Non-Functional Requirements
- Role-based security
- Data integrity
- Scalable modular architecture
- Maintainability
- Auditability
- Usability
- Performance
- PostgreSQL backend
- Extensibility

### Hidden Expectations
- Odoo-native architecture
- Proper state machines
- Strong record rules
- Clean reusable modules
- Distributed Git history
- Ability to justify architectural decisions

### Core Business Rules
- Signup creates Employee only
- Admin assigns roles
- Asset tags are system generated
- No double allocation
- Booking overlap validation
- Maintenance requires approval
- Audit cycles lock on completion
- Overdue detection is automatic

### Important Edge Cases
- Concurrent allocations
- Concurrent transfer requests
- Booking boundary conditions
- Duplicate maintenance requests
- Conflicting audit/asset states
- Department deactivation
- Null expected return dates

### Constraints
- No Accounting/Purchase scope
- PostgreSQL only
- Odoo 18 conventions
- Four fixed roles
- Ten required screens

### Priority
P0
- Authentication
- Asset lifecycle
- Allocation
- Booking
- Maintenance

P1
- Organization setup
- Asset directory
- Dashboard

P2
- Audit
- Notifications

P3
- Reports
- Activity Logs
