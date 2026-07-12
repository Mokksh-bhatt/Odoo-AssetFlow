# AssetFlow — Implementation Roadmap

## Parallelization strategy (read this first)

The 9 modules fall into 4 dependency tiers. **Team assignment is built around these tiers, not around arbitrary feature splits**, because Odoo addon folders are natural git-conflict boundaries — as long as two developers don't edit the same folder, merge conflicts are near-zero regardless of how much code they write.

```
Tier 0 (blocking, solo/mob)   assetflow_base
Tier 1 (parallel, 2 devs)     assetflow_asset        assetflow_notification
Tier 2 (parallel, 4 devs)     assetflow_allocation   assetflow_booking   assetflow_maintenance   assetflow_audit
Tier 3 (parallel, 2 devs)     assetflow_dashboard    assetflow_reports
```

**Key design decision:** `assetflow_notification` depends only on `assetflow_base`, not the other way around, and every Tier 2 module depends on it. This means notification-firing logic (`_notify_user(...)`) is available to every domain module from day one, instead of bolting notifications on at the end.

### Team assignment (4 developers)

| Developer | Owns | Rationale |
|---|---|---|
| **Dev 1** | `assetflow_base` → `assetflow_dashboard` | Foundation owner starts first (bottleneck), finishes last (needs everything for the KPI aggregation) |
| **Dev 2** | `assetflow_asset` → `assetflow_reports` | Asset owner understands the state machine best, best placed to build SQL-view reports on top of it |
| **Dev 3** | `assetflow_allocation` + `assetflow_booking` | "Who has it / who's using it" pair — related domain, shares the asset-conflict mental model |
| **Dev 4** | `assetflow_maintenance` + `assetflow_audit` | "Condition & verification" pair — both are approval-gated workflows on the same mixin |

`assetflow_notification` is small (one model, no complex workflow) — build it as a **Day 1 mob session** immediately after `assetflow_base`'s field contract is agreed, with whichever dev finishes their Tier-0 contribution first picking it up. Budget ~half a day.

### De-conflicting Tier 0

Don't let one developer build `assetflow_base` alone while three others wait. Instead:
1. **Hour 1 (all 4, whiteboard/doc, no code):** Agree the exact field names on `assetflow.department`, `assetflow.category`, `res.users` extension, and — critically — the exact field names on `assetflow.asset` (`asset_tag`, `state`, `category_id`, `current_holder_employee_id`, `current_holder_department_id`) even though `assetflow.asset` isn't Tier 0. This is the "contract." Write it down.
2. **Dev 1** builds `assetflow_base` for real, against the agreed contract.
3. **Devs 2–4** scaffold their own modules' models/views against the *agreed field names* on a local branch, using stub/mock data — they do NOT wait for `assetflow_base` to merge. When it merges, they rebase and it should mostly just work, because they coded against the contract, not against Dev 1's actual code.

### Conventions to enforce across all 4 developers (prevents 90% of conflicts)

- External IDs are always `module_name.descriptive_id` (e.g. `assetflow_allocation.action_transfer_request`) — never a bare `id="action_1"`.
- Each module owns its own `security/ir.model.access.csv` — never edit another module's.
- Each module adds its **own top-level or second-level menu item**, parented to `assetflow_base.menu_assetflow_root` (defined once, in base, and never touched again). No module edits another module's menu XML.
- Each module ships its own scoped demo data file (`data/xxx_demo.xml`) — never a shared demo file multiple devs touch.
- State-changing logic on `assetflow.asset` always goes through the single `_change_state()` method defined in `assetflow_asset` — no other module writes `state` directly.

---

## Module 1 — assetflow_base

**1. Objective**
Provide the shared foundation every other module depends on: departments, asset categories, security groups, the employee/role model, and two reusable mixins (approval workflow, sequencing).

