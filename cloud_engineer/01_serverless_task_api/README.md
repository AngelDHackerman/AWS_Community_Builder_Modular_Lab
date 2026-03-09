# Serverlss Task API Project

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

### 2. ¿Para qué se usa esta arquitectura en el mundo real?

Este patrón es muy común en startups y microservicios.

| Caso                 | Qué hace                        |
| -------------------- | ------------------------------- |
| API de usuarios      | Crear, editar o leer usuarios   |
| Backend de app móvil | Guardar sesiones, preferencias  |
| API de IoT           | Registrar sensores              |
| Event ingestion      | Guardar eventos de aplicaciones |
| Config service       | Guardar configuraciones         |

### 3. API Gateway (la puerta de entrada)

API Gateway es el servicio que expone una API HTTP pública.

Funciones principales:

    ✔ Recibir requests HTTP
    ✔ Autenticación (IAM, Cognito, API keys)
    ✔ Routing
    ✔ Rate limiting
    ✔ Integración con Lambda

### 4. AWS Lambda (backend serverless)

Lambda es donde vive la lógica de la aplicación.

Ventajas:

* no hay servidores
* escala automáticamente
* pagas por ejecución

Lambda:

    ✔ recibe request
    ✔ procesa lógica
    ✔ guarda datos

### 5. DynamoDB (base de datos serverless)

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

### 6. ¿Por qué usar S3 backup?

Aunque DynamoDB es confiable, muchas empresas:

    ✔ guardan logs
    ✔ guardan eventos
    ✔ guardan snapshots

en S3 buckets. 

Ventajas:

* auditoría
* data lake
* analytics con Athena
* ML training data

### 7. CloudWatch 

### 8. X-Ray Tracing 

## API Endpoints y Estructura JSON

Endpoints: 

* `GET /tasks` → obtener todas las tareas
* `GET /tasks/{task_id}` → obtener una tarea específica
* `POST /tasks` → crear una nueva tarea
* `PATCH /tasks/{task_id}` → editar parcialmente una tarea
* `DELETE /tasks/{task_id}` → eliminar una tarea

Ejemplo de un item __"Task"__ en DynamoDB: 

```json
{
  "task_id": "123",
  "title": "Study AWS Lambda",
  "status": "pending",
  "created_at": "2026-03-09T15:00:00Z",
  "updated_at": "2026-03-09T15:00:00Z"
}
```

Ejemplo de un item __"Log"__ a S3: 


```json
{
  "event_type": "task_created",
  "task_id": "123",
  "timestamp": "2026-03-09T15:00:00Z",
  "payload": {
    "title": "Study AWS Lambda",
    "status": "pending"
  }
}
```

En el backup de S3 se iran todos los eventos: `POST, PATCH, DELETE`. El evento `GET` se quedara solo en ClouWatch por simplicidad.

* Usario que solicita las task

Estoy simulando un backend serverless donde un cliente consume una API en API Gateway. Esa API invoca una Lambda, la cual puede leer o escribir datos en DynamoDB. La Lambda genera logs en CloudWatch, puede guardar backups o eventos en S3, y opcionalmente se integra con X-Ray para tracing y observability.

