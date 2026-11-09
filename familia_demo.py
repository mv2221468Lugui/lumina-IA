"""Cenário educacional fictício, determinístico e isolado de lumina.db."""
from datetime import date, timedelta
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

SALARIO_REFERENCIA = 1621.0  # premissa fictícia de demonstração, não cotação oficial
RENDA = 3 * SALARIO_REFERENCIA
CUSTOS = {
    'Moradia': 1150.0, 'Alimentação': 1320.0, 'Energia': 430.0,
    'Água': 175.0, 'Transporte': 610.0, 'Internet e celular': 185.0,
    'Educação': 240.0, 'Saúde': 190.0, 'Outros': 285.0,
}
COR = '#36d8f3'

def brl(v):
    return ('R$ {:,.2f}'.format(v)).replace(',', 'X').replace('.', ',').replace('X', '.')

@st.cache_data(show_spinner=False)
def dados_demo():
    rng = random.Random(2050)
    inicio = date(2026, 10, 1)
    linhas = []
    for categoria, mensal in CUSTOS.items():
        pesos = [rng.uniform(0.45, 1.65) for _ in range(30)]
        if categoria == 'Moradia':
            pesos = [0.0]*30
            pesos[4] = 1.0
        soma = sum(pesos)
        valores = [round(mensal * p / soma, 2) for p in pesos]
        valores[-1] = round(valores[-1] + mensal - sum(valores), 2)
        for i, valor in enumerate(valores):
            linhas.append({'data': inicio + timedelta(days=i), 'categoria': categoria, 'valor': valor})
    gastos = pd.DataFrame(linhas)
    sensores = []
    for i in range(30):
        dia = inicio + timedelta(days=i)
        fim_semana = dia.weekday() >= 5
        for hora in range(24):
            base = 0.14 + (0.38 if 18 <= hora <= 23 else 0) + (0.23 if 6 <= hora <= 8 else 0)
            base += (0.16 if fim_semana and 10 <= hora <= 17 else 0)
            sensores.append({'data': dia, 'dia': i+1, 'hora': hora,
                             'kwh': round(max(.03, base + rng.uniform(-.06, .08)), 3)})
    energia = pd.DataFrame(sensores)
    agua = pd.DataFrame([{'data': inicio+timedelta(days=i), 'm3': round(.38 + rng.uniform(-.09,.12), 3)} for i in range(30)])
    return gastos, energia, agua

