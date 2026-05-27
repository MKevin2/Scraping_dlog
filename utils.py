import os
import time
from config import PASTA_PDFS
from config import PASTA_RESUMOS

def tempo_execucao(inicio):
    
    fim = time.time()
    duracao = fim - inicio
    
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    milissegundos = int((duracao % 1) * 1000)
    
    return f"{minutos}m {segundos}s {milissegundos}ms"


def inicializar_diretorios():
    os.makedirs(PASTA_PDFS, exist_ok=True)
    os.makedirs(PASTA_RESUMOS, exist_ok=True)

    