
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DB_NAME = Path(__file__).with_name("lumina.db")

CATEGORIAS = [
    "Grãos e massas",
    "Enlatados",
    "Laticínios",
    "Bebidas",
    "Hortifruti",
    "Limpeza",
    "Outros"
]


def _conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabela_despensa():
    with _conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS despensa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT NOT NULL,
                categoria TEXT NOT NULL,
                quantidade REAL NOT NULL DEFAULT 0,
                unidade TEXT NOT NULL DEFAULT 'unidades',
                estoque_minimo REAL NOT NULL DEFAULT 1,
                validade TEXT,
                valor_unitario REAL NOT NULL DEFAULT 0,
                atualizado_em TEXT NOT NULL
            )
        """)


def listar_produtos():
    criar_tabela_despensa()

    with _conectar() as conexao:
        return pd.read_sql_query(
            "SELECT * FROM despensa ORDER BY categoria, produto",
            conexao
        )


def salvar_produto(
    produto, categoria, quantidade, unidade,
    minimo, validade, valor
):
    criar_tabela_despensa()

    with _conectar() as conexao:
        conexao.execute("""
            INSERT INTO despensa (
                produto, categoria, quantidade, unidade,
                estoque_minimo, validade, valor_unitario,
                atualizado_em
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            produto.strip(),
            categoria,
            quantidade,
            unidade,
            minimo,
            validade.isoformat() if validade else None,
            valor,
            datetime.now().isoformat(timespec="seconds")
        ))


def atualizar_quantidade(produto_id, quantidade):
    with _conectar() as conexao:
        conexao.execute("""
            UPDATE despensa
            SET quantidade = ?, atualizado_em = ?
            WHERE id = ?
        """, (
            quantidade,
            datetime.now().isoformat(timespec="seconds"),
            produto_id
        ))


def excluir_produto(produto_id):
    with _conectar() as conexao:
        conexao.execute(
            "DELETE FROM despensa WHERE id = ?",
            (produto_id,)
        )


def _grafico_prateleiras(df):
    fig = go.Figure()

    # Estrutura ilustrativa das três prateleiras.
    for y in [3, 2, 1]:
        fig.add_trace(go.Scatter3d(
            x=[0, 6, 6, 0, 0],
            y=[y, y, y, y, y],
            z=[0, 0, 0.22, 0.22, 0],
            mode="lines",
            line=dict(color="#38bdf8", width=8),
            showlegend=False,
            hoverinfo="skip"
        ))

    cores = {
        "Grãos e massas": "#fbbf24",
        "Enlatados": "#fb923c",
        "Laticínios": "#e0f2fe",
        "Bebidas": "#22d3ee",
        "Hortifruti": "#4ade80",
        "Limpeza": "#a78bfa",
        "Outros": "#cbd5e1"
    }

    for i, row in df.reset_index(drop=True).iterrows():
        nivel = i % 3
        pos = (i // 3) % 6

        fig.add_trace(go.Scatter3d(
            x=[0.55 + pos * 0.9],
            y=[3 - nivel],
            z=[0.55 + (i % 2) * 0.08],
            mode="markers+text",
            text=[str(row["produto"])],
            textposition="top center",
            marker=dict(
                size=13,
                color=cores.get(row["categoria"], "#67e8f9"),
                line=dict(color="#e0f2fe", width=1)
            ),
            name=str(row["produto"]),
            showlegend=False,
            hovertemplate=(
                f"{row['produto']}<br>"
                f"Estoque: {row['quantidade']:g} "
                f"{row['unidade']}<extra></extra>"
            )
        ))

    fig.update_layout(
        height=390,
        margin=dict(l=0, r=0, t=5, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[0, 6]),
            yaxis=dict(visible=False, range=[0.5, 3.5]),
            zaxis=dict(visible=False, range=[0, 1.3]),
            aspectmode="manual",
            aspectratio=dict(x=1.7, y=0.9, z=0.55),
            camera=dict(eye=dict(x=1.6, y=-2.0, z=1.4))
        )
    )

    return fig


