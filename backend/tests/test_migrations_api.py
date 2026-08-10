def _make_tenants(client):
    source = client.post("/api/v1/tenants", json={"display_name": "Contoso Source", "tenant_domain": "contoso.onmicrosoft.com", "role": "SOURCE"}).json()
    target = client.post("/api/v1/tenants", json={"display_name": "Contoso Target", "tenant_domain": "contosonew.onmicrosoft.com", "role": "TARGET"}).json()
    return source, target

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_full_migration_batch_evidence_flow(client):
    source, target = _make_tenants(client)
    mig_resp = client.post("/api/v1/migrations", json={"name": "Mass Tenant Migration", "source_tenant_id": source["id"], "target_tenant_id": target["id"]})
    assert mig_resp.status_code == 201
    migration = mig_resp.json(); assert migration["migration_code"].startswith("MASS"); assert migration["status"] == "RECEIVED"
    detail = client.get(f"/api/v1/migrations/{migration['id']}").json(); assert detail["wave_count"] == 0; assert detail["batch_count"] == 0
    wave = client.post(f"/api/v1/migrations/{migration['id']}/waves", json={"name": "Wave 1", "sequence": 1}).json()
    batch = client.post(f"/api/v1/waves/{wave['id']}/batches", json={"name": "Finance Users"}).json(); assert batch["batch_code"] == "BATCH-001"; assert batch["readiness_status"] == "NOT_ASSESSED"
    resource = client.post(f"/api/v1/batches/{batch['id']}/resources", json={"resource_type": "MAILBOX", "display_name": "Jane Doe", "source_identifier": "jane@contoso.onmicrosoft.com"}).json(); assert resource["batch_id"] == batch["id"]
    assert len(client.get(f"/api/v1/batches/{batch['id']}/resources").json()) == 1
    detail = client.get(f"/api/v1/migrations/{migration['id']}").json(); assert detail["wave_count"] == 1; assert detail["batch_count"] == 1
    evidence = client.post("/api/v1/evidence", json={"batch_id": batch["id"], "domain": "ExchangeOnline", "tool": "Get-MailUser", "operation_id": "op-001", "affected_resource": "jane@contoso.onmicrosoft.com", "status": "FAILED", "duration_ms": 2350}).json(); assert evidence["status"] == "FAILED"
    assert len(client.get(f"/api/v1/batches/{batch['id']}/evidence").json()) == 1
    exception = client.post("/api/v1/exceptions", json={"batch_id": batch["id"], "domain": "ExchangeOnline", "code": "TARGET_MAILUSER_INVALID", "description": "Target MailUser is invalid or missing.", "severity": "BLOCKING", "evidence_id": evidence["id"], "affected_resource": "jane@contoso.onmicrosoft.com"})
    assert exception.status_code == 201; exception = exception.json(); assert exception["status"] == "OPEN"
    filtered = client.get("/api/v1/exceptions", params={"batch_id": batch["id"], "severity": "BLOCKING"}).json(); assert len(filtered) == 1; assert filtered[0]["code"] == "TARGET_MAILUSER_INVALID"
    updated = client.patch(f"/api/v1/exceptions/{exception['id']}", json={"status": "ACKNOWLEDGED"}).json(); assert updated["status"] == "ACKNOWLEDGED"

def test_migration_not_found(client):
    assert client.get("/api/v1/migrations/does-not-exist").status_code == 404

def test_create_migration_with_bad_tenant_returns_404(client):
    resp = client.post("/api/v1/migrations", json={"name": "Bad Migration", "source_tenant_id": "missing", "target_tenant_id": "also-missing"})
    assert resp.status_code == 404
