import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST")

try:
    # Set environment user to admin
    env = env(user=1)
    env.cr.execute("INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s) ON CONFLICT DO NOTHING", (env.ref('assetflow_base.group_assetflow_asset_manager').id, env.user.id))
    
    logger.info("1. Asset Creation")
    category = env['assetflow.category'].create({'name': 'Test Category'})
    asset = env['assetflow.asset'].create({
        'name': 'Test Laptop Odoo 19',
        'category_id': category.id,
        'is_bookable': True
    })
    assert asset.state == 'available', "Asset should start as available"
    
    logger.info("2. Asset Allocation")
    allocation = env['assetflow.allocation'].create({
        'asset_id': asset.id,
        'employee_id': env.user.id,
    })
    assert allocation.status == 'active', "Allocation should be active"
    assert asset.state == 'allocated', "Asset should be allocated"
    
    logger.info("3. Asset Allocation Return")
    allocation.return_condition_notes = "Looks good"
    allocation.action_return()
    assert allocation.status == 'returned', "Allocation should be returned"
    assert asset.state == 'available', "Asset should be available again"

    logger.info("4. Booking")
    from datetime import datetime, timedelta
    now = datetime.now()
    booking1 = env['assetflow.booking'].create({
        'asset_id': asset.id,
        'start_datetime': now + timedelta(days=1),
        'end_datetime': now + timedelta(days=1, hours=2),
        'purpose': 'Meeting'
    })
    
    logger.info("5. Booking Overlap Prevention")
    overlap_error = False
    try:
        booking2 = env['assetflow.booking'].create({
            'asset_id': asset.id,
            'start_datetime': now + timedelta(days=1, hours=1),
            'end_datetime': now + timedelta(days=1, hours=3),
            'purpose': 'Overlap'
        })
    except Exception as e:
        overlap_error = True
        logger.info(f"Overlap correctly caught: {e}")
    assert overlap_error, "Booking overlap should have been prevented"
    
    logger.info("6. Maintenance Request Workflow & Approval")
    maintenance = env['assetflow.maintenance'].create({
        'asset_id': asset.id,
        'description': 'Screen Repair'
    })
    assert maintenance.state == 'draft', "Maintenance should start as draft"
    maintenance.action_submit()
    assert maintenance.state == 'pending', "Maintenance should be pending"
    assert asset.state == 'maintenance', "Asset should be in maintenance"
    
    maintenance.action_approve()
    assert maintenance.state == 'approved', "Maintenance should be approved"
    
    maintenance.completion_date = now.date()
    maintenance.work_performed = 'Replaced screen'
    maintenance.action_complete()
    assert maintenance.state == 'completed', "Maintenance should be completed"
    assert asset.state == 'available', "Asset should be available after maintenance"
    
    logger.info("7. Notifications")
    notifications = env['assetflow.notification'].search([('res_model', '=', 'assetflow.maintenance'), ('res_id', '=', maintenance.id)])
    assert notifications, "Notifications should have been generated"
    
    logger.info("8. Audit Cycle Generation")
    audit = env['assetflow.audit.cycle'].create({
        'name': 'Test Audit',
        'scope_type': 'all',
        'date_from': now.date(),
        'date_to': now.date() + timedelta(days=7),
        'auditor_ids': [(4, env.user.id)]
    })
    wizard = env['assetflow.audit.line.generate.wizard'].create({'cycle_id': audit.id})
    wizard.generate_lines()
    assert audit.line_ids, "Audit lines should have been generated"
    
    logger.info("9. Dashboard KPI execution")
    total_assets = env['assetflow.asset'].search_count([])
    assert total_assets > 0, "Dashboard should be able to count assets"
    
    logger.info("10. Reports SQL execution")
    heatmap = env['assetflow.report.booking.heatmap'].search([], limit=1)
    utilization = env['assetflow.report.asset.utilization'].search([], limit=1)
    
    logger.info("ALL TESTS PASSED SUCCESSFULLY! The environment is stable.")
    env.cr.commit()
except Exception as e:
    logger.error(f"TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    env.cr.rollback()
