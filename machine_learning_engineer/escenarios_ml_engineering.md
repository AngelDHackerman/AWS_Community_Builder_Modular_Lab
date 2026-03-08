## 11. ML training pipeline
- Arquitectura:
    * _S3 dataset_
    * _→ SageMaker training job_
    * _→ model artifact en S3_
- Usando:
    * Amazon SageMaker
- Conceptos:
    * training pipelines
    * feature engineering


## 12. ML inference API
- Arquitectura:
    * _API Gateway_
    * _→ Lambda_
    * _→ SageMaker endpoint_
- Conceptos:
    * real-time inference
    * latency vs costo

## 13. Fraud detection model
- Arquitectura:
    * transaction dataset
    * → SageMaker training
    * → model deployment
- Conceptos:
    * classification models
    * fraud detection
    * Este conecta perfecto con tu objetivo de fraud detection engineer.


## 14. ML pipeline con Databricks
- Arquitectura:
    * S3 data lake
    * → Databricks Spark
    * → MLflow experiment tracking
- Usando:
    * Databricks
- Conceptos:
    * Spark ML
    * experiment tracking
    * feature pipelines


## 15. Feature store architecture
- Arquitectura:
    * S3 raw
    * → Databricks feature engineering
    * → SageMaker model
- Conceptos:
    * feature store
    * reproducible ML pipelines