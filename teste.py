import os
import time
import requests
from bs4 import BeautifulSoup
from utils import tempo_execucao
from config import URL, BASE_URL, TIMEOUT, HEADERS, TERMO_INICIAL, FILTRO_URL_2026, CONTRATOS
import logging

logging.basicConfig(
    level=logging.INFO, 
    filename='request.log', 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Correção da criação da pasta destino principal
pasta_destino_raiz = "arquivos_dlog"
os.makedirs(pasta_destino_raiz, exist_ok=True)

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

            # Mantém o seu filtro cirúrgico que evita pegar links indesejados
            if titulo_minusculo.startswith(TERMO_INICIAL) and FILTRO_URL_2026 in href:
                link_final = link['href']
                if not link_final.startswith('http'):
                    link_final = BASE_URL + link_final

                contador += 1
                CONTRATOS.append((contador, titulo, link_final))

        if contador == 0:
            print("Nenhum contrato localizado.")
        else:
            logging.info(f"Contrato(s): {len(CONTRATOS)} encontrados.")

    except Exception as e:
        print(f"Erro: {e}")
        logging.error(f"Automação gerou uma exceção! \n{e}")
        logging.info('------- ENCERRANDO -------\n')

    finally:
        print("Iniciando o download dos arquivos mapeados...\n")
        
        for contador, titulo, link_final in CONTRATOS:
            print(f"{contador}: {titulo}\n{link_final}")
            
            try:
                # 1. Cria uma subpasta para cada contrato para manter organizado
                # Remove caracteres que o sistema operacional proíbe em pastas
                nome_pasta_limpo = "".join(c for c in titulo if c.isalnum() or c in (' ', '_', '-', '.')).strip()
                pasta_contrato = os.path.join(pasta_destino_raiz, nome_pasta_limpo)
                os.makedirs(pasta_contrato, exist_ok=True)

                # 2. Extrai o nome original do arquivo a partir da URL
                nome_arquivo = link_final.split('/')[-1].split('?')[0]
                
                # 3. Lógica crucial: Se não terminar com .pdf, nós adicionamos!
                if not nome_arquivo.lower().endswith('.pdf'):
                    nome_arquivo += ".pdf"
                
                caminho_salvamento = os.path.join(pasta_contrato, nome_arquivo)
                
                # 4. Faz o download do binário (Stream)
                print(f"-> Baixando e salvando como: {nome_arquivo}...")
                with requests.get(link_final, headers=HEADERS, timeout=TIMEOUT, stream=True) as r:
                    r.raise_for_status()
                    with open(caminho_salvamento, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                print("   ✅ Download concluído com sucesso.\n")
                logging.info(f"Sucesso no download: {titulo} salvo como {nome_arquivo}")
                
                # Um pequeno delay de boa vizinhança para não sobrecarregar o servidor do Gov
                time.sleep(0.5)

            except Exception as e_download:
                print(f"   ❌ Erro ao baixar este contrato: {e_download}\n")
                logging.error(f"Erro no download do contrato {titulo}: {e_download}")

        tempo_total = tempo_execucao(inicio_execucao)
        logging.info(f'Tempo: {tempo_total}.')
        logging.info('------- ENCERRANDO -------\n')

if __name__ == "__main__":
    capturar_contratos()