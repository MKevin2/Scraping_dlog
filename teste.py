import os
import time
import logging
import requests
import numpy as np
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import inicializar_diretorios, tempo_execucao
from config import CONTRATOS_25, CONTRATOS_26, FILTRO_URL_25, FILTRO_URL_26, URL_25, URL_26, BASE_URL, PASTA_PDFS, PASTA_RESUMOS, TIMEOUT, HEADERS, TERMO_INICIAL, CONTRATOS, links, links_25

logging.basicConfig(
    level=logging.INFO, 
    filename='request.log', 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extrair_links(url):

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup.find_all('a', href=True)
    
    except Exception as e:
        logging.error(f"Erro ao acessar a URL {url}: {e}")
        print(f"Erro ao conectar com {url}: {e}")
        
        return []


def filtrar_e_classificar_links(links_25, links_26):

    contador = 0

    for link in (links_25 + links_26):
        href = link['href'].lower()
        titulo = link.get_text().strip()
        titulo_minusculo = titulo.lower()

        if not titulo_minusculo.startswith(TERMO_INICIAL):
            continue

        link_final = link['href'] if link['href'].startswith('http') else BASE_URL + link['href']

        if FILTRO_URL_26 in href:
            contador += 1
            CONTRATOS_26.append((contador, titulo, link_final))
            CONTRATOS.append((contador, titulo, link_final))

        elif FILTRO_URL_25 in href:
            contador += 1
            CONTRATOS_25.append((contador, titulo, link_final))
            CONTRATOS.append((contador, titulo, link_final))

    return contador


def limpar_nome_arquivo(titulo):

    caracteres_validos = "".join(c for c in titulo if c.isalnum() or c in (' ', '_', '-', '.'))
    
    return caracteres_validos.strip().replace(" ", "_")


def baixar_anexo_pdf(url_anexo, titulo_limpo, link_origem):

    try:
        res_anexo = requests.get(url_anexo, headers=HEADERS, timeout=TIMEOUT, stream=True)
        tipo_anexo = res_anexo.headers.get('Content-Type', '').lower()
        
        if 'pdf' in tipo_anexo or 'application/octet-stream' in tipo_anexo or 'download' in url_anexo.lower():
            caminho_pdf = os.path.join(PASTA_PDFS, f"{titulo_limpo}.pdf")
            print("      ↳ [CONFIRMADO] Baixando arquivo PDF do anexo...")
            
            with open(caminho_pdf, 'wb') as f_pdf:
                for chunk in res_anexo.iter_content(chunk_size=8192):
                    f_pdf.write(chunk)
            
            print(f"      ✅ Arquivo salvo em: pdfs/{titulo_limpo}.pdf")
            return True
        
    except Exception as e:
        print(f"      ❌ Erro ao acessar anexo: {e}")

    return False


def processar_pagina_resumo(html_text, titulo_limpo, url_origem):

    soup_interno = BeautifulSoup(html_text, 'html.parser')
    area_conteudo = soup_interno.find(id="parent-fieldname-text") or soup_interno.find(class_="parent-fieldname-text")
    
    if not area_conteudo:
        print("   ❌ Não foi possível mapear o corpo do texto desta página.")
        
        return

    texto_resumo = area_conteudo.get_text(separator="\n").strip()
    nome_txt = f"{titulo_limpo}_resumo.txt"
    
    with open(os.path.join(PASTA_RESUMOS, nome_txt), 'w', encoding='utf-8') as f:
        f.write(texto_resumo)

    print(f"   ✅ Resumo salvo em: resumos/{nome_txt}")

    links_anexos = area_conteudo.find_all('a', href=True)
    anexos_baixados = 0
    
    for link_anexo in links_anexos:
        url_anexo_completa = urljoin(url_origem, link_anexo['href'])
        
        if any(excluir in url_anexo_completa.lower() for excluir in ['#', 'facebook', 'twitter', 'whatsapp', 'compartilhar']):
            continue
            
        print(f"      ↳ Analisando anexo potencial: {link_anexo.get_text().strip()}")
        
        if baixar_anexo_pdf(url_anexo_completa, titulo_limpo, url_origem):
            anexos_baixados += 1

    if anexos_baixados == 0:
        print("   ⚠️ Nenhum anexo de arquivo válido foi localizado dentro do texto da página.")


def baixar_contratos():
    if not CONTRATOS:
        
        return

    inicializar_diretorios()

    for contador, titulo, link_final in CONTRATOS:
        print(f"{contador}: {titulo}\nURL: {link_final}")
        titulo_limpo = limpar_nome_arquivo(titulo)
        
        try:
            resposta = requests.get(link_final, headers=HEADERS, timeout=TIMEOUT)
            resposta.raise_for_status()
            tipo_resposta = resposta.headers.get('Content-Type', '').lower()
            
            if 'html' in tipo_resposta:
                print("   -> Página de resumo detectada. Procurando anexos reais...")
                processar_pagina_resumo(resposta.text, titulo_limpo, link_final)
            
            else:
                print("   -> PDF direto detectado. Baixando arquivo...")
                caminho_salvamento = os.path.join(PASTA_PDFS, f"{titulo_limpo}.pdf")
                
                with open(caminho_salvamento, 'wb') as f:
                    f.write(resposta.content)
                
                print(f"   ✅ PDF direto baixado com sucesso: pdfs/{titulo_limpo}.pdf")
            
            print("-" * 50 + "\n")
            time.sleep(0.5)

        except Exception as e_download:
            
            print(f"   ❌ Erro ao processar este contrato: {e_download}\n")
            logging.error(f"Erro no processamento do contrato {titulo}: {e_download}")


def capturar_contratos():
    inicio_execucao = time.time()
    logging.info('------- INICIANDO -------')
    print("\nConectando ao site e analisando a estrutura...\n")
    
    try:

        array_paginas = np.arange(0, 331, 30, dtype=int)
        lista_array = [int(x) for x in array_paginas]

        for pag in lista_array:
            links.append(f'{URL_25}?b_start:int={pag}')

        for extracao in links:
            lista_extraida = extrair_links(extracao)
            links_25.extend(lista_extraida)

        links_26 = extrair_links(URL_26)

        total_encontrados = filtrar_e_classificar_links(links_26, links_25)

        if total_encontrados == 0:
            logging.info("Nenhum contrato localizado.")
            
            print("Nenhum contrato localizado.")
            
            return
            
        logging.info(f"Contrato(s): {len(CONTRATOS)} encontrados.")

        baixar_contratos()

    except Exception as e:
        print(f"Erro na captura principal: {e}")
        logging.error(f"Automação gerou uma exceção geral! \n{e}")
    
    finally:
        tempo_total = tempo_execucao(inicio_execucao)
        logging.info(f'Tempo: {tempo_total}.')
        logging.info('------- ENCERRANDO -------\n')

if __name__ == "__main__":
    capturar_contratos()