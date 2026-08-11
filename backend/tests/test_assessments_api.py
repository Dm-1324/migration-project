def _seed_batch(client):
    source = client.post("/api/v1/tenants", json={"display_name": "Contoso Source", "tenant_domain": "contoso.onmicrosoft.com", "role": "SOURCE"}).json()
    target = client.post("/api/v1/tenants", json={"display_name": "Contoso Target", "tenant_domain": "contosonew.onmicrosoft.com", "role": "TARGET"}).json()
    migration = client.post("/api/v1/migrations", json={"name": "Mass Tenant Migration", "source_tenant_id": source["id"], "target_tenant_id": target["id"]}).json()
    wave = client.post(f"/api/v1/migrations/{migration['id']}/waves", json={"name": "Wave 1"}).json()
    batch = client.post(f"/api/v1/waves/{wave['id']}/batches", json={"name": "Finance Users"}).json()
    return migration, wave, batch


def _domain_payload(domain, status, blocked=0, warning=0, ready=250, blockers=None):
    blockers = blockers or []
    return {"domain": domain, "status": status, "evaluated_resources": ready + blocked + warning, "ready": ready, "warning": warning, "blocked": blocked, "can_proceed": status == "READY", "blockers": blockers, "recommended_actions": []}


def test_readiness_not_ready_before_any_assessment(client):
    _, _, batch = _seed_batch(client)
    body = client.get(f"/api/v1/readiness/{batch['id']}").json()
    assert body["status"] == "NOT_READY"
    assert body["can_proceed"] is False
    assert set(body["domains"].keys()) == {"Entra", "ExchangeOnline", "OneDrive"}


def test_full_assessment_flow_all_ready(client):
    _, _, batch = _seed_batch(client)
    start = client.post(f"/api/v1/batches/{batch['id']}/assessments", json={}).json()
    run_id = start["run_id"]
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    for domain in ("Entra", "ExchangeOnline", "OneDrive"):
        assert client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload(domain, "READY")).status_code == 201
    detail = client.get(f"/api/v1/assessments/{assessment_id}").json()
    assert detail["run_status"] == "COMPLETED" and detail["overall_status"] == "READY" and detail["can_proceed"] is True
    assert client.get(f"/api/v1/runs/{run_id}/status").json()["status"] == "COMPLETED"
    assert client.get(f"/api/v1/readiness/{batch['id']}").json()["status"] == "READY"
    assert client.get(f"/api/v1/batches/{batch['id']}").json()["readiness_status"] == "READY"


def test_blocked_domain_produces_blocked_overall_and_denies_ready_transition(client):
    _, _, batch = _seed_batch(client)
    client.post(f"/api/v1/batches/{batch['id']}/assessments", json={})
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("Entra", "READY"))
    client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("ExchangeOnline", "BLOCKED", blocked=1, ready=249, blockers=[{"code": "TARGET_MAILUSER_INVALID", "severity": "BLOCKING", "evidence_ref": "exec-9fd2"}]))
    client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("OneDrive", "READY"))
    detail = client.get(f"/api/v1/assessments/{assessment_id}").json()
    assert detail["overall_status"] == "BLOCKED" and detail["can_proceed"] is False
    transition = client.post(f"/api/v1/batches/{batch['id']}/lifecycle/transition", json={"target_state": "READY"}).json()
    assert transition["allowed"] is False


def test_lifecycle_transition_allowed_when_ready(client):
    _, _, batch = _seed_batch(client)
    client.post(f"/api/v1/batches/{batch['id']}/assessments", json={})
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    for domain in ("Entra", "ExchangeOnline", "OneDrive"):
        client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload(domain, "READY"))
    transition = client.post(f"/api/v1/batches/{batch['id']}/lifecycle/transition", json={"target_state": "READY"}).json()
    assert transition["allowed"] is True and transition["current_state"] == "READY"


def test_unavailable_domain_never_becomes_ready(client):
    _, _, batch = _seed_batch(client)
    client.post(f"/api/v1/batches/{batch['id']}/assessments", json={})
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    payload = _domain_payload("ExchangeOnline", "UNAVAILABLE", ready=0)
    payload["error_code"] = "M365_TIMEOUT"
    payload["can_proceed"] = False
    client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=payload)
    client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("Entra", "READY"))
    client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("OneDrive", "READY"))
    detail = client.get(f"/api/v1/assessments/{assessment_id}").json()
    assert detail["overall_status"] == "NOT_READY" and detail["can_proceed"] is False


def test_malformed_domain_result_rejected(client):
    _, _, batch = _seed_batch(client)
    client.post(f"/api/v1/batches/{batch['id']}/assessments", json={})
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    resp = client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("Entra", "SOMETHING_INVALID"))
    assert resp.status_code == 422


def test_submit_result_for_undeclared_domain_is_rejected(client):
    _, _, batch = _seed_batch(client)
    client.post(f"/api/v1/batches/{batch['id']}/assessments", json={"domains": ["Entra", "ExchangeOnline"]})
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    resp = client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload("OneDrive", "READY"))
    assert resp.status_code == 400


def test_audit_trail_captures_assessment_lifecycle(client):
    _, _, batch = _seed_batch(client)
    client.post(f"/api/v1/batches/{batch['id']}/assessments", json={})
    assessment_id = client.get(f"/api/v1/batches/{batch['id']}/assessments").json()[0]["id"]
    for domain in ("Entra", "ExchangeOnline", "OneDrive"):
        client.post(f"/api/v1/assessments/{assessment_id}/domains/result", json=_domain_payload(domain, "READY"))
    event_types = {e["event_type"] for e in client.get("/api/v1/audit", params={"batch_id": batch["id"]}).json()}
    assert {"ASSESSMENT_STARTED", "DOMAIN_RESULT_SUBMITTED", "ASSESSMENT_COMPLETED"}.issubset(event_types)


def test_readiness_for_missing_batch_returns_404(client):
    assert client.get("/api/v1/readiness/does-not-exist").status_code == 404
