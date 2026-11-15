# Lumina AI 2050 — Edição Premium

## Abrir no Windows
1. Extraia o ZIP, abra a pasta e clique em `INICIAR_WINDOWS.bat`.
2. Se necessário, execute `python -m pip install -r requirements.txt` e `python -m streamlit run app.py`.
3. Abra http://localhost:8501 no mesmo computador.

## Funcionalidades
- Visão Geral com novos gráficos de curva e rosca.
- Análise Inteligente: Sankey, mapa de calor e KNN didático com dados sintéticos.
- Laboratório de Economia: simulações de metas.
- Assistente Lumina: respostas locais baseadas em regras (sem Gemini nesta versão).
- Minha Smart Home: planta interativa offline, celular virtual para luzes e sensores, e maquete 3D opcional (internet necessária).
- Despensa Inteligente: inventário, alertas e alterações persistidas em `cliente_demo.db`.
- Minhas Despesas: CRUD de registros reais em `lumina.db` separado da demonstração, exportação CSV e exclusão por ID.

## Segurança e preservação
Não incluímos nem sobrescrevemos `lumina.db`. Faça backup dos seus bancos antes de atualizar. O arquivo `cliente_demo.db` foi copiado do envio original. Dados de sensores, família e previsões de demonstração são fictícios. Não existem dispositivos físicos conectados. Não inclua chaves de API no projeto.

## Testes
Execute `python run_tests.py`. Os testes usam bancos temporários; não altere `lumina.db` para testá-los.