def exibir_despensa():
    criar_tabela_despensa()
    df = listar_produtos()

    # Cabeçalho visual
    st.html("""
    <div style="
        background:
            radial-gradient(
                circle at 85% 15%,
                rgba(34,211,238,.2),
                transparent 30%
            ),
            linear-gradient(120deg,#07152b,#0b3552);
        border:1px solid #176080;
        border-radius:18px;
        padding:22px;
        margin-bottom:18px;
    ">
        <div style="
            color:#67e8f9;
            font-size:11px;
            font-weight:800;
            letter-spacing:2px;
        ">
            SMART HOME 2050 · GESTÃO DOMÉSTICA
        </div>

        <h2 style="color:#f1f8ff;margin:6px 0;">
            🥫 Despensa Inteligente
        </h2>

        <p style="color:#c5d9ed;margin:0;">
            Controle seus produtos, acompanhe a validade
            e saiba quando é hora de repor.
        </p>
    </div>
    """)

    # Preparação dos dados
    hoje = date.today()

    if not df.empty:
        df["quantidade"] = pd.to_numeric(
            df["quantidade"], errors="coerce"
        ).fillna(0)

        df["estoque_minimo"] = pd.to_numeric(
            df["estoque_minimo"], errors="coerce"
        ).fillna(0)

        df["valor_unitario"] = pd.to_numeric(
            df["valor_unitario"], errors="coerce"
        ).fillna(0)

        validade = pd.to_datetime(
            df["validade"], errors="coerce"
        )

        baixo = df[
            df["quantidade"] <= df["estoque_minimo"]
        ]

        hoje_timestamp = pd.Timestamp(hoje)
        limite_validade = pd.Timestamp(
            hoje + timedelta(days=7)
        )

        # Produtos que vencem hoje ou nos próximos 7 dias.
        vencendo = df[
            validade.notna()
            & (validade >= hoje_timestamp)
            & (validade <= limite_validade)
        ]

        # Produtos cuja validade já passou.
        vencidos = df[
            validade.notna()
            & (validade < hoje_timestamp)
        ]

        valor_total = float(
            (df["quantidade"] * df["valor_unitario"]).sum()
        )

    else:
        baixo = df.copy()
        vencendo = df.copy()
        vencidos = df.copy()
        valor_total = 0.0

    # Indicadores
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("📦 Produtos cadastrados", len(df))
    m2.metric("⚠️ Estoque baixo", len(baixo))
    m3.metric("⏳ Validade próxima", len(vencendo))

    valor_formatado = (
        f"R$ {valor_total:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    m4.metric("💰 Valor estimado", valor_formatado)

    # Prateleiras e alertas
    visual, resumo = st.columns([1.35, 1], gap="large")

    with visual:
        st.markdown("#### 🧊 Prateleiras da despensa")

        if df.empty:
            st.info(
                "Cadastre produtos para preencher "
                "as prateleiras virtuais."
            )
        else:
            st.plotly_chart(
                _grafico_prateleiras(df),
                use_container_width=True,
                config={"displayModeBar": False}
            )

        st.caption(
            "Representação 3D ilustrativa. "
            "Não há câmera ou sensor físico conectado nesta versão."
        )

    with resumo:
        st.markdown("#### 🔔 Central de alertas")

        if baixo.empty:
            st.success(
                "Nenhum produto abaixo do estoque mínimo."
            )
        else:
            for _, p in baixo.iterrows():
                st.warning(
                    f"{p['produto']}: {p['quantidade']:g} "
                    f"{p['unidade']} — reposição sugerida."
                )

        if not vencidos.empty:
            for _, p in vencidos.iterrows():
                st.error(
                    f"{p['produto']}: produto vencido "
                    f"em {p['validade']}."
                )

        if vencendo.empty:
            st.success(
                "Nenhum produto com validade próxima."
            )
        else:
            for _, p in vencendo.iterrows():
                st.info(
                    f"{p['produto']}: validade {p['validade']}."
                )

    st.divider()

    cadastro, inventario = st.columns(
        [1, 1.25],
        gap="large"
    )

    # Cadastro
    with cadastro:
        st.markdown("#### ➕ Cadastrar produto")

        with st.form(
            "form_novo_produto_despensa",
            clear_on_submit=True
        ):
            produto = st.text_input(
                "Nome do produto",
                placeholder="Ex.: Arroz"
            )

            categoria = st.selectbox(
                "Categoria",
                CATEGORIAS
            )

            quantidade = st.number_input(
                "Quantidade atual",
                min_value=0.0,
                value=1.0,
                step=1.0
            )

            unidade = st.selectbox(
                "Unidade",
                [
                    "unidades",
                    "pacotes",
                    "kg",
                    "g",
                    "litros",
                    "ml",
                    "latas"
                ]
            )

            minimo = st.number_input(
                "Avisar quando chegar a",
                min_value=0.0,
                value=1.0,
                step=1.0
            )

            validade = st.date_input(
                "Validade (opcional)",
                value=None
            )

            valor = st.number_input(
                "Valor unitário estimado (R$)",
                min_value=0.0,
                value=0.0,
                step=1.0
            )

            enviar = st.form_submit_button(
                "Adicionar à despensa",
                use_container_width=True
            )

        if enviar:
            if produto.strip():
                salvar_produto(
                    produto,
                    categoria,
                    quantidade,
                    unidade,
                    minimo,
                    validade,
                    valor
                )

                st.success("Produto adicionado à despensa!")
                st.rerun()
            else:
                st.error("Informe o nome do produto.")

    # Inventário
    with inventario:
        st.markdown("#### 📋 Inventário")

        if df.empty:
            st.caption(
                "Seus produtos cadastrados aparecerão aqui."
            )

        else:
            exibicao = df[
                [
                    "produto",
                    "categoria",
                    "quantidade",
                    "unidade",
                    "estoque_minimo",
                    "validade",
                    "valor_unitario"
                ]
            ].copy()

            exibicao.columns = [
                "Produto",
                "Categoria",
                "Qtd.",
                "Unidade",
                "Mínimo",
                "Validade",
                "Valor unit. (R$)"
            ]

            st.dataframe(
                exibicao,
                use_container_width=True,
                hide_index=True
            )

            opcoes = {
                f"{int(r.id)} — {r.produto}": int(r.id)
                for r in df.itertuples()
            }

            escolhido = st.selectbox(
                "Atualizar ou remover produto",
                list(opcoes),
                key="produto_despensa_selecionado"
            )

            produto_id = opcoes[escolhido]

            linha = df[
                df["id"] == produto_id
            ].iloc[0]

            nova_qtd = st.number_input(
                "Nova quantidade",
                min_value=0.0,
                value=float(linha["quantidade"]),
                step=1.0,
                key=f"qtd_produto_{produto_id}"
            )

            a, b = st.columns(2)

            if a.button(
                "Salvar quantidade",
                use_container_width=True
            ):
                atualizar_quantidade(
                    produto_id,
                    nova_qtd
                )

                st.success("Estoque atualizado.")
                st.rerun()

            if b.button(
                "Excluir produto",
                use_container_width=True
            ):
                st.session_state[
                    "confirmar_exclusao_produto"
                ] = produto_id

            if (
                st.session_state.get(
                    "confirmar_exclusao_produto"
                ) == produto_id
            ):
                st.warning(
                    "Confirme a exclusão deste produto."
                )

                c1, c2 = st.columns(2)

                if c1.button(
                    "Confirmar exclusão",
                    key=f"confirmar_produto_{produto_id}"
                ):
                    excluir_produto(produto_id)

                    st.session_state.pop(
                        "confirmar_exclusao_produto",
                        None
                    )

                    st.rerun()

                if c2.button(
                    "Cancelar",
                    key=f"cancelar_produto_{produto_id}"
                ):
                    st.session_state.pop(
                        "confirmar_exclusao_produto",
                        None
                    )

                    st.rerun()

    st.caption(
        "Os produtos são salvos na tabela própria 'despensa' "
        "do mesmo arquivo lumina.db. "
        "Os registros de despesas existentes não são alterados."
    )
