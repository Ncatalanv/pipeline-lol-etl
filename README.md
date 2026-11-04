# League of Legends ETL Pipeline | Cloud Data Engineering

Un pipeline ETL (Extract, Transform, Load) automatizado que extrae estadísticas de partidas de la API oficial de Riot Games, procesa los datos en Python y los carga en un almacén de datos transaccional en la nube.

Este proyecto demuestra el ciclo de vida completo de la ingeniería de datos, incluyendo orquestación en la nube, manejo de límites de peticiones (Rate Limiting) y modelado de datos relacionales.

## Arquitectura del Flujo de Datos

1. **Extract (Riot Games API):** Extracción de perfiles de invocador (Account-V1) y detalles de partidas (Match-V5) utilizando peticiones HTTP. Implementa control de errores (status 429) y *rate limiting* adaptativo.
2. **Transform (Pandas):** Limpieza de estructuras JSON anidadas, deduplicación de registros, cálculo de métricas derivadas (KDA) y normalización de identificadores unificados (Riot IDs).
3. **Load (TiDB Serverless / MySQL):** Ingesta de datos limpios hacia una base de datos relacional en la nube utilizando SQLAlchemy y PyMySQL.
4. **Orchestration (GitHub Actions):** Automatización CI/CD que ejecuta el script principal de manera programada (CRON), manteniendo la base de datos actualizada diariamente sin intervención manual.

## Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Librerías:** Pandas, SQLAlchemy, PyMySQL, Requests
* **Base de Datos:** TiDB Serverless (MySQL-compatible Cloud DB)
* **Orquestación e Infraestructura:** GitHub Actions

## Modelo de Datos

Los datos se estructuran en una tabla de hechos diseñada para análisis analítico (`fact_player_match_stats`):

| Columna | Tipo de Dato | Descripción |
| :--- | :--- | :--- |
| `match_id` | VARCHAR | Identificador único de la partida (ej. LA2_123456789) |
| `puuid` | VARCHAR | Identificador global único del jugador |
| `summoner_name` | VARCHAR | Riot ID y Tagline (ej. Jugador#LAS) |
| `champion_name` | VARCHAR | Campeón utilizado |
| `kills` / `deaths` / `assists` | INT | Estadísticas de combate base |
| `kda` | FLOAT | Ratio de Asesinatos, Muertes y Asistencias |
| `total_damage` | INT | Daño total infligido a campeones |
| `win` | BOOLEAN | Resultado de la partida (1 = Victoria, 0 = Derrota) |

## Despliegue Local

Para replicar este proyecto en un entorno local:

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/lol-etl-pipeline.git](https://github.com/tu-usuario/lol-etl-pipeline.git)