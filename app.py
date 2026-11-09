import sqlite3
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from familia_demo import dados_demo, RENDA, brl, CUSTOS
from smart_home_3d import exibir_smart_home_3d, obter_resumo_consumo
from inteligencia_ml import resumo_inteligente
from regras_despensa import validar_quantidade
from simulador import simular_economia, CATEGORIAS

st.set_page_config(page_title="Lumina AI | Minha Casa",page_icon="🏠",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
.stApp {background:linear-gradient(135deg,#061122,#0b1d32 70%,#061122);color:#eaf4ff}
[data-testid="stSidebar"] {background:#08172a}
[data-testid="stMetric"] {background:#102840;border:1px solid #224660;border-radius:14px;padding:16px}
h1,h2,h3 {color:#e8f9ff!important}
</style>""",unsafe_allow_html=True)
DB=Path(__file__).with_name('cliente_demo.db')
PRODUTOS=[('Arroz','Grãos e massas',3,'pacotes',2,'2027-04-20',22.5),('Feijão','Grãos e massas',1,'pacotes',2,'2027-02-18',9.8),('Leite','Laticínios',5,'litros',3,'2026-11-13',5.7),('Macarrão','Grãos e massas',4,'pacotes',2,'2027-03-01',6.5),('Óleo','Outros',1,'unidades',2,'2027-06-01',8.9),('Detergente','Limpeza',3,'unidades',2,'2027-09-01',3.5),('Café','Bebidas',2,'pacotes',2,'2027-01-15',18.0),('Tomate','Hortifruti',2,'kg',1,'2026-11-11',8.0),('Água mineral','Bebidas',8,'litros',4,'2027-05-10',2.5),('Farinha','Grãos e massas',2,'pacotes',1,'2027-05-22',7.0)]

def db():
    return sqlite3.connect(DB)

def iniciar_despensa():
    with db() as con:
        con.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, produto TEXT NOT NULL, categoria TEXT, quantidade REAL NOT NULL, unidade TEXT, minimo REAL, validade TEXT, preco REAL)')
        if con.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]==0:
            con.executemany('INSERT INTO produtos(produto,categoria,quantidade,unidade,minimo,validade,preco) VALUES(?,?,?,?,?,?,?)',PRODUTOS)

def produtos():
    with db() as con: return pd.read_sql_query('SELECT * FROM produtos ORDER BY categoria,produto',con)

gastos,energia,agua=dados_demo()
total=float(gastos.valor.sum()); saldo=RENDA-total
cats=gastos.groupby('categoria',as_index=False).valor.sum().sort_values('valor',ascending=False)
consumo=float(energia.kwh.sum()); agua_total=float(agua.m3.sum())
iniciar_despensa()

with st.sidebar:
    st.markdown('## ✦ LUMINA AI')
    st.caption('Sua casa. Suas decisões.')
    pagina=st.radio('Navegação',['Visão Geral','Análise Inteligente','Laboratório de Economia','Assistente Lumina','Minha Smart Home','Despensa Inteligente'],label_visibility='collapsed')
    st.divider()
    st.caption('👨‍👩‍👧‍👦 Residência familiar · 4 moradores')
    st.caption('Dados de demonstração · sensores simulados')

if pagina=='Visão Geral':
    st.title('🏠 Bem-vindo à sua casa')
    st.caption('Seu panorama financeiro e doméstico em um só lugar · Referência: outubro de 2026')
    a,b,c,d=st.columns(4)
    a.metric('Renda familiar',brl(RENDA));b.metric('Despesas do mês',brl(total));c.metric('Saldo disponível',brl(saldo));d.metric('Moradores','4')
    a,b,c=st.columns(3)
    a.metric('Energia',f'{consumo:.1f} kWh');b.metric('Água',f'{agua_total:.1f} m³');c.metric('Maior despesa',cats.iloc[0].categoria)
    l,r=st.columns([1.4,1])
    with l:
        diario=gastos.groupby('data',as_index=False).valor.sum(); diario['acumulado']=diario.valor.cumsum()
        st.plotly_chart(px.area(diario,x='data',y='acumulado',title='Evolução do orçamento',labels={'data':'Data','acumulado':'Total (R$)'}),use_container_width=True)
    with r: st.plotly_chart(px.bar(cats,x='valor',y='categoria',orientation='h',title='Para onde foi o dinheiro?',labels={'valor':'R$','categoria':''}),use_container_width=True)
    st.info('💡 Sugestão Lumina: revisar compras de alimentação e o consumo de energia no período noturno.')

elif pagina=='Análise Inteligente':
    st.title('📊 Análise Inteligente')
    st.caption('Histórico financeiro e planejamento de economia da residência')
    a,b,c=st.columns(3)
    a.metric('Gasto analisado',brl(total));b.metric('Renda comprometida',f'{total/RENDA:.1%}');c.metric('Saldo do período',brl(saldo))
    st.subheader('Fluxo do dinheiro')
    labels=['Renda familiar','Despesas','Saldo']+cats.categoria.tolist()
    sankey=go.Figure(go.Sankey(node=dict(label=labels,pad=18,thickness=18),link=dict(source=[0,0]+[1]*len(cats),target=[1,2]+list(range(3,len(labels))),value=[total,max(saldo,0)]+cats.valor.tolist())))
    sankey.update_layout(height=350,margin=dict(l=5,r=5,t=15,b=5))
    st.plotly_chart(sankey,use_container_width=True)
    st.subheader('Mapa de calor do consumo de energia')
    mapa=energia.pivot(index='hora',columns='dia',values='kwh')
    st.plotly_chart(px.imshow(mapa,aspect='auto',color_continuous_scale='Turbo',labels={'x':'Dia do mês','y':'Hora','color':'kWh'}),use_container_width=True)
    st.subheader('Plano de economia já calculado')
    metas={'Energia':.15,'Água':.10,'Alimentação':.08,'Transporte':.05}
    proj=cats.copy();proj['novembro']=proj.apply(lambda x:x.valor*(1-metas.get(x.categoria,0)),axis=1)
    economia=float((proj.valor-proj.novembro).sum())
    a,b,c=st.columns(3)
    a.metric('Mês analisado',brl(total));b.metric('Próximo mês projetado',brl(total-economia));c.metric('Economia potencial',brl(economia))
    long=proj.melt(id_vars='categoria',value_vars=['valor','novembro'],var_name='mes',value_name='R$')
    long['mes']=long.mes.replace({'valor':'Outubro','novembro':'Novembro (meta)'})
    st.plotly_chart(px.bar(long,x='categoria',y='R$',color='mes',barmode='group'),use_container_width=True)
    st.success('Plano recomendado: diminuir luzes desnecessárias, monitorar água, planejar compras e usar alertas de validade.')
    st.caption('Projeções hipotéticas baseadas em metas, não previsões garantidas.')
    st.subheader('🧪 Machine Learning aplicado à energia')
    serie = [(dia, float(kwh)) for dia, kwh in energia.groupby('data').kwh.sum().items()]
    ml = resumo_inteligente(serie)
    m1,m2,m3=st.columns(3)
    m1.metric('Previsão KNN · próximo dia',f"{ml['previsao_kwh']:.2f} kWh")
    m2.metric('Erro médio no teste (MAE)',f"{ml['mae']:.2f} kWh")
    m3.metric('Dias com consumo atípico (IQR)',len(ml['anomalias']))
    st.caption('KNN supervisionado com 3 vizinhos, usando o dia da semana. Treino: primeiros 23 dias; teste: últimos 7 dias. IQR é detecção estatística de extremos. Dados sintéticos: demonstração acadêmica, não previsão real nem Deep Learning.')
    if ml['anomalias']:
        st.info('Dias atípicos detectados: '+', '.join(f'{d:%d/%m} ({v:.1f} kWh)' for d,v in ml['anomalias']))
    st.subheader('Resumo automático do período')
    pico_hora=int(energia.groupby('hora').kwh.mean().idxmax())
    st.write(f'Em 30 dias, o consumo simulado foi de **{consumo:.1f} kWh**. O horário de maior consumo médio foi **{pico_hora:02d}h**. A categoria financeira mais cara foi **{cats.iloc[0].categoria}** ({brl(float(cats.iloc[0].valor))}). O modelo KNN estima **{ml["previsao_kwh"]:.2f} kWh** para {ml["data_previsao"]:%d/%m/%Y}, com erro médio de **{ml["mae"]:.2f} kWh** no conjunto de teste.')


elif pagina=='Laboratório de Economia':
    st.title('🎛️ Laboratório de Economia')
    st.caption('Experimente decisões e descubra o impacto no orçamento da família, sem alterar os dados salvos.')
    st.markdown('### E se a nossa família economizasse mais?')
    st.write('Ajuste as metas de cada categoria. O Lumina calcula a diferença no orçamento instantaneamente.')
    metas={}
    cols=st.columns(2)
    iniciais={'Energia':15,'Água':10,'Alimentação':8,'Transporte':5}
    for i,categoria in enumerate(CATEGORIAS):
        with cols[i%2]:
            metas[categoria]=st.slider(f'Reduzir {categoria} (%)',0,40,iniciais[categoria],1,key='sim_'+categoria)
    resultado=simular_economia(dict(zip(cats.categoria,cats.valor)),RENDA,metas)
    a,b,c=st.columns(3)
    a.metric('Economia estimada',brl(resultado['economia']))
    b.metric('Novo gasto mensal',brl(resultado['gasto_projetado']),delta=brl(-resultado['economia']))
    c.metric('Saldo após as metas',brl(resultado['saldo_projetado']),delta=brl(resultado['economia']))
    categorias=list(resultado['por_categoria'])
    comparacao=pd.DataFrame({'Categoria':categorias,
        'Hoje':[float(cats.set_index('categoria').loc[x,'valor']) for x in categorias],
        'Com metas':[resultado['por_categoria'][x] for x in categorias]})
    fig=px.bar(comparacao.melt(id_vars='Categoria',var_name='Cenário',value_name='R$'),
               x='Categoria',y='R$',color='Cenário',barmode='group',title='Seu orçamento: antes e depois')
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('### Sua missão de economia')
    if resultado['economia'] >= 200:
        st.success('🏆 Meta Ouro! Seu cenário economiza pelo menos R$ 200 por mês.')
    elif resultado['economia'] >= 100:
        st.info('🥈 Meta Prata! Você encontrou mais de R$ 100 em economia potencial.')
    elif resultado['economia'] > 0:
        st.info('🥉 Meta Bronze! Pequenas mudanças também fazem diferença.')
    else:
        st.info('Comece ajustando uma meta acima de zero.')
    st.caption('Simulação hipotética com despesas fictícias de outubro de 2026. Os percentuais são escolhas do visitante, não resultados previstos por IA. Nenhum dado é modificado.')

elif pagina=='Assistente Lumina':
    st.title('🤖 Assistente Lumina')
    st.caption('Pergunte sobre sua casa. Respostas automáticas com base nos dados disponíveis, sem conexão com Gemini.')
    perguntas=['Quanto gastamos neste mês?','Qual foi a maior despesa?','Quanto sobrou da renda?','Como economizar energia?','Como está o consumo de água?','Quais produtos precisam de reposição?','O que melhorar no próximo mês?','Quais luzes estão acesas?','Tem algum produto vencido?','Qual a previsão de energia?','Resuma o mês']
    def responder(q):
        import unicodedata
        def normalizar(texto):
            return ''.join(c for c in unicodedata.normalize('NFKD', texto.lower()) if not unicodedata.combining(c))
        s = normalizar(q)
        p = produtos()
        baixos = p[p.quantidade <= p.minimo]
        vencimentos = pd.to_datetime(p.validade, errors='coerce')
        vencidos = p[vencimentos.dt.date < date.today()]
        resumo = obter_resumo_consumo()
        metas = {'Energia': .15, 'Água': .10, 'Alimentação': .08, 'Transporte': .05}
        economia = sum(float(r.valor)*metas.get(r.categoria, 0) for r in cats.itertuples())
        if any(x in s for x in ['previsao de energia', 'prever energia', 'machine learning', 'knn']):
            serie = [(dia, float(kwh)) for dia, kwh in energia.groupby('data').kwh.sum().items()]
            ml = resumo_inteligente(serie)
            return f'KNN prevê {ml["previsao_kwh"]:.2f} kWh para {ml["data_previsao"]:%d/%m/%Y}. Erro médio nos 7 dias de teste: {ml["mae"]:.2f} kWh. Resultado educacional com dados simulados.'
        if any(x in s for x in ['resuma', 'resumo do mes', 'sumariz']):
            return f'Resumo de outubro: renda {brl(RENDA)}, despesas {brl(total)}, saldo {brl(saldo)}. Maior categoria: {cats.iloc[0].categoria}. Energia: {consumo:.1f} kWh; água: {agua_total:.1f} m³. Todos os dados são simulados.'
        if any(x in s for x in ['maior despesa', 'maior gasto', 'mais gast', 'mais caro']):
            return f'A maior categoria foi {cats.iloc[0].categoria}, com {brl(float(cats.iloc[0].valor))} no período analisado.'
        if any(x in s for x in ['sobrou', 'saldo', 'renda', 'salario', 'orcamento']):
            return f'A renda familiar simulada é {brl(RENDA)}; as despesas somaram {brl(total)} e o saldo é {brl(saldo)}. O orçamento comprometido é {total/RENDA:.1%}.'
        if any(x in s for x in ['vencid', 'validade', 'vencer']):
            if vencidos.empty: return 'Não há produtos vencidos cadastrados no momento.'
            return 'Produtos vencidos: ' + ', '.join(vencidos.produto.tolist()) + '. Confira a despensa antes de consumir.'
        if any(x in s for x in ['reposicao', 'acabando', 'estoque', 'despensa', 'produto', 'comprar']):
            return ('Produtos para repor: ' + ', '.join(f'{r.produto} ({r.quantidade:g} {r.unidade})' for r in baixos.itertuples()) + '.') if not baixos.empty else 'Nenhum produto está abaixo ou no estoque mínimo cadastrado.'
        if any(x in s for x in ['luz acesa', 'luzes acesas', 'comodo', 'lampada', 'smart home', 'casa ligada', 'potencia', 'cenario']):
            ligadas = [nome for nome, ligado in resumo['luzes'].items() if ligado]
            ambientes = ', '.join(ligadas) if ligadas else 'nenhuma luz ligada'
            return f'Estado virtual atual da Smart Home: {ambientes}. Potência instantânea simulada: {resumo["potencia_total_w"]} W (inclui aparelhos). Cenário: {st.session_state.lumina_cenario}.'
        if any(x in s for x in ['agua', 'vazamento']):
            return f'O histórico simulado de água totalizou {agua_total:.1f} m³ no mês. Sugiro verificar vazamentos e reduzir o tempo de torneiras abertas.'
        if any(x in s for x in ['energia', 'eletricidade', 'economizar luz']):
            return f'O histórico simulado registrou {consumo:.1f} kWh no mês. Meta sugerida: reduzir 15% dos gastos de energia, evitando aparelhos ligados sem necessidade.'
        if any(x in s for x in ['proximo', 'melhorar', 'economizar', 'novembro', 'previsao', 'economia']):
            return f'Para o próximo mês, sugerimos reduzir energia em 15%, água em 10%, alimentação em 8% e transporte em 5%. Economia hipotética: {brl(economia)}; gasto projetado: {brl(total-economia)}. Veja os cenários em Análise Inteligente.'
        if any(x in s for x in ['gast', 'despesa', 'mes', 'total']):
            return f'As despesas simuladas somaram {brl(total)} em outubro de 2026, para uma renda familiar de {brl(RENDA)}.'
        return 'Consigo consultar gastos, saldo, orçamento, energia, água, luzes da casa, estoque, validade e metas do próximo mês. Escolha uma pergunta sugerida ou use essas palavras na sua pergunta.'
    if 'conversa_lumina' not in st.session_state: st.session_state.conversa_lumina=[('assistant','Olá! Sou o Lumina. Como posso ajudar com sua casa hoje?')]
    cols=st.columns(2)
    for i,q in enumerate(perguntas):
        if cols[i%2].button(q,key=f'pergunta_{i}',use_container_width=True): st.session_state.conversa_lumina.extend([('user',q),('assistant',responder(q))])
    for role,msg in st.session_state.conversa_lumina:
        with st.chat_message(role): st.write(msg)
    q=st.chat_input('Pergunte sobre sua casa...')
    if q: st.session_state.conversa_lumina.extend([('user',q),('assistant',responder(q))]);st.rerun()
    st.caption('Respostas automáticas baseadas em dados simulados e no estado virtual da casa; não utiliza IA generativa.')

elif pagina=='Minha Smart Home':
    st.title('🏡 Minha Smart Home')
    st.caption('Controle virtual dos ambientes e cenários · Modelo 3D interativo')
    exibir_smart_home_3d()

elif pagina=='Despensa Inteligente':
    st.title('🥫 Despensa Inteligente')
    st.caption('Inventário da família com produtos já cadastrados e alertas automáticos')
    df=produtos();hoje=date.today()
    df['validade_dt']=pd.to_datetime(df.validade,errors='coerce')
    baixos=df[df.quantidade<=df.minimo]
    vencidos=df[df.validade_dt.dt.date<hoje]
    proximos=df[(df.validade_dt.dt.date>=hoje)&(df.validade_dt.dt.date<=hoje+timedelta(days=7))]
    a,b,c,d=st.columns(4)
    a.metric('Produtos',len(df));b.metric('Estoque baixo',len(baixos));c.metric('Vencidos',len(vencidos));d.metric('Valor estimado',brl(float((df.quantidade*df.preco).sum())))
    if not baixos.empty: st.warning('Reposição sugerida: '+', '.join(baixos.produto.tolist()))
    if not vencidos.empty: st.error('Validade ultrapassada: '+', '.join(vencidos.produto.tolist()))
    if not proximos.empty: st.info('Próximos do vencimento: '+', '.join(proximos.produto.tolist()))
    st.dataframe(df[['produto','categoria','quantidade','unidade','minimo','validade','preco']].rename(columns={'produto':'Produto','categoria':'Categoria','quantidade':'Quantidade','unidade':'Unidade','minimo':'Estoque mínimo','validade':'Validade','preco':'Preço unitário'}),use_container_width=True,hide_index=True)
    st.subheader('Atualizar estoque')
    op={f'{r.produto} · {r.quantidade:g} {r.unidade}':int(r.id) for r in df.itertuples()}
    escolhido=st.selectbox('Produto',list(op)); registro=df[df.id==op[escolhido]].iloc[0]
    nova=st.number_input('Quantidade disponível',min_value=0.0,value=float(registro.quantidade),step=1.0)
    if st.button('Salvar quantidade',type='primary'):
        with db() as con: con.execute('UPDATE produtos SET quantidade=? WHERE id=?',(validar_quantidade(nova),int(registro.id)))
        st.success('Estoque atualizado.');st.rerun()
    with st.expander('Adicionar um novo produto'):
        with st.form('novo_produto'):
            nome=st.text_input('Produto'); categoria=st.selectbox('Categoria',['Grãos e massas','Enlatados','Laticínios','Bebidas','Hortifruti','Limpeza','Outros'])
            qtd=st.number_input('Quantidade',min_value=0.0,value=1.0); unidade=st.selectbox('Unidade',['unidades','pacotes','kg','litros','latas'])
            minimo=st.number_input('Estoque mínimo',min_value=0.0,value=1.0);preco=st.number_input('Preço unitário (R$)',min_value=0.0,value=0.0)
            if st.form_submit_button('Cadastrar'):
                if nome.strip():
                    with db() as con: con.execute('INSERT INTO produtos(produto,categoria,quantidade,unidade,minimo,validade,preco) VALUES(?,?,?,?,?,?,?)',(nome.strip(),categoria,validar_quantidade(qtd),unidade,validar_quantidade(minimo),None,preco))
                    st.rerun()
                else: st.error('Informe o nome do produto.')
    st.caption('Os ajustes da despensa ficam no banco separado cliente_demo.db, sem alterar lumina.db.')

st.divider()
st.caption('Lumina AI · Ambiente de demonstração com dados financeiros e sensores simulados · Smart Home 2050')