def exibir_familia_demo():
    gastos, energia, agua = dados_demo()
    total = float(gastos.valor.sum())
    saldo = RENDA-total
    consumo = energia.kwh.sum()
    agua_total = agua.m3.sum()
    st.markdown('## 🏠 Família 2050 | Central de Inteligência')
    st.caption('EXPO TECH 2026 · DEMONSTRAÇÃO AUTOMÁTICA · OUTUBRO 2026 (30 DIAS)')
    st.info('🧪 Todos os personagens, salários, despesas e leituras de sensores desta página são **fictícios**. Nenhum dado é gravado no banco lumina.db.')
    st.markdown('**Cenário pronto:** pai, mãe e dois filhos moram na Smart Home 2050. Para esta simulação, três integrantes da família recebem uma renda mensal equivalente a um salário mínimo de referência cada. O valor de referência de R$ 1.621 é uma premissa da demonstração, não uma verificação da legislação vigente.')
    c1,c2,c3,c4=st.columns(4)
    c1.metric('👨‍👩‍👧‍👦 Moradores', '4 pessoas')
    c2.metric('💼 Renda familiar', brl(RENDA), '3 rendas simuladas')
    c3.metric('💳 Gastos em 30 dias', brl(total))
    c4.metric('💰 Saldo do mês', brl(saldo))
    c5,c6,c7=st.columns(3)
    c5.metric('⚡ Energia estimada', f'{consumo:.1f} kWh')
    c6.metric('💧 Água estimada', f'{agua_total:.1f} m³')
    c7.metric('📅 Período analisado', '01–30/10/2026')
    st.markdown('### 🔎 Onde o dinheiro foi parar?')
    totais=gastos.groupby('categoria',as_index=False).valor.sum().sort_values('valor',ascending=False)
    labels=['Renda familiar','Gastos','Saldo disponível']+totais.categoria.tolist()
    fig=go.Figure(go.Sankey(
        node=dict(label=labels, pad=17, thickness=17, color=['#36d8f3','#fb923c','#4ade80']+['#64748b']*len(totais)),
        link=dict(source=[0,0]+[1]*len(totais),target=[1,2]+list(range(3,3+len(totais))),
                  value=[total,max(saldo,0)]+totais.valor.tolist())))
    fig.update_layout(height=430, margin=dict(l=5,r=5,t=10,b=10), font_size=12)
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    a,b=st.columns([1.2,1])
    with a:
        diario=gastos.groupby('data',as_index=False).valor.sum()
        acumulado=diario.copy()
        acumulado['acumulado']=acumulado.valor.cumsum()
        f=px.area(acumulado,x='data',y='acumulado',title='Evolução acumulada dos gastos — 30 dias',labels={'data':'Dia','acumulado':'R$ acumulados'})
        f.update_traces(line_color=COR)
        st.plotly_chart(f,use_container_width=True)
    with b:
        f=px.bar(totais,x='valor',y='categoria',orientation='h',title='Categorias que mais pesaram',labels={'valor':'R$ no mês','categoria':''})
        f.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(f,use_container_width=True)
    st.markdown('### 🌡️ Mapa de calor: quando a casa consome mais?')
    mapa=energia.pivot(index='hora',columns='dia',values='kwh')
    f=px.imshow(mapa,labels={'x':'Dia de outubro','y':'Hora do dia','color':'kWh'},aspect='auto',color_continuous_scale='Turbo',title='Consumo elétrico simulado por hora e por dia')
    st.plotly_chart(f,use_container_width=True)
    pico=energia.groupby('hora').kwh.mean().idxmax()
    st.markdown('### 🧠 Diagnóstico automático')
    maior=totais.iloc[0]
    st.write(f'**Maior categoria:** {maior.categoria}, com {brl(maior.valor)} ({maior.valor/total:.1%} dos gastos).')
    st.write(f'**Horário crítico de energia:** por volta das {int(pico):02d}h, conforme os sensores simulados. Vale investigar iluminação e aparelhos ligados nesse período.')
    st.write(f'**Orçamento:** {total/RENDA:.1%} da renda fictícia foi comprometida. Saldo disponível: {brl(saldo)}.')
    st.markdown('### 🔮 Novembro: plano pronto de melhoria')
    # Metas fixas para que ninguém precise preencher formulários.
    metas={'Energia': .15, 'Água': .10, 'Alimentação': .08, 'Transporte': .05}
    proj=totais.copy()
    proj['economia']=proj.apply(lambda r: round(r.valor*metas.get(r.categoria,0),2),axis=1)
    proj['novembro']=proj.valor-proj.economia
    economia=float(proj.economia.sum())
    futuro=total-economia
    x,y,z=st.columns(3)
    x.metric('Outubro · observado na simulação',brl(total))
    y.metric('Novembro · cenário com metas',brl(futuro),f'-{brl(economia)}')
    z.metric('Economia potencial',f'{economia/total:.1%}')
    comp=proj.melt(id_vars='categoria',value_vars=['valor','novembro'],var_name='periodo',value_name='R$')
    comp['periodo']=comp.periodo.replace({'valor':'Outubro (simulado)','novembro':'Novembro (meta)'})
    st.plotly_chart(px.bar(comp,x='categoria',y='R$',color='periodo',barmode='group',title='Comparação automática: outubro × novembro'),use_container_width=True)
    st.markdown('**Plano de ação sugerido:** reduzir iluminação e climatização desnecessárias no horário de pico; observar vazamentos e banhos longos; usar alertas de validade da despensa para evitar desperdício; planejar deslocamentos.')
    st.caption('Novembro é uma projeção de metas, não um resultado real nem uma previsão estatística validada. A análise é automática e baseada em regras; não depende de API de IA.')
    st.markdown('### 📥 Evidências para a apresentação')
    st.download_button('Baixar despesas simuladas (CSV)',gastos.to_csv(index=False).encode('utf-8-sig'),'familia_2050_despesas_outubro.csv','text/csv')
    st.download_button('Baixar sensores simulados (CSV)',energia.to_csv(index=False).encode('utf-8-sig'),'familia_2050_sensores_outubro.csv','text/csv')
