from modules.scraper import processar_portais
from modules.storage import salvar_resultados
from modules.utils import gerar_estatisticas

termos = input("Digite os termos de busca separados por vírgula: ").split(',')
resultados = processar_portais(termos)

salvar_resultados(resultados)
gerar_estatisticas(resultados)
