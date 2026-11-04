import os
from sqlalchemy import create_engine

def load_to_database(df, table_name = "fact_player,match_stats"):
    #Obtener la URL de conexión de .env
    db_url = os.getenv("DB_CONNECTION_STRING")

    #SQLAlchemy crea el motor que gestiona la conexión con la base de datos
    engine = create_engine(db_url)

    #Abrimos una transacción segura con la base de datos
    with engine.begin() as connection:
        #Pandas convierte el DataFrame en sentencias INSERT SQL automáticamente
        #if_exists="append" --> si la tabla existe, agrega las filas nuevas al final
        #index=False --> evita guardar el índice numérico autogenerado de pandas (0, 1, 2) como una columna
        df.to_sql(name=table_name, con=connection, if_exists="append", index=False)

    print(f"Exitosamente cargados {len(df)} registros en la tabla '{table_name}'.")