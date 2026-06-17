from ragfactory.core import Settings


def test_settings_have_sane_defaults():
    settings = Settings(_env_file=None)

    assert settings.chunk_size == 200
    assert settings.chunk_overlap == 50
    assert settings.top_k == 5
    assert settings.openai_api_key is None
