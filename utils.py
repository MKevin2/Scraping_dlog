import time
import os

def tempo_execucao(inicio):
    
    fim = time.time()
    duracao = fim - inicio
    
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    
    return f"{minutos}m {segundos}s"