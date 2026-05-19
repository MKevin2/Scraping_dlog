CONTRATOS = []

URL = "https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/contratos-dlog/dlog-2026"
BASE_URL = "https://www.gov.br"
TIMEOUT = 30

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

TERMO_INICIAL = "contrato nº"
FILTRO_URL_2026 = "contratos-dlog/dlog-2026/"