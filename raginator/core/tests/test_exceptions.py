# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from raginator.core import RaginatorError, StageError


def test_stage_error_includes_stage_name_in_message():
    error = StageError(stage="chunk", message="boom")

    assert error.stage == "chunk"
    assert "chunk" in str(error)
    assert "boom" in str(error)
    assert isinstance(error, RaginatorError)
