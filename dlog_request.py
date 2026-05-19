import requests
from bs4 import BeautifulSoup
from config import URL, BASE_URL, TIMEOUT, HEADERS, TERMO_INICIAL, FILTRO_URL_2026, CONTRATOS

def capturar_contratos():
    try:
        print("Conectando ao site e analisando a estrutura...")
        response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)

        contador = 0

        for link in links:
            href = link['href'].lower()
            texto = link.get_text().strip()
            texto_minusculo = texto.lower()

            if texto_minusculo.startswith(TERMO_INICIAL) and FILTRO_URL_2026 in href:
                link_final = link['href']
                if not link_final.startswith('http'):
                    link_final = BASE_URL + link_final

                contador += 1

                CONTRATOS.append((contador, texto, link_final))

        if contador == 0:
            print("Nenhum contrato localizado.")

        else:
            print(f"Sucesso! {len(CONTRATOS)} contratos encontrados.")

    except Exception as e:
        print(f"Erro: {e}")

    for contador, texto, link_final in CONTRATOS:
        print(f"{contador}: {texto}\n{link_final}\n")

if __name__ == "__main__":
    capturar_contratos()