from __future__ import annotations

import pytest


@pytest.mark.integration
def test_frontend_component_rendering_cases_documented(import_optional):
    # Frontend tests are specified in tests.md (React Testing Library + Jest).
    # This Python suite keeps the requirement visible until frontend code exists.
    import_optional("frontend")


@pytest.mark.integration
def test_frontend_user_flow_cases_documented(import_optional):
    # Frontend flow: paste URL -> generate -> output + loading + download states.
    import_optional("frontend")
