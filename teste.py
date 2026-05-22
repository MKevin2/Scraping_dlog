import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 1. URL correta da listagem de contratos DLOG 2026
url_pagina = "https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/contratos-dlog/dlog-2026" 

# 2. Configuração de Headers robusta para evitar o bloqueio do Gov.br
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-PT,pt;q=0.8,en-US;q=0.5,en;q=0.3'
}

pasta_destino = "arquivos_dlog_2026"
os.makedirs(pasta_destino, exist_ok=True)

print("A aceder à página principal do DLOG...")
resposta = requests.get(url_pagina, headers=headers)
soup = BeautifulSoup(resposta.text, 'html.parser')

# 3. Localizar os links dos contratos
# No padrão do Gov.br, o conteúdo principal costuma estar dentro da ID 'parent-fieldname-text' ou classes similares
links_encontrados = 0

for link in soup.find_all('a'):
    href = link.get('href')
    texto_link = link.get_text().strip()
    
    if href and "contrato" in href.lower():
        url_contrato = urljoin(url_pagina, href)
        
        if "dlog-2026" in url_contrato:
            print(f"\nA extrair informações de: {texto_link}")
            
            try:
                resposta_contrato = requests.get(url_contrato, headers=headers)
                soup_contrato = BeautifulSoup(resposta_contrato.text, 'html.parser')
                
                conteudo_principal = soup_contrato.find(id="parent-fieldname-text")
                if not conteudo_principal:
                    conteudo_principal = soup_contrato.find(class_="parent-fieldname-text")
                
                if conteudo_principal:
                    texto_completo = conteudo_principal.get_text(separator="\n").strip()
                    
                    # Define um nome seguro para o ficheiro de texto baseado no link
                    nome_seguro = href.split('/')[-1] + ".txt"
                    caminho_arquivo = os.path.join(pasta_destino, nome_seguro)
                    
                    # 5. Guarda a informação extraída no ficheiro
                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        f.write(f"Origem: {url_contrato}\n")
                        f.write("-" * 50 + "\n")
                        f.write(texto_completo)
                    
                    print(f"✅ Guardado com sucesso em: {nome_seguro}")
                    links_encontrados += 1
                else:
                    print("⚠️ Não foi possível encontrar a caixa de texto principal deste contrato.")
                    
            except Exception as e:
                print(f"❌ Erro ao aceder ao contrato {texto_link}: {e}")

if links_encontrados == 0:
    print("\nNenhum contrato foi extraído. Verifique se a estrutura da página sofreu alterações.")
else:
    print(f"\nFim do processo. {links_encontrados} ficheiros guardados na pasta '{pasta_destino}'.")