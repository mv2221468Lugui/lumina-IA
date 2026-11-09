"""Regras testáveis da despensa; independentes do Streamlit e do banco."""
from datetime import date, timedelta
from math import isfinite

def validar_quantidade(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not isfinite(valor) or valor < 0:
        raise ValueError("A quantidade deve ser um número finito não negativo.")
    return float(valor)

def situacao_estoque(quantidade, minimo):
    quantidade = validar_quantidade(quantidade)
    minimo = validar_quantidade(minimo)
    return "repor" if quantidade <= minimo else "normal"

def situacao_validade(validade, referencia=None):
    if not validade:
        return "sem validade"
    referencia = referencia or date.today()
    dia = date.fromisoformat(validade) if isinstance(validade, str) else validade
    if dia < referencia:
        return "vencido"
    if dia <= referencia + timedelta(days=7):
        return "próximo do vencimento"
    return "válido"
