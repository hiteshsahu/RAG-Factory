# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

import pytest
from raginator.core import Chunker


def test_abstract_stage_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Chunker()
