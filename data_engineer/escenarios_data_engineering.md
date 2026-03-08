## 6. Batch ETL pipeline
- Arquitectura:
    * S3 raw
    * → Glue ETL
    * → S3 curated
    * → Athena
- Conceptos:
    * medallion architecture
    * batch pipelines


## 7. Streaming ingestion
- Arquitectura:
    * API ingestion
    * → Kinesis
    * → Lambda
    * → S3
- Conceptos:
    * streaming vs batch
    * backpressure
    * event processing


## 8. Data warehouse pipeline
- Arquitectura:
    * S3
    * → Redshift Spectrum
    * → BI dashboard
- Conceptos:
    * data warehouse
    * star schema


## 9. Data quality checks
- Arquitectura:
    * Glue job
    * → validation rules
    * → failed dataset bucket
- Conceptos:
    * data quality
    * schema validation


## 10. Data catalog automation
- Arquitectura:
    * Step Functions
    * → Glue crawler
    * → Athena
- Conceptos:
    * metadata management
    * data discovery