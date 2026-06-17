from ragfactory.generate import TemplateGenerator


def test_generate_includes_context():
    answer = TemplateGenerator().generate("What is RAG?", ["chunk one", "chunk two"])

    assert "What is RAG?" in answer
    assert "chunk one" in answer
    assert "chunk two" in answer


def test_generate_without_context():
    answer = TemplateGenerator().generate("unanswerable", [])

    assert "No context found" in answer
