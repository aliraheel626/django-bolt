from __future__ import annotations

import sys
import time

import pytest

pytestmark = [pytest.mark.server_integration, pytest.mark.platform_smoke]


def test_runbolt_serves_http_request(make_server_project):
    project = make_server_project(
        project_api_body="""
        @api.get("/hello")
        async def hello():
            return {"message": "plain"}
        """
    )

    with project.start() as server:
        response = server.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "plain"}


def test_runbolt_dev_serves_http_request(make_server_project):
    project = make_server_project(
        project_api_body="""
        @api.get("/hello")
        async def hello():
            return {"message": "dev"}
        """
    )

    with project.start(dev=True) as server:
        response = server.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "dev"}


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Reload smoke runs only on Linux.")
def test_runbolt_dev_reloads_after_file_change(make_server_project):
    project = make_server_project(
        project_api_body="""
        @api.get("/version")
        async def version():
            return {"version": "v1"}
        """
    )

    with project.start(dev=True) as server:
        initial = server.get("/version")
        assert initial.json() == {"version": "v1"}

        time.sleep(0.3)
        project.write_project_api(
            """
            @api.get("/version")
            async def version():
                return {"version": "v2"}
            """
        )

        payload = server.wait_for_json("/version", lambda body: body["version"] == "v2", timeout=30)

    assert payload == {"version": "v2"}
