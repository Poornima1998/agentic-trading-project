from __future__ import annotations

from pathlib import Path

import boto3
import pandas as pd
from sqlalchemy import create_engine

from src.config import settings


class AWSClient:
    def __init__(self) -> None:
        self.s3_client = None
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_default_region,
            )

    def upload_file_to_s3(self, file_path: str | Path, object_name: str | None = None) -> None:
        if not self.s3_client:
            raise RuntimeError("AWS credentials are not configured.")
        if not settings.s3_bucket:
            raise RuntimeError("S3_BUCKET is not configured.")

        file_path = Path(file_path)
        self.s3_client.upload_file(str(file_path), settings.s3_bucket, object_name or file_path.name)

    def write_dataframe_to_rds(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is not configured.")
        engine = create_engine(settings.database_url)
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists=if_exists, index=False)
