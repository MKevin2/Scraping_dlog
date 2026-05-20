import time
import os

def tempo_execucao(inicio):
    
    fim = time.time()
    duracao = fim - inicio
    
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    milissegundos = int((duracao % 1) * 1000)
    
    return f"{minutos}m {segundos}s {milissegundos}ms"
    