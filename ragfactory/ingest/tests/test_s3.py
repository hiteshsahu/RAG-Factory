from io import BytesIO
from typing import Any

from ragfactory.ingest import S3Ingestor


class FakePaginator:
    def __init__(self, pages: list[dict[str, Any]]) -> None:
        self._pages = pages

    def paginate(self, **kwargs: Any) -> list[dict[str, Any]]:
        return self._pages


class FakeS3Client:
    def __init__(self, objects: dict[str, bytes]) -> None:
        self._objects = objects

    def get_paginator(self, _name: str) -> FakePaginator:
        return FakePaginator([{"Contents": [{"Key": key} for key in self._objects]}])

    def get_object(self, Bucket: str, Key: str) -> dict[str, Any]:
        return {"Body": BytesIO(self._objects[Key])}


def test_s3_ingestor_reads_every_object():
    client = FakeS3Client({"docs/a.txt": b"hello s3"})

    [document] = list(S3Ingestor(bucket="my-bucket", prefix="docs/", client=client).ingest())

    assert document.content == "hello s3"
    assert document.metadata == {"bucket": "my-bucket", "key": "docs/a.txt"}
    assert document.source_id == "s3://my-bucket/docs/a.txt"
