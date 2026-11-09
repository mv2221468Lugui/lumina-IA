"""Simulações financeiras puras, sem modificar dados persistidos."""
from math import isfinite

CATEGORIAS = ('Energia', 'Água', 'Alimentação', 'Transporte')

def simular_economia(custos, renda, metas):
    """Retorna economia e orçamento projetado a partir de percentuais 0..100."""
    if not isfinite(float(renda)) or float(renda) < 0:
        raise ValueError('Renda inválida')
    base = {}
    for categoria, valor in custos.items():
        valor = float(valor)
        if not isfinite(valor) or valor < 0:
            raise ValueError('Despesa inválida')
        base[categoria] = valor
    for categoria, percentual in metas.items():
        if categoria not in base or not isfinite(float(percentual)) or not 0 <= float(percentual) <= 100:
            raise ValueError('Meta inválida')
    projetado = {cat: round(valor * (1 - float(metas.get(cat, 0)) / 100), 2) for cat, valor in base.items()}
    gasto_atual = round(sum(base.values()), 2)
    gasto_futuro = round(sum(projetado.values()), 2)
    return {'gasto_atual': gasto_atual, 'gasto_projetado': gasto_futuro,
            'economia': round(gasto_atual - gasto_futuro, 2),
            'saldo_atual': round(float(renda) - gasto_atual, 2),
            'saldo_projetado': round(float(renda) - gasto_futuro, 2),
            'por_categoria': projetado}
