# League of Legends Incremental ETL & Data App

An End-to-End Data Engineering project that extracts live match statistics from the official Riot Games API, transforms nested JSON data, loads it into a cloud-based TiDB (MySQL) Data Warehouse, and serves it through an interactive UI inspired by OP.GG.

This project demonstrates a complete data engineering lifecycle, focusing on modular architecture, API rate-limit handling, relational data modeling, and **Incremental Loading** strategies.

## Key Data Engineering Features

* **On-Demand ETL Pipeline:** Instead of traditional scheduled batch jobs, the pipeline is triggered dynamically via the Streamlit UI. If a queried player is not in the database, the app extracts their recent matches on the fly.
* **Incremental Loading Strategy:** To prevent data duplication and optimize API call limits, the pipeline cross-references incoming `match_id`s with existing database records, transforming and inserting only new matches.
* **Modular Architecture:** The codebase is strictly decoupled into `extract`, `transform`, and `load` modules within the `src/` directory, adhering to software engineering best practices for scalability.
* **Data Modeling:** Flat, analytics-ready Fact Table (`fact_player_match_stats`) designed to support rapid querying and metric calculation (Win Rate, KDA) without complex joins.
* **Secure Secrets Management:** API keys and database credentials are fully decoupled from the codebase using Streamlit Secrets and dynamic OS environment variable injection.

## Technology Stack

* **Language:** Python 3.11+
* **Data Processing:** Pandas
* **Database & ORM:** TiDB Serverless (MySQL-compatible Cloud DB), SQLAlchemy, PyMySQL
* **Data Serving & UI:** Streamlit, Plotly, HTML/CSS
* **Source API:** Riot Games Developer API (Account-V1, Match-V5)

## Relational Data Model

The data is structured into a transactional Fact Table optimized for downstream analytics (`fact_player_match_stats`):

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `match_id` | VARCHAR | Unique match identifier (e.g., LA2_123456789) |
| `puuid` | VARCHAR | Global unique player identifier |
| `summoner_name` | VARCHAR | Normalized Riot ID and Tagline (e.g., Player#LAS) |
| `champion_name` | VARCHAR | Champion played |
| `kills` / `deaths` / `assists` | INT | Core combat statistics |
| `kda` | FLOAT | Derived metric: (Kills + Assists) / max(1, Deaths) |
| `total_damage` | INT | Total damage dealt to champions |
| `win` | BOOLEAN | Match outcome (1 = Victory, 0 = Defeat) |

## Local Setup & Deployment

To replicate this Data Engineering environment locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ncatalanv/pipeline-lol-etl.git
   cd pipeline-lol-etl
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Secrets:**
   Create a `.streamlit` folder in the root directory and add a `secrets.toml` file with your credentials:
   ```toml
   [tidb]
   host = "your-tidb-host.cloud"
   port = 4000
   database = "lol_analytics"
   username = "your-username"
   password = "your-password"

   [riot]
   api_key = "RGAPI-your-developer-api-key"
   ```

4. **Launch the Data App:**
   ```bash
   streamlit run app.py
   ```