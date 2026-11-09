"""Modelos didáticos determinísticos sobre dados sintéticos. Não há API externa.
KNN é aprendizado supervisionado; detecção IQR é regra estatística, não rede neural.
"""
from datetime import timedelta
from statistics import mean


def distancia_dias(a, b):
    """Distância cíclica entre dias da semana (0=segunda)."""
    diferenca = abs(a.weekday() - b.weekday())
    return min(diferenca, 7 - diferenca)


def prever_knn(historico, alvo, k=3):
    """Prevê kWh/dia por KNN usando dia da semana, sem vazamento do alvo."""
    if not historico or k < 1:
        raise ValueError('Histórico não vazio e k positivo são necessários.')
    vizinhos = sorted(historico, key=lambda item: (distancia_dias(item[0], alvo), abs((alvo-item[0]).days)))[:k]
    return mean(valor for _, valor in vizinhos)


def avaliar_knn(historico, dias_teste=7, k=3):
    """Treina nos primeiros dias e testa cronologicamente nos últimos dias."""
    if len(historico) <= dias_teste or dias_teste < 1:
        raise ValueError('É necessário ter dias de treino e teste.')
    ordenado = sorted(historico)
    treino, teste = ordenado[:-dias_teste], ordenado[-dias_teste:]
    previsoes = [(dia, real, prever_knn(treino, dia, k)) for dia, real in teste]
    mae = mean(abs(real-previsto) for _, real, previsto in previsoes)
    return mae, previsoes


def detectar_anomalias_iqr(historico, multiplicador=1.5):
    """Detecta extremos por intervalo interquartil, sem treinar modelo de ML."""
    valores = sorted(v for _, v in historico)
    if len(valores) < 4:
        return []
    def mediana(v):
        n=len(v)
        return (v[(n-1)//2]+v[n//2])/2
    metade=len(valores)//2
    q1=mediana(valores[:metade]); q3=mediana(valores[-metade:])
    margem=multiplicador*(q3-q1)
    return [(dia, v) for dia, v in historico if v < q1-margem or v > q3+margem]


def resumo_inteligente(historico):
    """Resumo em linguagem natural extraído de dados, não gerado por LLM."""
    mae, _ = avaliar_knn(historico)
    ultimo = max(d for d, _ in historico)
    proximo = ultimo + timedelta(days=1)
    previsao = prever_knn(historico, proximo)
    anomalias = detectar_anomalias_iqr(historico)
    return {'mae': mae, 'data_previsao': proximo, 'previsao_kwh': previsao,
            'anomalias': anomalias, 'amostras': len(historico)}
