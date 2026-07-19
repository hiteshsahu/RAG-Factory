# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

DASHBOARD_PATH = Path(__file__).parent.parent / "dashboards" / "raginator.json"


def test_dashboard_json_is_valid_and_references_known_metrics():
    dashboard = json.loads(DASHBOARD_PATH.read_text())

    assert dashboard["title"]
    panel_exprs = " ".join(
        target["expr"] for panel in dashboard["panels"] for target in panel["targets"]
    )
    for metric in (
        "raginator_index_requests_total",
        "raginator_indexed_chunks_total",
        "raginator_query_requests_total",
        "raginator_query_score_bucket",
    ):
        assert metric in panel_exprs