**2. Files to create**
```
assetflow_base/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── assetflow_department.py
│   ├── assetflow_category.py
│   ├── assetflow_category_field.py
│   ├── res_users.py
│   ├── approval_mixin.py
│   └── sequence_mixin.py
├── security/
│   ├── security_groups.xml
│   ├── ir.model.access.csv
│   └── department_category_rules.xml
├── views/
│   ├── department_views.xml
│   ├── category_views.xml
│   ├── res_users_views.xml
│   └── assetflow_menus.xml
├── data/
│   └── assetflow_sequences.xml
└── static/description/icon.png
```

**3. Python models**
- `assetflow.department` — hierarchy via `parent_id`/`child_ids`, `department_head_id`, `active`
- `assetflow.category` — with `field_ids` (One2many)
- `assetflow.category.field` — dynamic per-category attribute definitions
- `res.users` (`_inherit`) — adds `assetflow_department_id`, `employee_code`, display-only `assetflow_role`
- `assetflow.approval.mixin` (AbstractModel) — `state`, `approver_id`, `approval_date`, `rejection_reason`, `action_approve()`, `action_reject()`
- `assetflow.sequence.mixin` (AbstractModel) — sequence lookup helper

**4. XML views**
Department tree/form (with hierarchy), Category tree/form (inline `field_ids` editable list), `res.users` form inherited to add an "AssetFlow" tab (department, employee code, role — read-only unless `group_assetflow_admin`), root menu `menu_assetflow_root` + Organization Setup menu with 3 sub-items (Departments, Categories, Employee Directory).

**5. Security files**
`security_groups.xml`: `group_assetflow_employee`, `group_assetflow_department_head` (implies employee), `group_assetflow_asset_manager` (implies employee), `group_assetflow_admin` (implies both). `ir.model.access.csv`: employee=read on department/category, admin=full CRUD. `department_category_rules.xml`: write/unlink restricted to admin at the record-rule level too (defense in depth beyond model access).

**6. Dependencies**
`base`, `mail`

**7. Estimated implementation order**
**First — before any other module branches meaningfully diverge.** Contract agreed Hour 1, built Day 1.

