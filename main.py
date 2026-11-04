from src.extract import RiotDataExtractor
from src.transform import transform_match_data
from src.load import load_to_database
import time

#Llamar archivos en orden lógico de ETL
def run_pipeline():
    print("(1/3) Iniciando Extracción...")
    extractor = RiotDataExtractor(region="americas")

    #Aquí poner ID para analizar - Nombre - TAG
    puuid = extractor.get_puuid("Erenxd69", "LAS")

    #Obtener los últimos 10 IDs de partida
    match_ids = extractor.get_match_ids(puuid, count=10)

    #Usar List COmprehension para hacer una petición por cad partida y guardar los JSONs
    raw_matches = []
    print(f"Se encontraron {len(match_ids)} partidas. Descargando detalles...")

    for match_id in match_ids:
        print(f"Extreyendo detalles de la partida {match_id}...")
        match_data = extractor.get_match_detail(match_id)
        raw_matches.append(match_data)
        time.sleep(0.5)

    print("(2/3) Transformando datos...")
    df_clean = transform_match_data(raw_matches)

    print("(3/3) Cargando datos a la base de datos...")
    load_to_database(df_clean)

    print("Pipeline completado exitosamente.")

if __name__ == "__main__":
    run_pipeline()
