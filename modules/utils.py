from datetime import datetime
import os

def tirar_screenshot(navegador, nome):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    navegador.save_screenshot(f"output/falha_{nome}_{ts}.png")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def gerar_estatisticas(dados):
    from collections import Counter
    contagem = Counter([d["estado"] for d in dados])
    print("Estatísticas por estado:")
    for estado, qtd in contagem.items():
        print(f"{estado}: {qtd}")
