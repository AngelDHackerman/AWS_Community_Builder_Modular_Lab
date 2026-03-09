## 1. Arquitectura del módulo

Flujo:

* Un cliente hace una petición HTTP.
* API Gateway recibe la petición.
* Lambda ejecuta lógica backend.
* Lambda guarda o lee datos en DynamoDB.
* Lambda guarda backup o eventos en S3.
* Logs quedan en CloudWatch.

Arquitectura:
```
    Client
     ↓
    API Gateway
     ↓
    Lambda
     ↓
    DynamoDB
     ↓
    S3 backup
     ↓
    CloudWatch
     ↓
    X-Ray Tracing
```

