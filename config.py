import os

links = []
links_25 = []
lista_extraida = []

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

PASTA_RAIZ = "arquivos_dlog"
PASTA_PDFS = os.path.join(PASTA_RAIZ, "pdfs")
PASTA_RESUMOS = os.path.join(PASTA_RAIZ, "resumos")

CONTRATOS = []
CONTRATOS_26 = []
CONTRATOS_25 = []

URL_26 = "https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/contratos-dlog/dlog-2026"
URL_25 = "https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/contratos-dlog/dlog-2025"

BASE_URL = "https://www.gov.br"
TERMO_INICIAL = "contrato nº"
TIMEOUT = 30

FILTRO_URL_26 = "contratos-dlog/dlog-2026/"
FILTRO_URL_25 = "contratos-dlog/dlog-2025/"
