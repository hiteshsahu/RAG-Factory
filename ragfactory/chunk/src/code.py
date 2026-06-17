from __future__ import annotations

import ast

from ragfactory.core import Chunk, Chunker, RawDocument


class CodeChunker(Chunker):
    """Splits source code along top-level function/class boundaries (The Chunk-Inator, code mode).

    Uses Python's ast module for valid Python source; falls back to
    blank-line-separated blocks for anything else (other languages, or code
    that fails to parse).
    """

    def chunk(self, document: RawDocument) -> list[Chunk]:
        blocks = self._python_blocks(document.content) or self._blank_line_blocks(
            document.content
        )
        return [
            Chunk(
                content=block,
                metadata=document.metadata,
                chunk_id=f"{document.source_id}-{index}",
                doc_id=document.source_id,
            )
            for index, block in enumerate(blocks)
            if block.strip()
        ]

    def _python_blocks(self, source: str) -> list[str] | None:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None

        top_level_nodes = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        ]
        if not top_level_nodes:
            return None

        lines = source.splitlines()
        return [
            "\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno])
            for node in top_level_nodes
        ]

    def _blank_line_blocks(self, source: str) -> list[str]:
        blocks = []
        current: list[str] = []
        for line in source.splitlines():
            if line.strip() == "" and current:
                blocks.append("\n".join(current))
                current = []
            elif line.strip() != "":
                current.append(line)
        if current:
            blocks.append("\n".join(current))
        return blocks
