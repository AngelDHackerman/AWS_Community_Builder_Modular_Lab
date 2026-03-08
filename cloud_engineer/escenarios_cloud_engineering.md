## 1. Serverless Data API
- Arquitectura:
    * API Gateway
    * → Lambda
    * → DynamoDB
    * → S3 backup
- Conceptos:
    * IAM least privilege
    * serverless backend
    * logging con CloudWatch
- Preguntas de entrevista que practicarías:
    * cuándo usar DynamoDB vs RDS
    * cómo manejar retries en Lambda
    * cómo diseñar rate limiting


## 2. Event-driven pipeline
- Arquitectura:
    * S3 upload
    * → EventBridge
    * → Lambda
    * → SNS notification
- Conceptos:
    * event-driven rchitectures
    * observabilidad
    * resiliencia


## 3. Secure data lake
- Arquitectura:
    * S3 data lake
    * → Glue Data Catalog
    * → Athena queries
- Conceptos:
    * particionado
    * formato Parquet
    * costos de Athena


## 4. Terraform multi-environment
- Infraestructura:
    * dev
    * staging
    * prod
- Conceptos:
    * terraform modules
    * remote state
    * variables y workspaces
    

## 5. Observability stack
- Arquitectura:
    * Lambda
    * → CloudWatch metrics
    * → alarms
    * → SNS
- Conceptos:
    * monitoring
    * alerting
    * debugging cloud systems