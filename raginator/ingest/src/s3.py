# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import boto3
from raginator.core import Ingestor, RawDocument


class S3Ingestor(Ingestor):
    """Reads every object under a bucket/prefix as a text document (The Suck-Inator)."""

    def __init__(self, bucket: str, prefix: str = "", client: Any | None = None) -> None:
        self._bucket = bucket
        self._prefix = prefix
        self._client = client if client is not None else boto3.client("s3")

    def ingest(self) -> Iterable[RawDocument]:
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                body = self._client.get_object(Bucket=self._bucket, Key=key)["Body"].read()
                yield RawDocument(
                    content=body.decode("utf-8", errors="replace"),
                    metadata={"bucket": self._bucket, "key": key},
                    source_id=f"s3://{self._bucket}/{key}",
                )