**8. Acceptance criteria**
- Signup creates a user with only `group_assetflow_employee`, no role picker anywhere in the signup flow
- Only the Employee Directory tab (admin-only) can change a user's group
- Attempting to grant oneself `group_assetflow_admin` via direct RPC fails (test this — don't just hide the button)
- Deactivating a department doesn't delete it or orphan its children silently
- Category custom fields save per-category and are retrievable

**9. Common mistakes**
- Using `implied_ids` incorrectly so Department Head doesn't inherit Employee's base permissions
- Role-assignment logic living in the signup controller "just this once" instead of being structurally impossible there
- Missing `active` field default → deactivate ends up hard-deleting via cascade
- Two developers independently creating `menu_assetflow_root` — must be defined exactly once, here, and never redefined

**10. Suggested Git branch name**
`feature/assetflow-base`

---

## Module 2 — assetflow_asset

**1. Objective**
Central asset registry with the full lifecycle state machine and per-asset history.

**2. Files to create**
```
assetflow_asset/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── assetflow_location.py
│   ├── assetflow_asset.py
│   ├── assetflow_asset_state_log.py
│   └── assetflow_asset_category_value.py
├── security/
│   ├── ir.model.access.csv
│   └── asset_rules.xml
├── views/
│   ├── asset_views.xml
│   ├── location_views.xml
│   └── asset_menus.xml
└── data/
    └── asset_sequence.xml
```

**3. Python models**
- `assetflow.location` — `name`, `code`, `department_id`
- `assetflow.asset` — full field set from the architecture doc; the critical method is `_change_state(new_state, reason=None)`, the **single enforcement point** for the transition matrix, called by every other module instead of `write({'state': ...})` directly
- `assetflow.asset.state.log` — append-only, written inside `_change_state()`
- `assetflow.asset.category.value` — stores dynamic category-field values per asset

**4. XML views**
Form with `statusbar` widget on `state`, tabs for Allocation History / Maintenance History (empty `One2many` lists until Tier 2 lands — this is fine, they render correctly regardless of module install order), Kanban grouped by state, tree with decorations for overdue-adjacent flags, search view with tag/serial/QR/category/status/department/location filters, Locations tree/form, menu item "Assets" under the root menu.

**5. Security files**
`ir.model.access.csv`: employee=read, asset_manager/admin=full CRUD (no unlink for anyone below admin — retire/dispose instead of deleting). `asset_rules.xml`: employee sees assets currently held by them/their department plus anything `is_bookable=True`; asset_manager/admin unrestricted.

**6. Dependencies**
`assetflow_base`

**7. Estimated implementation order**
**Second**, immediately after base's contract is fixed. This is the highest-leverage module — everything else reads or writes through it.

**8. Acceptance criteria**
- Registering an asset auto-assigns `AF-0001` style tag, gapless per-sequence
- Attempting an illegal transition (e.g. `disposed → available`) raises a validation error, not a silent no-op
- Search/filter works on every listed field
- History tabs render without error even with zero related records

**9. Common mistakes**
- Any other module bypassing `_change_state()` and writing `state` directly — this single mistake silently breaks the transition matrix and is easy to miss in review
- QR code left as a plain unindexed `Char` with no generation/uniqueness logic
- Forgetting `index=True` on `asset_tag` and `serial_number` — search becomes slow once demo data grows
- Category dynamic-field values not validated against `required=True` definitions from `assetflow.category.field`

**10. Suggested Git branch name**
`feature/assetflow-asset`

---

## Module 3 — assetflow_notification

**1. Objective**
Thin, low-level notification service every domain module can call into, plus a personal notification feed UI.

**2. Files to create**
```
assetflow_notification/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── assetflow_notification.py
├── security/
│   ├── ir.model.access.csv
│   └── notification_rules.xml
└── views/
    ├── notification_views.xml
    └── notification_menus.xml
```

**3. Python models**
- `assetflow.notification` — `user_id`, `title`, `body`, `notification_type` (Selection matching the spec's exact list), `res_model`, `res_id`, `is_read`, `create_date`
- One public helper method, e.g. `create_notification(user_id, notification_type, title, body, res_model=None, res_id=None)`, meant to be called from every other module

**4. XML views**
List view (unread bolded via `decoration-bf`), a bell-icon-style kanban or simple list in the Notifications menu, filter for Unread/All.

**5. Security files**
`ir.model.access.csv`: every role gets create (system-generated, but keep it open for now)/read on their own records. `notification_rules.xml`: **hard rule** `user_id = uid`, no exceptions — even admin only sees their own notifications here (it's a personal inbox, not a shared mailbox).

**6. Dependencies**
`assetflow_base`

**7. Estimated implementation order**
**Third, in parallel with `assetflow_asset`.** Small enough to build in half a day — good candidate for whichever developer clears their Tier-0 contribution first.

**8. Acceptance criteria**
- Calling the helper method from a Python shell creates a record visible only to the target user
- A user cannot query another user's notifications via the list view, search, or direct RPC
- Marking as read persists and filters correctly

**9. Common mistakes**
- Building this as a "big" event system (message bus, pub/sub) — over-engineering for a hackathon; a plain model + helper method is enough
- Forgetting the record rule and relying only on a default domain in the view (trivially bypassable via RPC)
- Not exposing `res_model`/`res_id` as a clickable link back to the source record — small UX detail that scores well in judging

**10. Suggested Git branch name**
`feature/assetflow-notification`

---

## Module 4 — assetflow_allocation

**1. Objective**
Allocation of assets to employees/departments with hard conflict prevention, plus the transfer-request remedy workflow.

**2. Files to create**
```
assetflow_allocation/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── assetflow_allocation.py
│   └── assetflow_transfer_request.py
├── security/
│   ├── ir.model.access.csv
│   └── allocation_rules.xml
└── views/
    ├── allocation_views.xml
    ├── transfer_request_views.xml
    └── allocation_menus.xml
```

**3. Python models**
- `assetflow.allocation` — conflict rule enforced via `@api.constrains` **and** a partial unique SQL index (`WHERE status = 'active'`) on `asset_id` for concurrency safety
- `assetflow.transfer.request` (inherits `assetflow_base`'s `approval.mixin`) — `action_approve()` override creates a new `assetflow.allocation`, closes the old one, updates the asset's denormalized holder fields

**4. XML views**
Allocation form/tree with a "Return" button (opens a wizard-like inline form for condition notes), Transfer Request form with `statusbar` + Approve/Reject buttons (visible only to Asset Manager/Department Head), menu items under "Allocation & Transfers".

**5. Security files**
`ir.model.access.csv`: employee=create own transfer requests + read own allocations; asset_manager=full CRUD. `allocation_rules.xml`: employee sees allocations where they're the holder or requester; department_head sees their department (including children); asset_manager/admin unrestricted.

**6. Dependencies**
`assetflow_asset`, `assetflow_notification`

**7. Estimated implementation order**
**Fourth, in parallel with booking, maintenance, and audit** (Tier 2).

**8. Acceptance criteria**
- Allocating an already-held asset is blocked, the error names the current holder, and a "Request Transfer" action is offered instead of a dead end
- Approving a transfer atomically closes the old allocation and opens a new one — no window where the asset shows no holder or two holders
- Returning an asset requires condition notes and flips the asset back to Available
- `assetflow.notification` fires on: Asset Assigned, Transfer Approved

**9. Common mistakes**
- Relying only on the Python `@api.constrains` for the no-double-allocation rule — under concurrent requests (a real risk during a live demo where two people click at once) this needs the DB-level partial unique index too
- Forgetting to sync `assetflow.asset.current_holder_*` fields on both allocate and return, leaving the asset list showing a stale holder
- Letting the *requester* also be the *approver* on their own transfer request

**10. Suggested Git branch name**
`feature/assetflow-allocation`

---

## Module 5 — assetflow_booking

**1. Objective**
Time-slot booking of shared/bookable assets with strict overlap prevention.

**2. Files to create**
```
assetflow_booking/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── assetflow_booking.py
├── security/
│   ├── ir.model.access.csv
│   └── booking_rules.xml
├── views/
│   ├── booking_views.xml
│   └── booking_menus.xml
└── data/
    └── booking_cron.xml
```

**3. Python models**
- `assetflow.booking` — `start_datetime`, `end_datetime`, `status`, overlap check via `@api.constrains` using **strict** inequality (`start < other.end AND end > other.start`) so back-to-back bookings are valid
- Two `ir.cron` jobs defined in `data/booking_cron.xml`: status auto-transition (upcoming→ongoing→completed) and pre-slot reminders

**4. XML views**
Calendar view (colored by status), form, tree, menu items under "Bookings" (Booking Calendar, My Bookings).

**5. Security files**
`ir.model.access.csv`: all employees create/read; `booking_rules.xml`: employees can write/cancel only their own bookings; department_head/asset_manager can cancel any.

**6. Dependencies**
`assetflow_asset`, `assetflow_notification`

**7. Estimated implementation order**
**Fourth, in parallel with allocation, maintenance, and audit** (Tier 2). Structurally simplest of the four — no approval workflow, just a constraint check — so it's a reasonable pick for whichever dev is least familiar with the `approval.mixin` pattern.

**8. Acceptance criteria**
- Exact boundary case from the spec: Room B2 booked 9:00–10:00 → 9:30–10:30 rejected, 10:00–11:00 accepted
- Cron correctly flips status without manual intervention (verify with a demo booking timed a few minutes out)
- Cancelling a booking immediately frees the slot for a new overlapping request
- Reminder notification fires once (not repeatedly) before the slot starts

**9. Common mistakes**
- Using `<=`/`>=` instead of strict `<`/`>` in the overlap query — this incorrectly blocks the valid back-to-back case that's explicitly called out as a test case in the problem statement
- Comparing `Datetime` fields without accounting for Odoo's UTC storage, causing off-by-timezone false positives/negatives
- Cron interval too coarse (e.g. hourly) making status changes visibly stale during a live demo — use 5–10 minutes
- Missing `reminder_sent` flag, causing duplicate reminder notifications on every cron run

**10. Suggested Git branch name**
`feature/assetflow-booking`

---

## Module 6 — assetflow_maintenance

**1. Objective**
Route maintenance requests through mandatory approval before any repair work begins, syncing asset state automatically.

**2. Files to create**
```
assetflow_maintenance/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── assetflow_maintenance_request.py
├── security/
│   ├── ir.model.access.csv
│   └── maintenance_rules.xml
└── views/
    ├── maintenance_views.xml
    └── maintenance_menus.xml
```

**3. Python models**
- `assetflow.maintenance.request` (inherits `approval.mixin`, extended with technician sub-states: `technician_assigned`, `in_progress`, `resolved`) — captures `prior_asset_state` at creation so resolution/rejection can revert correctly instead of hardcoding `available`

**4. XML views**
Kanban board grouped by state (this doubles as a literal visual workflow board — good demo material), form with `statusbar`, tree, menu item under "Maintenance".

**5. Security files**
`ir.model.access.csv`: employee=create/read own; asset_manager=full CRUD + approve. `maintenance_rules.xml`: employee sees only requests they raised; asset_manager/admin unrestricted.

**6. Dependencies**
`assetflow_asset`, `assetflow_notification`

**7. Estimated implementation order**
**Fourth, in parallel** (Tier 2).

**8. Acceptance criteria**
- Raising a request does not change the asset's state
- Approval (and only approval) flips the asset to `maintenance`
- Resolution reverts the asset to its actual prior state (test with an asset that was `allocated`, not just `available`, before the request)
- A rejected request leaves the asset state untouched
- Requester cannot approve their own request (server-side, not just hidden button)

**9. Common mistakes**
- Hardcoding `resolved → available`, breaking the case where the asset was allocated when the fault was reported
- Allowing a second open maintenance request on an asset that's already `Under Maintenance`
- Approval button visible-but-non-functional for non-Asset-Managers because the check only lives in the view's `groups` attribute and not in the mixin's `action_approve()` method

**10. Suggested Git branch name**
`feature/assetflow-maintenance`

---

## Module 7 — assetflow_audit

**1. Objective**
Structured, scoped audit cycles with assigned auditors and auto-generated discrepancy reports.

**2. Files to create**
```
assetflow_audit/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── assetflow_audit_cycle.py
│   ├── assetflow_audit_line.py
│   └── assetflow_audit_discrepancy.py
├── wizards/
│   ├── __init__.py
│   └── audit_line_generate_wizard.py
├── security/
│   ├── ir.model.access.csv
│   └── audit_rules.xml
└── views/
    ├── audit_cycle_views.xml
    ├── audit_line_views.xml
    └── audit_menus.xml
```

**3. Python models**
- `assetflow.audit.cycle` — `scope_type`, `department_id`/`location_id`, `date_from`/`date_to`, `auditor_ids` (Many2many), `state` (draft/in_progress/closed)
- `assetflow.audit.line` — one per in-scope asset, `result` (pending/verified/missing/damaged)
- `assetflow.audit.discrepancy` (repurposes `approval.mixin` as open/resolved) — auto-created when a line's `result` is written as missing/damaged
- `assetflow.audit.line.generate.wizard` (TransientModel) — bulk-populates lines for all assets matching the cycle's scope when it moves to `in_progress`

**4. XML views**
Cycle form with `statusbar`, embedded line list (editable `result` field with a select widget), wizard view, discrepancy list, menu item under "Audits".

**5. Security files**
`ir.model.access.csv`: asset_manager/admin=full CRUD; regular employees have no access. `audit_rules.xml`: an auditor sees only cycles/lines where they're in `auditor_ids`; department head sees their department's cycles read-only.

**6. Dependencies**
`assetflow_asset`, `assetflow_notification`

**7. Estimated implementation order**
**Fourth, in parallel** (Tier 2) — lowest UI-centrality of the four, good pairing with maintenance for one developer since both reuse `approval.mixin`.

**8. Acceptance criteria**
- Cycle cannot move to `in_progress` without ≥1 auditor and a valid scope + date range
- Auditors can only mark lines within cycles they're assigned to
- Marking a line missing/damaged auto-creates exactly one discrepancy record (no duplicates on re-save)
- Closing the cycle locks all lines from further edits and sets confirmed-missing assets to `lost`

**9. Common mistakes**
- Allowing writes to lines after `state = 'closed'` — needs an explicit guard in `write()`, not just a readonly view attribute
- Generating lines for every asset in the system instead of respecting `scope_type`/`department_id`/`location_id`
- Re-saving a line with the same `result` value creating a second discrepancy record — guard with a check for an existing open discrepancy before creating a new one

**10. Suggested Git branch name**
`feature/assetflow-audit`

---

## Module 8 — assetflow_dashboard

**1. Objective**
Real-time KPI snapshot and quick actions — the first screen every role sees.

**2. Files to create**
```
assetflow_dashboard/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── dashboard_controller.py
├── static/src/
│   ├── js/dashboard.js
│   └── xml/dashboard_templates.xml
├── security/
│   └── ir.model.access.csv   (if any computed models are added)
└── views/
    └── dashboard_menus.xml
```

**3. Python models**
No new persistent models. A controller/model method aggregating counts from `assetflow.asset`, `assetflow.booking`, `assetflow.maintenance.request`, `assetflow.allocation` — e.g. a single `get_dashboard_data()` method returning a dict for the OWL client action to consume.

**4. XML views**
An OWL client action (`ir.actions.client`) as the "Dashboard" menu target — KPI cards, overdue-returns list styled distinctly from upcoming, three quick-action buttons routing to the Register Asset / Book Resource / Raise Maintenance Request forms in their respective modules.

**5. Security files**
No new access rules needed if it only reads through existing models' own record rules (the dashboard should respect the same row-level visibility as the underlying models — an employee's dashboard only counts what they can already see).

**6. Dependencies**
`assetflow_asset`, `assetflow_allocation`, `assetflow_booking`, `assetflow_maintenance`, `assetflow_notification`

**7. Estimated implementation order**
**Last (Tier 3).** Needs all Tier 2 modules installed to have real data to aggregate.

**8. Acceptance criteria**
- All 6 KPI cards show correct live counts
- Overdue returns are visually distinct from upcoming ones, not just filtered
- Quick actions open the correct pre-configured forms in one click
- Dashboard respects each role's row-level visibility (an employee doesn't see org-wide counts)

**9. Common mistakes**
- Aggregating with `search_count` calls that ignore the underlying models' record rules (accidentally showing org-wide numbers to an Employee)
- Building the dashboard as a plain window action with a pivot view instead of a proper client action — technically easier but visually much weaker for a demo
- Not caching/optimizing the aggregation query, causing a visible lag every time the dashboard opens once demo data grows

**10. Suggested Git branch name**
`feature/assetflow-dashboard`

---

## Module 9 — assetflow_reports

**1. Objective**
Operational analytics: utilization trends, maintenance frequency, department summaries, booking heatmap, exports.

**2. Files to create**
```
assetflow_reports/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── assetflow_report_utilization.py   (SQL-view backed, _auto = False)
│   └── assetflow_report_booking_heatmap.py (SQL-view backed, _auto = False)
├── security/
│   └── ir.model.access.csv
└── views/
    ├── report_views.xml   (graph/pivot on asset, booking, maintenance)
    └── report_menus.xml
```

**3. Python models**
- `assetflow.report.asset.utilization` — `_auto = False`, backed by `init()` creating a PostgreSQL view aggregating allocation-days vs idle-days per asset
- `assetflow.report.booking.heatmap` — `_auto = False`, aggregates booking counts by day-of-week/hour

Everything else (maintenance frequency, department allocation summary) is a `graph`/`pivot` view directly on the existing `assetflow.maintenance.request` / `assetflow.allocation` models — no new model needed.

**4. XML views**
Graph and pivot `ir.actions.act_window` entries on Asset/Booking/Maintenance/Allocation, plus dedicated actions for the two SQL-view models, menu items under "Reports". Export uses Odoo's native list-view XLSX/CSV button — no custom export code needed.

**5. Security files**
`ir.model.access.csv`: read-only for department_head/asset_manager/admin; no employee access (reports are a managerial screen per the spec's role list).

**6. Dependencies**
`assetflow_asset`, `assetflow_allocation`, `assetflow_booking`, `assetflow_maintenance`, `assetflow_audit`

**7. Estimated implementation order**
**Last (Tier 3), alongside dashboard.** Needs every Tier 2 module's schema finalized since the SQL views join across them.

**8. Acceptance criteria**
- Utilization report correctly distinguishes most-used vs idle assets
- Booking heatmap accurately reflects peak windows against seeded demo data
- Every report is exportable via the native list export
- SQL views don't break if a referenced table is empty (return zero rows, not an error)

**9. Common mistakes**
- Writing the SQL view once and never re-running `init()` after a later schema change in Tier 2 modules — stale view definition
- Building custom Python aggregation loops instead of using Odoo's built-in `graph`/`pivot` view types for the simple cases — much more code for no benefit
- Forgetting `_auto = False` on the SQL-view-backed models, which makes Odoo try to create a real table over your view definition

**10. Suggested Git branch name**
`feature/assetflow-reports`

---

## Recommended order for AI-assisted code generation (e.g. Antigravity)

A single AI coding agent generating modules sequentially should **not** follow the human parallel-team order — it should follow strict dependency order, and within each tier, order modules so the agent reinforces one pattern at a time rather than jumping between unrelated patterns (this measurably reduces inconsistency/hallucination across a long session).

1. **`assetflow_base`** — must exist before anything else can be generated meaningfully. Establishes the field contract, the two mixins, and the security group hierarchy that every later prompt will reference.
2. **`assetflow_asset`** — the single most-referenced model in the whole system. Generate and validate this thoroughly (including the `_change_state()` transition matrix) before moving on, since every later module's prompts will need to cite its exact field names.
3. **`assetflow_notification`** — small and low-risk. Generating it right after asset establishes the `create_notification()` calling convention early, so every subsequent module's prompts can say "call the existing notification helper" instead of reinventing the pattern each time.
4. **`assetflow_booking`** — generate before the approval-workflow modules. It has no `approval.mixin` dependency, so it exercises a *different* pattern (constraint-based validation) in isolation, before the agent's context gets loaded up with mixin-based state machines.
5. **`assetflow_allocation`** — the first `approval.mixin` consumer. This establishes the approve/reject pattern the agent will repeat in steps 6 and 7.
6. **`assetflow_maintenance`** — reuses the exact pattern from step 5 with technician sub-states added. Generating it immediately after allocation, while that pattern is still fresh in context, keeps the two implementations consistent with each other.
7. **`assetflow_audit`** — the most complex `approval.mixin` consumer (cycle + line + discrepancy, three related models). Saved for last among the domain modules since it benefits most from the agent having already produced two working examples of the pattern to stay consistent with.
8. **`assetflow_dashboard`** — first of the two aggregation modules. Requires every Tier 2 model to exist with final field names.
9. **`assetflow_reports`** — generate last. The SQL-view-backed models need the full, stable schema of every prior module to avoid regenerating views after later schema drift.

**Practical tip for step-by-step AI generation:** within each module, generate in the same sub-order every time — `models` → `security/ir.model.access.csv` → `security/*_rules.xml` → `views` → `data` (sequences/cron) — and have the agent verify the module installs cleanly before starting the next one. Feed the previous module's actual final code (not just a description) as context when generating a dependent module; this is what keeps field names and external IDs consistent across 9 separate generation passes.
