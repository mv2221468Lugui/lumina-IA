# Lumina AI — Portal do Cliente | Entrega ExpoTech 2026

## Como iniciar (Windows)
1. Extraia o ZIP em uma pasta nova.
2. Faça backup de qualquer projeto anterior. **Não substitua nem apague `lumina.db`.**
3. No terminal desta pasta: `python -m pip install -r requirements.txt`
4. Execute: `python -m streamlit run app.py`.
5. Abra o endereço local indicado pelo Streamlit.

## O que já vem configurado
- Família fictícia de 4 moradores com 3 rendas mensais simuladas.
- Histórico determinístico de outubro de 2026 e projeção de novembro.
- Visão Geral, Análise Inteligente, Laboratório de Economia, Assistente Lumina, Minha Smart Home e Despensa Inteligente.
- Despensa com 10 produtos de exemplo, gravados no `cliente_demo.db` criado na primeira execução.
- Assistente local sem Gemini: responde perguntas previstas sobre finanças, energia, água, estoque, validade e estado virtual das luzes.
- Controles de iluminação e cenários da Smart Home 3D.

## Limitações e transparência
- Os valores, salários, sensores, consumo e previsões são **simulados**; não são medições reais.
- O chat é baseado em regras e consultas, não em IA generativa.
- A casa 3D precisa de acesso à internet para carregar Three.js pelo CDN.
- A renderização completa e as interações devem ser verificadas no navegador de apresentação.
- O `cliente_demo.db` preserva as alterações de estoque feitas durante o uso. Para um ambiente limpo, extraia novamente o ZIP em uma pasta nova; não apague bancos de projetos anteriores.

## Checklist antes da apresentação
- Abrir as seis páginas e verificar que não há erros.
- Perguntar ao chat sobre gastos, reposição, produtos vencidos e luzes.
- Alternar um cenário e conferir os interruptores e a resposta do chat.
- Atualizar uma quantidade da despensa e verificar o alerta.
- Conferir a casa 3D e a conexão com o CDN no computador que será usado.


## Melhorias alinhadas às disciplinas
- **NLP:** assistente de regras com reconhecimento de intenções por palavras-chave e sumarização baseada nos dados; não é um LLM nem RAG.
- **Gen AI / Prompt Engineering:** disciplina contextualizada no projeto; não há integração com modelo generativo nesta versão.
- **Machine Learning:** KNN supervisionado implementado em Python para estimar kWh/dia, com separação cronológica treino/teste e MAE.
- **Data Science:** gráficos, agregações e análise estatística IQR de valores atípicos.
- **AI-Driven Software Engineering:** testes `unittest`, GitHub Actions, instruções de revisão e documentação.
- **Deploy:** execução local por Streamlit; CI não é deploy.

Execute `python run_tests.py` para rodar os testes. O fluxo no GitHub só será comprovado depois de publicar o repositório e conferir o log da execução.

**Limites:** os dados são sintéticos e pequenos; o KNN é uma demonstração acadêmica, sem validação em dados reais. Não há redes neurais, GAN, XGBoost, RAG, aprendizado por reforço ou agente autônomo implementados.


## Preparação das apresentações
Consulte `docs/roteiros_por_disciplina.md` e `docs/checklist_apresentacao.md`. Cronograma: segunda Engenharia de Software (nome exato a validar); quarta NLP; quinta AI-Driven Software Engineering (Dani Monteiro); sexta Machine Learning e Deep Learning.

## Laboratório de Economia
O simulador interativo usa `simulador.py`, não grava no banco, e possui testes unitários em `tests/test_simulador.py`. Seus cenários são hipotéticos, não predições de IA.

## Regra adicional verificada
`regras_despensa.py` valida que quantidades não sejam negativas e classifica estoque e validade; testes em `tests/test_regras_despensa.py`.


## Atualização visual da Smart Home 3D

A casa recebeu acabamentos adicionais (rodapés, móveis, eletrodomésticos, roupa de cama, luminárias, paisagismo e detalhes da garagem e piscina), com iluminação, sombras e neblina visual refinadas. Os comandos existentes e a simulação de consumo foram preservados. É uma **maquete 3D ilustrativa**, não um modelo arquitetônico fotorealista ou integração com dispositivos físicos. Requer acesso à CDN do Three.js para renderizar.
