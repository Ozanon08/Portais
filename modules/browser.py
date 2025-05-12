from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from fake_useragent import UserAgent
import random
import time
import os
import re
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def iniciar_navegador(headless=False, proxy=None):
    # 1. Configuração do WebDriver com caminho absoluto
    edge_driver_path = r"C:\Users\rodrigo.zanon\Desktop\Feito\Python\4. PMO\App\Projeto 1\modules\msedgedriver.exe"
    
    if not os.path.exists(edge_driver_path):
        raise FileNotFoundError(f"EdgeDriver não encontrado em: {edge_driver_path}")

    # 2. Configurações avançadas de capabilities
    capabilities = DesiredCapabilities.EDGE.copy()
    capabilities['acceptInsecureCerts'] = True
    capabilities['pageLoadStrategy'] = 'eager'

    # 3. Configuração detalhada das opções
    options = EdgeOptions()
    
    # Configurações de stealth
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent dinâmico com versão correspondente ao navegador
    ua = UserAgent(browsers=['edge'])
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    
    # Configurações de janela e performance
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
    
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Configuração de proxy se fornecido
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    # 4. Inicialização do serviço com configurações extras
    service = EdgeService(
        executable_path=edge_driver_path,
        service_args=['--verbose'],
        capabilities=capabilities
    )

    try:
        # 5. Iniciação do navegador com proteções adicionais
        navegador = webdriver.Edge(service=service, options=options)
        
        # 6. Scripts avançados de stealth
        scripts = [
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array",
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise",
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol",
            "const newProto = navigator.__proto__",
            "delete newProto.webdriver",
            "navigator.__proto__ = newProto",
            "window.chrome = {app: {isInstalled: false}}",
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]})",
            "Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})",
            "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4})"
        ]
        
        for script in scripts:
            try:
                navegador.execute_script(script)
            except:
                pass
        
        # 7. Padrões de navegação humana
        navegador.execute_script(
            "window.onload = function() {"
            "  setTimeout(function(){"
            "    window.scrollBy({top: 500, behavior: 'smooth'});"
            "  }, 1500);"
            "}"
        )
        
        # 8. Delay humano inicial
        time.sleep(random.uniform(1.5, 3.5))
        
        return navegador
        
    except Exception as e:
        raise Exception(
            f"Falha crítica ao iniciar navegador. Causas possíveis:\n"
            f"1. Versão incompatível do EdgeDriver\n"
            f"2. Bloqueio por política corporativa\n"
            f"3. Conflito com antivírus\n"
            f"Erro detalhado: {str(e)}"
        )

def configurar_comportamento_humano(navegador):
    """Aplica padrões de comportamento humano no navegador"""
    try:
        # Variação de timezone e geolocalização
        navegador.execute_script(
            "Object.defineProperty(navigator, 'timezone', {value: 'America/Sao_Paulo'});"
            "Object.defineProperty(navigator, 'geolocation', {"
            "  get: function() {"
            "    return {"
            "      getCurrentPosition: function(success) {"
            "        success({"
            "          coords: {"
            "            latitude: -23.5505 + (Math.random() * 0.01 - 0.005),"
            "            longitude: -46.6333 + (Math.random() * 0.01 - 0.005)"
            "          }"
            "        });"
            "      }"
            "    };"
            "  }"
            "});"
        )
        
        # Alteração de resolução e cores
        navegador.execute_script(
            "Object.defineProperty(screen, 'width', {value: 1920});"
            "Object.defineProperty(screen, 'height', {value: 1080});"
            "Object.defineProperty(screen, 'colorDepth', {value: 24});"
        )
        
        # Mock de WebGL
        navegador.execute_script(
            "const getParameter = WebGLRenderingContext.prototype.getParameter;"
            "WebGLRenderingContext.prototype.getParameter = function(parameter) {"
            "  if (parameter === 37445) return 'Microsoft';"
            "  if (parameter === 37446) return 'ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)';"
            "  return getParameter(parameter);"
            "};"
        )
        
    except Exception as e:
        print(f"Aviso: Não foi possível configurar comportamento humano completo: {str(e)}")