def _seed_batch_with_resources(client):
    source = client.post("/api/v1/tenants", json={"display_name": "Contoso Source", "tenant_domain": "contoso.onmicrosoft.com", "role": "SOURCE"}).json()
    target = client.post("/api/v1/tenants", json={"display_name": "Contoso Target", "tenant_domain": "contosonew.onmicrosoft.com", "role": "TARGET"}).json()
    migration = client.post("/api/v1/migrations", json={"name": "Mass Tenant Migration", "source_tenant_id": source["id"], "target_tenant_id": target["id"]}).json()
    wave = client.post(f"/api/v1/migrations/{migration['id']}/waves", json={"name": "Wave 1"}).json()
    batch = client.post(f"/api/v1/waves/{wave['id']}/batches", json={"name": "Finance Users"}).json()
    client.post(f"/api/v1/batches/{batch['id']}/resources", json={"resource_type": "MAILBOX", "display_name": "Jane Doe", "source_identifier": "jane@contoso.onmicrosoft.com", "target_identifier": "jane@contosonew.onmicrosoft.com"})
    return migration, wave, batch


def test_mock_adapters_are_deterministic(client):
    from app.adapters.exchange import check_mailbox
    from app.adapters.graph import check_identity
    from app.adapters.sharepoint import check_site
    from app.models.batch import Resource

    ready = Resource(batch_id="b1", resource_type="MAILBOX", display_name="Jane Doe", source_identifier="jane@contoso.com", target_identifier="jane@contosonew.com")
    blocked = Resource(batch_id="b1", resource_type="MAILBOX", display_name="No Target", source_identifier="notarget@contoso.com", target_identifier=None)
    warning = Resource(batch_id="b1", resource_type="MAILBOX", display_name="Warn Case", source_identifier="warn@contoso.com", target_identifier="warn@contosonew.com")

    for check_fn, blocked_code, warning_code in ((check_identity, "GROUP_MAPPING_MISSING", "LICENSE_MISMATCH"), (check_mailbox, "TARGET_MAILUSER_INVALID", "FORWARDING_ENABLED"), (check_site, "SITE_MAPPING_MISSING", "STORAGE_QUOTA_LOW")):
        assert check_fn(ready).status == "READY"
        assert check_fn(ready).status == "READY"
        assert check_fn(blocked).status == "BLOCKED" and check_fn(blocked).code == blocked_code
        assert check_fn(warning).status == "WARNING" and check_fn(warning).code == warning_code


def test_full_phase3_assessment_ready(client):
    _, _, batch = _seed_batch_with_resources(client)
    body = client.post(f"/api/v1/tools/start_batch_assessment/{batch['id']}", json={}).json()
    assert body["run_status"] == "COMPLETED"
    assert body["overall_status"] == "READY"
    assert body["can_proceed"] is True
    assert len(body["results"]) == 3


def test_blocked_resource_propagates_to_all_domains(client):
    _, _, batch = _seed_batch_with_resources(client)
    client.post(f"/api/v1/batches/{batch['id']}/resources", json={"resource_type": "MAILBOX", "display_name": "Ghost User", "source_identifier": "ghost@contoso.onmicrosoft.com"})
    body = client.post(f"/api/v1/tools/start_batch_assessment/{batch['id']}", json={}).json()
    assert body["overall_status"] == "BLOCKED"
    assert body["blocker_count"] == 3
    codes = {r["blockers"][0]["code"] for r in body["results"]}
    assert codes == {"GROUP_MAPPING_MISSING", "TARGET_MAILUSER_INVALID", "SITE_MAPPING_MISSING"}


def test_failure_simulation_is_not_ready(client):
    _, _, batch = _seed_batch_with_resources(client)
    body = client.post(f"/api/v1/tools/start_batch_assessment/{batch['id']}", json={"simulate_errors": {"ExchangeOnline": "M365_TIMEOUT"}}).json()
    assert body["overall_status"] == "NOT_READY"
    exchange = next(r for r in body["results"] if r["domain"] == "ExchangeOnline")
    assert exchange["status"] == "UNAVAILABLE"
    assert exchange["error_code"] == "M365_TIMEOUT"


def test_completed_assessment_is_immutable(client):
    _, _, batch = _seed_batch_with_resources(client)
    body = client.post(f"/api/v1/tools/start_batch_assessment/{batch['id']}", json={}).json()
    resp = client.post("/api/v1/tools/assess_entra", json={"assessment_id": body["id"]})
    assert resp.status_code == 400
    assert "already completed" in resp.json()["detail"]


def test_invalid_simulation_code_is_rejected(client):
    _, _, batch = _seed_batch_with_resources(client)
    resp = client.post(f"/api/v1/tools/start_batch_assessment/{batch['id']}", json={"simulate_errors": {"ExchangeOnline": "NOT_A_REAL_ERROR"}})
    assert resp.status_code == 422


def test_copilot_resolvers(client):
    migration, _, batch = _seed_batch_with_resources(client)
    m = client.get(f"/api/v1/resolve/migrations/{migration['migration_code']}")
    b = client.get(f"/api/v1/resolve/batches/{batch['batch_code']}")
    assert m.status_code == 200 and m.json()["id"] == migration["id"]
    assert b.status_code == 200 and b.json()["id"] == batch["id"]
    assert client.get("/api/v1/resolve/batches/BATCH-999").status_code == 404
