import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extrair_dados(html, termos, portal):
    soup = BeautifulSoup(html, "html.parser")
    resultados = []
    encontrados = set()

    base_url = portal['url']
    termos_lower = [termo.lower() for termo in termos]

    print("\n🔍 Iniciando busca por links <a>...")

    # 1. Procurar <a href> normais
    for link in soup.find_all("a", href=True):
        texto = link.get_text(separator=' ', strip=True).lower()
        href = link['href']
        if any(t in texto for t in termos_lower):
            url_completa = href if href.startswith("http") else urljoin(base_url, href)
            print(f"➡️ Encontrado link: {texto} → {url_completa}")
            if url_completa not in encontrados:
                resultados.append({
                    "orgao": portal['nome'],
                    "estado": portal['estado'],
                    "url": url_completa
                })
                encontrados.add(url_completa)

    # 2. Procurar <tr role="row" onclick="..."> que tenham texto com termos
    print("\n🔍 Buscando links em <tr role='row'>...")
    for tr in soup.find_all("tr", attrs={"role": "row"}, onclick=True):
        texto = tr.get_text(separator=' ', strip=True).lower()
        if any(t in texto for t in termos_lower):
            onclick = tr['onclick']
            match = re.search(r"'(.*?)'", onclick)
            if match:
                href = match.group(1)
                url_completa = href if href.startswith("http") else urljoin(base_url, href)
                print(f"➡️ Encontrado onclick: {texto} → {url_completa}")
                if url_completa not in encontrados:
                    resultados.append({
                        "orgao": portal['nome'],
                        "estado": portal['estado'],
                        "url": url_completa
                    })
                    encontrados.add(url_completa)
                    
    # 3. Varre todos os <a> com href (inclusive dentro de <h3>, <div>, etc.)
    for tag in soup.find_all(["div", "section", "tr", "li", "article"]):
        texto_bloco = tag.get_text(separator=' ', strip=True).lower()
        if any(t in texto_bloco for t in termos_lower):
            for link_tag in tag.find_all("a", href=True):
                href = link_tag["href"]
                url_completa = href if href.startswith("http") else urljoin(base_url, href)
                if url_completa not in encontrados:
                    resultados.append({
                        "orgao": portal["nome"],
                        "estado": portal["estado"],
                        "url": url_completa
                    })
                    encontrados.add(url_completa)

    print(f"\n✅ Total encontrado: {len(resultados)} links.")
    return resultados


