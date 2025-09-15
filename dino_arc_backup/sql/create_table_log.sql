USE [data-master-dev-db-logs];
GO

CREATE TABLE dino_ingestion_logs (
    execution_id NVARCHAR(255),
    table_name NVARCHAR(255),
    [schema_name] NVARCHAR(255),
    catalog_name NVARCHAR(255),
    source_path NVARCHAR(1000),
    execution_status NVARCHAR(100),
    start_time DATETIME2,
    end_time DATETIME2,
    execution_duration_seconds FLOAT,
    records_read BIGINT,
    records_written BIGINT,
    [file_format] NVARCHAR(50),
    ingestion_type NVARCHAR(50),
    [message] NVARCHAR(MAX),
    files_ingested NVARCHAR(MAX),
    file_size_bytes BIGINT,
    additional_metadata NVARCHAR(MAX)
);
