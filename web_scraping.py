import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import tempo_execucao
from config import URL, BASE_URL, TIMEOUT, HEADERS, TERMO_INICIAL, FILTRO_URL_2026, CONTRATOS
import logging

logging.basicConfig(
    level=logging.INFO, 
    filename='request.log', 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
        print(f"Erro na captura principal: {e}")
        logging.error(f"Automação gerou uma exceção! \n{e}")
        logging.info('------- ENCERRANDO -------\n')

    finally:
        if CONTRATOS:
            pasta_pdfs = os.path.join(pasta_destino_raiz, "pdfs")
            pasta_resumos = os.path.join(pasta_destino_raiz, "resumos")
            
            os.makedirs(pasta_pdfs, exist_ok=True)
            os.makedirs(pasta_resumos, exist_ok=True)
            
            for contador, titulo, link_final in CONTRATOS:
                print(f"{contador}: {titulo}\nURL: {link_final}")
                
                titulo_limpo = "".join(c for c in titulo if c.isalnum() or c in (' ', '_', '-', '.')).strip().replace(" ", "_")
                
                try:
                    response_conteudo = requests.get(link_final, headers=HEADERS, timeout=TIMEOUT)
                    response_conteudo.raise_for_status()
                    
                    content_type = response_conteudo.headers.get('Content-Type', '').lower()
                    
                    # CASO A: É uma página de resumo em HTML
                    if 'html' in content_type:
                        print("   -> Página de resumo detectada. Procurando anexos reais...")
                        
                        soup_interno = BeautifulSoup(response_conteudo.text, 'html.parser')
                        area_conteudo = soup_interno.find(id="parent-fieldname-text") or soup_interno.find(class_="parent-fieldname-text")
                        
                        if area_conteudo:
                            texto_resumo = area_conteudo.get_text(separator="\n").strip()
                            nome_txt = f"{titulo_limpo}_resumo.txt"
                            
                            with open(os.path.join(pasta_resumos, nome_txt), 'w', encoding='utf-8') as f:
                                f.write(texto_resumo)
                            print(f"      ✅ Resumo salvo em: resumos/{nome_txt}")
                            
                            links_anexos = area_conteudo.find_all('a', href=True)
                            anexos_baixados = 0
                            
                            for link_anexo in links_anexos:
                                href_anexo = link_anexo['href']
                                url_anexo_completa = urljoin(link_final, href_anexo)
                                
                                if any(excluir in url_anexo_completa.lower() for excluir in ['#', 'facebook', 'twitter', 'whatsapp', 'compartilhar']):
                                    continue
                                    
                                print(f"      ↳ Analisando anexo potencial: {link_anexo.get_text().strip()}")
                                
                                try:
                                    res_anexo = requests.get(url_anexo_completa, headers=HEADERS, timeout=TIMEOUT, stream=True)
                                    tipo_anexo = res_anexo.headers.get('Content-Type', '').lower()
                                    
                                    if 'pdf' in tipo_anexo or 'application/octet-stream' in tipo_anexo or 'download' in url_anexo_completa.lower():
                                        nome_pdf = f"{titulo_limpo}.pdf"
                                        caminho_pdf = os.path.join(pasta_pdfs, nome_pdf)
                                        
                                        print(f"      ↳ [CONFIRMADO] Baixando arquivo PDF do anexo...")
                                        with open(caminho_pdf, 'wb') as f_pdf:
                                            for chunk in res_anexo.iter_content(chunk_size=8192):
                                                f_pdf.write(chunk)

                                        print(f"      ✅ Arquivo salvo em: pdfs/{nome_pdf}")
                                        logging.info(f"Arquivo PDF salvo: {link_anexo.get_text().strip()}")
                                        anexos_baixados += 1      
                                        
                                except Exception as error_anexo:
                                    print(f"      ❌ Erro ao tentar acessar o link do anexo: {error_anexo}")
                                    logging.error(f"Automação gerou uma exceção! \n{e}")
                                    logging.info('------- ENCERRANDO -------\n')
                            
                            if anexos_baixados == 0:
                                print("   ⚠️ Nenhum anexo de arquivo válido foi localizado dentro do texto da página.")
                        else:
                            print("   ❌ Não foi possível mapear o corpo do texto desta página.")

                    # CASO B: É o PDF direto (como o caso do Contrato 01)
                    else:
                        print("   -> PDF direto detectado. Baixando arquivo...")
                        nome_arquivo_base = f"{titulo_limpo}.pdf"
                        caminho_salvamento = os.path.join(pasta_pdfs, nome_arquivo_base)
                        
                        with open(caminho_salvamento, 'wb') as f:
                            f.write(response_conteudo.content)
                            
                        print(f"   ✅ PDF direto baixado com sucesso: pdfs/{nome_arquivo_base}")
                    
                    print("-" * 50 + "\n")
                    time.sleep(0.5)

                except Exception as e_download:
                    print(f"   ❌ Erro ao processar o download deste contrato: {e_download}\n")
                    logging.error(f"Erro no processamento do contrato {titulo}: {e_download}")
                    logging.info('------- ENCERRANDO -------\n')

        tempo_total = tempo_execucao(inicio_execucao)
        logging.info(f'Tempo: {tempo_total}.')
        logging.info('------- ENCERRANDO -------\n')

if __name__ == "__main__":
    capturar_contratos()