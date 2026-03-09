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

## 2. ¿Para qué se usa esta arquitectura en el mundo real?

Este patrón es muy común en startups y microservicios.

| Caso                 | Qué hace                        |
| -------------------- | ------------------------------- |
| API de usuarios      | Crear, editar o leer usuarios   |
| Backend de app móvil | Guardar sesiones, preferencias  |
| API de IoT           | Registrar sensores              |
| Event ingestion      | Guardar eventos de aplicaciones |
| Config service       | Guardar configuraciones         |

## 3. API Gateway (la puerta de entrada)

API Gateway es el servicio que expone una API HTTP pública.

Funciones principales:

    ✔ Recibir requests HTTP
    ✔ Autenticación (IAM, Cognito, API keys)
    ✔ Routing
    ✔ Rate limiting
    ✔ Integración con Lambda

## 4. AWS Lambda (backend serverless)

Lambda es donde vive la lógica de la aplicación.

Ventajas:

* no hay servidores
* escala automáticamente
* pagas por ejecución

Lambda:

    ✔ recibe request
    ✔ procesa lógica
    ✔ guarda datos

## 5. DynamoDB (base de datos serverless)

DynamoDB es una base de datos NoSQL totalmente administrada.

Ventajas:

* escala automáticamente
* latencia muy baja
* no necesitas servidores
* altamente disponible

Operaciones comunes:

| Acción | API        |
| ------ | ---------- |
| Create | PutItem    |
| Read   | GetItem    |
| Update | UpdateItem |
| Delete | DeleteItem |

