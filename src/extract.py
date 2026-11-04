import os
import time
import requests
from dotenv import load_dotenv

#Se conectará a la API de Riot Games.

#Cargar variables ocultas del archivo .env (API key y conexión a DB)
load_dotenv()

class RiotDataExtractor:
    def __init__(self, region="americas"):
        #Obtener la clave de forma segura sin quemarla en el código
        self.api_key = os.getenv("RIOT_API_KEY")
        #El header que exige Riot para autenticar cada petición HTTP
        self.headers = {"X-Riot-Token": self.api_key}
        self.region = region
        self.base_url = f"https://{self.region}.api.riotgames.com"

    def get_puuid(self, game_name, tag_line):
        #Obtener el ID único universal (PUUID) del jugador a partir de su nombre y tag
        url = f"{self.base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)

        #Manejo de "Rate Limit" de Riot. Si supero el límite de peticiones, Riot devuelve código 429
        if response.status_code == 429:
            print("Límite de API alcanzado. Esperando 10 segundos...")
            time.sleep(10)
            return self.get_puuid(game_name, tag_line) #Reintento recursivo

        response.raise_for_status() #Lanza error y detiene el script si falla por otra razón
        return response.json()["puuid"]

    def get_match_ids(self, puuid, count=10):
        #Con el PUUID, pediré los IDs de las últimas 'count' partidas
        url = f"{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json() #Retornará una simple lista de IDs de partidas

    def get_match_detail(self, match_id):
        #Pedir toda la data de una partida específica
        url = f"{self.base_url}/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 429:
            print(f"Límite de API alcanzado al obtener detalles de la partida {match_id}. Esperando 10 segundos...")
            time.sleep(10)
            return self.get_match_detail(match_id) #Reintento recursivo


        if response.status_code == 200:
            return response.json()
        return None


