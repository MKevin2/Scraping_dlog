import os
import time
import requests
from utils import tempo_execucao
from bs4 import BeautifulSoup
from config import URL, BASE_URL, TIMEOUT, HEADERS, TERMO_INICIAL, FILTRO_URL_2026, CONTRATOS
import logging

logging.basicConfig(
    level=logging.INFO, 
    filename='request.log', 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

pasta_destino = "arquivos_dlog"
os.makedirs

def capturar_contratos():

    inicio_execucao = time.time()
    
    try:
        logging.info('------- INICIANDO -------')
        print("\nConectando ao site e analisando a estrutura...\n")
        response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)

        contador = 0

        for link in links:
            href = link['href'].lower()
            titulo = link.get_text().strip()
            titulo_minusculo = titulo.lower()

            if titulo_minusculo.startswith(TERMO_INICIAL) and FILTRO_URL_2026 in href:
                link_final = link['href']
                if not link_final.startswith('http'):
                    link_final = BASE_URL + link_final

                contador += 1

                # logging.info(f'{contador}: {titulo}') -> retornaria o nome dos contratos a cada iteração dentro do arquivo de logging

                CONTRATOS.append((contador, titulo, link_final))

        if contador == 0:
            print("Nenhum contrato localizado.")

        else:
            logging.info(f"Contrato(s): {len(CONTRATOS)} encontrados.")

    except Exception as e:
        print(f"Erro: {e}")
        logging.error(f"Automação gerou um exceção! \n{e}")
        logging.info('------- ENCERRANDO -------\n')

    finally:
        
        for contador, titulo, link_final in CONTRATOS:
            print(f"{contador}: {titulo}\n{link_final}\n")

    tempo_total = tempo_execucao(inicio_execucao)
    logging.info(f'Tempo: {tempo_total}.')
    logging.info('------- ENCERRANDO -------\n')

if __name__ == "__main__":
    capturar_contratos()