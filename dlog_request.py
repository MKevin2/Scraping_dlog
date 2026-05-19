import requests
from bs4 import BeautifulSoup

contratos = []

URL = "https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/contratos-dlog/dlog-2026"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

def capturar_contratos():
    try:
        print("Conectando ao site e analisando a estrutura...")
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)

        contador = 0

        for link in links:
            href = link['href'].lower()
            texto = link.get_text().strip()
            texto_minusculo = texto.lower()

            if texto_minusculo.startswith("contrato nº") and "contratos-dlog/dlog-2026/" in href:
                link_final = link['href']
                if not link_final.startswith('http'):
                    link_final = "https://www.gov.br" + link_final

                contador += 1

                contratos.append((contador, texto, link_final))

        if contador == 0:
            print("Nenhum contrato localizado.")

        else:
            print(f"Sucesso! {contador} contratos encontrados.")

    except Exception as e:
        print(f"Erro: {e}")

    for contador, texto, link_final in contratos:
        print(f"{contador}: {texto}\n{link_final}\n")

if __name__ == "__main__":
    capturar_contratos()