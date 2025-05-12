import json

def salvar_resultados(resultados):
    urls_unicas = set()
    with open("resultados.txt", "w", encoding="utf-8") as f:
        for item in resultados:
            if item['url'] not in urls_unicas:
                f.write(f"{item['orgao']} - {item['url']}\n")
                urls_unicas.add(item['url'])

