import pandas as pd

#Aplanar datos que vienen de la API de Riot Games y limpiar inconsistencias matemáticas

def transform_match_data(raw_matches):
    #Guardar los datos planos antes de pasarlos a Pandas
    transformed_records = []

    for match in raw_matches:
        if not match: #Si la patición falla y viene vacía, la saltamos
            continue

        #Navegar por el JSON: extraer metadatos generales de la partida
        info = match["info"]
        match_id = match["metadata"]["matchId"]
        game_duration = info["gameDuration"]
        game_mode = info["gameMode"]

        #Iteramos sobre los 10 jugadores de esa partida
        for participant in info["participants"]:

            #Calculamos el KDA (Kills + Assists / Deaths)
            #Usamos max(1, deaths) para evitar el error fatal de división por cero si el jugador no murió
            deaths = max(1, participant["deaths"])
            kda = round((participant["kills"] + participant["assists"]) / deaths, 2)

            #Crear un diccionario solo con los datos que me importan para análisis
            record = {
                "match_id": match_id,
                "game_mode": game_mode,
                "game_duration_min": round(game_duration / 60, 2), #Convertir segundos a minutos
                "puuid": participant["puuid"],
                "summoner_name": f"{participant.get('riotIdGameName', 'Desconocido')}#{participant.get('riotIdTagline', '')}",
                "champion_name": participant["championName"],
                "kills": participant["kills"],
                "deaths": participant["deaths"],
                "assists": participant["assists"],
                "kda": kda,
                "total_damage": participant["totalDamageDealtToChampions"],
                "gold_earned": participant["goldEarned"],
                "win": participant["win"] #Boolean
            }
            transformed_records.append(record)

    #Convertir la lista de diccionarios en un DataFrame de Pandas
    df = pd.DataFrame(transformed_records)

    #Eliminar duplicados exactos por si se procesa la misma partida dos veces por error
    df.drop_duplicates(subset=["match_id", "puuid"], inplace= True)

    return df




