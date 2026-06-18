import pytest
from raginator.core import Chunker


def test_abstract_stage_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Chunker()
