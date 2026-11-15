"""Importação validada de medições externas para análise preditiva experimental."""
import pandas as pd
from inteligencia_ml import avaliar_knn, prever_knn
from datetime import timedelta


def ler_historico_csv(arquivo):
    try:
        df = pd.read_csv(arquivo, sep=None, engine='python', encoding='utf-8-sig')
    except Exception as exc:
        raise ValueError('CSV inválido ou ilegível. Use cabeçalho data,kwh.') from exc
    df.columns = [str(c).strip().lower() for c in df.columns]
    if not {'data','kwh'}.issubset(df.columns):
        raise ValueError('O CSV precisa conter as colunas data e kwh.')
    df = df[['data','kwh']].copy()
    df['data'] = pd.to_datetime(df['data'], errors='coerce', format='%Y-%m-%d')
    df['kwh'] = pd.to_numeric(df['kwh'].astype(str).str.replace(',','.',regex=False),errors='coerce')
    if df.isna().any().any() or (df.kwh < 0).any():
        raise ValueError('Datas devem estar em AAAA-MM-DD e kWh deve ser numérico e não negativo.')
    if df.data.duplicated().any():
        raise ValueError('Existem datas repetidas. Forneça um total de kWh por dia.')
    df = df.sort_values('data')
    if len(df) < 14:
        raise ValueError('São necessários pelo menos 14 dias de medições para avaliação.')
    if (df.data.diff().dropna().dt.days != 1).any():
        raise ValueError('O histórico deve ter dias consecutivos, sem lacunas.')
    return [(r.data.date(),float(r.kwh)) for r in df.itertuples(index=False)]


def analisar_consumo_real(historico):
    if len(historico) < 14:
        raise ValueError('São necessários pelo menos 14 dias.')
    dias_teste = max(3,round(len(historico)*0.2))
    mae, _ = avaliar_knn(historico,dias_teste=dias_teste)
    proximo = historico[-1][0]+timedelta(days=1)
    return {'mae':mae,'data_previsao':proximo,
            'previsao_kwh':prever_knn(historico,proximo), 'amostras':len(historico)}
