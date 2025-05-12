import os
import json
import time
from pathlib import Path
import pandas as pd
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from undetected_chromedriver import Chrome, ChromeOptions
from .browser import iniciar_navegador
from .parser import extrair_dados
from .utils import tirar_screenshot, log

class CloudFlareSolver:
    def __init__(self, driver):
        self.driver = driver
        
    def is_cloudflare_challenge(self):
        try:
            return "cloudflare" in self.driver.page_source.lower() or \
                   self.driver.find_elements(By.XPATH, "//div[@class='cf-challenge-container']")
        except:
            return False
            
    def solve_cloudflare(self, timeout=30):
        try:
            log("🔍 Detectado desafio do Cloudflare, tentando resolver...")
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@title, 'Widget')]"))
            )
            checkbox = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']"))
            )
            ActionChains(self.driver).move_to_element(checkbox).pause(1).click().perform()
            log("✅ Checkbox do Cloudflare clicado")
            self.driver.switch_to.default_content()
            time.sleep(5)
            if "challenge-complete" in self.driver.page_source.lower():
                log("🎉 Desafio do Cloudflare resolvido com sucesso!")
                return True
        except Exception as e:
            log(f"⚠️ Falha ao resolver Cloudflare: {str(e)}")
            self.driver.switch_to.default_content()
        return False

def processar_portais(termos):
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / 'config' / 'portais.json'
    
    with open(config_path, encoding='utf-8') as f:
        portais = json.load(f)

    resultados = []
    for idx, portal in enumerate(portais):
        navegador = None
        try:
            log(f"Iniciando {portal.get('nome')} ({portal.get('estado')})")
            options = ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--start-maximized")
            
            navegador = Chrome(options=options)
            navegador.set_page_load_timeout(60)
            navegador.get(portal['url'])

            if 'filtro_xpath' in portal:
                try:
                    filtro_btn = WebDriverWait(navegador, 5).until(
                        EC.element_to_be_clickable((By.XPATH, portal['filtro_xpath']))
                    )
                    filtro_btn.click()
                    log("📂 Filtro expandido com sucesso")
                    time.sleep(1)
                except Exception as e:
                    log(f"⚠️ Não foi possível expandir o filtro: {str(e)}")
            
            try:
                cookie_btn = WebDriverWait(navegador, 3).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'Aceitar') or contains(., 'Concordar') or contains(., 'Aceito')]")
                    )
                )
                cookie_btn.click()
                log("✅ Cookies aceitos")
                time.sleep(1)
            except (TimeoutException, NoSuchElementException):
                log("⚠️ Botão de cookies não encontrado - continuando sem aceitar")
            except Exception as e:
                log(f"⚠️ Erro ao tentar aceitar cookies: {str(e)}")

            campo_busca = WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, portal['busca_xpath']))
            )
            campo_busca.clear()
            
            for char in " ".join(termos):
                campo_busca.send_keys(char)
                time.sleep(0.1)
            log(f"📝 Termo de busca preenchido: {' '.join(termos)}")

            # ✅ Ajusta quantidade de itens, se definido no JSON
            if "lista_xpath" in portal:
                try:
                    lista_info = portal["lista_xpath"]
                    select_element = WebDriverWait(navegador, 10).until(
                        EC.presence_of_element_located((By.XPATH, lista_info["xpath"]))
                    )
                    Select(select_element).select_by_value(lista_info["valor"])
                    log(f"📄 Quantidade de itens ajustada para {lista_info['valor']}")
                    time.sleep(1)
                except Exception as e:
                    log(f"⚠️ Erro ao ajustar quantidade de itens: {e}")

            # Executa a busca
            if portal.get('usar_enter', False):
                campo_busca.send_keys(Keys.ENTER)
                log("⏎ ENTER pressionado")
                time.sleep(1)
            else:
                try:
                    botao = WebDriverWait(navegador, 5).until(
                        EC.element_to_be_clickable((By.XPATH, portal['botao_xpath']))
                    )
                    navegador.execute_script("arguments[0].scrollIntoView(true);", botao)
                    time.sleep(0.5)
                    botao.click()
                    log("🖱️ Botão de consulta clicado")
                except Exception as e:
                    log(f"⚠️ Erro ao clicar no botão: {str(e)}")
                    campo_busca.send_keys(Keys.ENTER)
                    log("⏎ Fallback: ENTER pressionado")

            # Espera variável conforme índice do portal
            tempo_espera = 20 if idx < 14 else 55
            log(f"⏳ Aguardando {tempo_espera} segundos para carregamento dos resultados...")
            time.sleep(tempo_espera)
                        
            dados = extrair_dados(navegador.page_source, termos, portal)
            for dado in dados:
                dado.update({
                    "Órgão": portal.get('nome'),
                    "Estado": portal.get('estado'),
                    "URL": portal.get('url')
                })
            resultados.extend(dados)

        except TimeoutException:
            log(f"⏰ Timeout em {portal.get('nome')} ({portal.get('estado')}): {portal['url']}")
        except Exception as e:
            if navegador:
                screenshot_dir = base_dir / 'screenshots'
                screenshot_dir.mkdir(exist_ok=True)
                screenshot_path = screenshot_dir / f"{portal.get('estado', 'erro')}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                tirar_screenshot(navegador, str(screenshot_path))
            log(f"❌ Erro em {portal.get('nome')} ({portal.get('estado')}): {str(e)}")
        finally:
            if navegador:
                try:
                    navegador.quit()
                    log("🛑 Navegador fechado")
                    time.sleep(1)
                except:
                    pass

    if resultados:
        df = pd.DataFrame(resultados)
        colunas_fixas = ['Órgão', 'Estado', 'URL']
        outras_colunas = [col for col in df.columns if col not in colunas_fixas]
        df = df[colunas_fixas + outras_colunas]

        excel_path = base_dir / f"{termos}_resultados.xlsx"  # Corrigido nome do arquivo

        # Se o arquivo já existir, carregue os dados antigos e concatene
        if excel_path.exists():
            df_existente = pd.read_excel(excel_path, engine='openpyxl')
            df = pd.concat([df_existente, df], ignore_index=True)
            df.drop_duplicates(inplace=True)  # Opcional: remove linhas repetidas

        df.to_excel(excel_path, index=False, engine='openpyxl')
        log(f"💾 Planilha Excel gerada em: {excel_path}")


    return resultados
