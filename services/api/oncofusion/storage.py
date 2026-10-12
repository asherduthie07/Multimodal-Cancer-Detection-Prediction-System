from pathlib import Path
from typing import Protocol


class ArtifactStore(Protocol):
    def put(self, case_id: str, digest: str, suffix: str, content: bytes) -> str: ...


class LocalArtifactStore:
    def __init__(self, root: str):
        self.root = Path(root).resolve()

    def put(self, case_id: str, digest: str, suffix: str, content: bytes) -> str:
        # IDs and digest are validated before this method is called.
        target_dir = self.root / case_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{digest}{suffix}"
        target.write_bytes(content)
        return str(target)


class S3ArtifactStore:
    """S3-compatible adapter; install boto3 only when object storage is configured."""

    def __init__(self, bucket: str, endpoint_url: str | None = None):
        import boto3
        self.bucket = bucket
        self.client = boto3.client("s3", endpoint_url=endpoint_url)

    def put(self, case_id: str, digest: str, suffix: str, content: bytes) -> str:
        key = f"cases/{case_id}/{digest}{suffix}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)
        return f"s3://{self.bucket}/{key}"
