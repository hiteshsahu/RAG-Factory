from ragfactory.chunk import CodeChunker
from ragfactory.core import RawDocument


def _doc(text: str) -> RawDocument:
    return RawDocument(content=text, metadata={}, source_id="doc")


def test_splits_python_by_top_level_function_and_class():
    source = (
        "def foo():\n"
        "    return 1\n"
        "\n\n"
        "class Bar:\n"
        "    def method(self):\n"
        "        return 2\n"
    )

    chunks = CodeChunker().chunk(_doc(source))

    assert len(chunks) == 2
    assert chunks[0].content.startswith("def foo():")
    assert chunks[1].content.startswith("class Bar:")
    assert "def method" in chunks[1].content


def test_falls_back_to_blank_line_blocks_for_non_python():
    source = "function foo() {\n  return 1;\n}\n\nfunction bar() {\n  return 2;\n}\n"

    chunks = CodeChunker().chunk(_doc(source))

    assert len(chunks) == 2
    assert "function foo" in chunks[0].content
    assert "function bar" in chunks[1].content


def test_empty_source_yields_no_chunks():
    assert CodeChunker().chunk(_doc("")) == []
