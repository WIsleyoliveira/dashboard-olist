import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title='Dashboard de Vendas - Olist', 
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ---------------------------------------------------------------------------
# CSS customizado para visual profissional
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fundo geral escuro */
    .stApp { background-color: #0e1117; }

    /* Cards de KPI */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetric"] label { font-size: 0.82rem; color: #8888aa; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.45rem; font-weight: 700; color: #e0e0ff;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #0a0a1a; }
    section[data-testid="stSidebar"] * { color: #b0b0cc !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #ffffff !important; }

    /* Tabs */
    button[data-baseweb="tab"] { font-weight: 600; color: #b0b0cc !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #ff4b4b !important; }

    /* Titulos e textos */
    h1, h2, h3 { color: #e0e0ff !important; }
    p, span, label, .stCaption { color: #a0a0c0 !important; }

    /* Expander */
    details { background-color: #1a1a2e; border-radius: 8px; }

    /* Dividers */
    hr { border-color: #2a2a4a !important; }

    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #4cc9f0;
        color: #4cc9f0 !important;
        border-radius: 8px;
        font-weight: 600;
    }
    .stDownloadButton button:hover {
        background: #4cc9f0;
        color: #0e1117 !important;
    }

    /* Insight boxes */
    .insight-box {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 100%);
        border-left: 3px solid #4cc9f0;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0 16px 0;
        font-size: 0.85rem;
        color: #a0a0c0;
        line-height: 1.5;
    }

    /* Rodape */
    .footer { text-align: center; color: #555577; font-size: 0.75rem; padding: 30px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Carregamento dos dados
# ---------------------------------------------------------------------------
@st.cache_data
def load():
    df = pd.read_csv('olist_limpo_categorizado_projeto.csv')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'], errors='coerce')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'], errors='coerce')
    df['mes_ano'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    if 'tempo_entrega' not in df.columns:
        df['tempo_entrega'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    if 'tempo_atraso' not in df.columns:
        df['tempo_atraso'] = df['order_delivered_customer_date'] > df['order_estimated_delivery_date']
    return df


df = load()

# ---------------------------------------------------------------------------
# Funcao auxiliar para insights estilizados
# ---------------------------------------------------------------------------
def insight(texto, icone='💡'):
    """Exibe um box de insight estilizado abaixo dos graficos."""
    st.markdown(f'<div class="insight-box">{icone} {texto}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar - Filtros
# ---------------------------------------------------------------------------
st.sidebar.title('Painel de Controle')
st.sidebar.markdown('---')

todas_categorias = sorted(df['product_category_name'].dropna().unique())
categorias_sel = st.sidebar.multiselect(
    'Categorias de produto',
    options=todas_categorias,
    default=todas_categorias[:10],
)

status_sel = st.sidebar.multiselect(
    'Status do pedido',
    options=sorted(df['order_status'].unique()),
    default=df['order_status'].unique().tolist(),
)

meses = sorted(df['mes_ano'].unique())
mes_inicio, mes_fim = st.sidebar.select_slider(
    'Periodo',
    options=meses,
    value=(meses[0], meses[-1]),
)

st.sidebar.markdown('---')
st.sidebar.caption('Dashboard Olist - Analise de Vendas')

# ---------------------------------------------------------------------------
# Filtragem
# ---------------------------------------------------------------------------
df_f = df[
    df['product_category_name'].isin(categorias_sel)
    & df['order_status'].isin(status_sel)
    & (df['mes_ano'] >= mes_inicio)
    & (df['mes_ano'] <= mes_fim)
]
df_entregues = df_f[df_f['order_status'] == 'delivered']

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title('📊 Dashboard de Vendas - Olist')
st.caption(f'Periodo selecionado: **{mes_inicio}** ate **{mes_fim}**  ·  '
           f'{len(categorias_sel)} categorias  ·  '
           f'{len(df_f):,} registros filtrados')

# ---------------------------------------------------------------------------
# KPIs com deltas
# ---------------------------------------------------------------------------
def formatar_valor(valor):
    """Abrevia valores grandes: 1.2M, 350K, etc."""
    if valor >= 1_000_000:
        return f'R$ {valor / 1_000_000:.1f}M'
    elif valor >= 1_000:
        return f'R$ {valor / 1_000:.1f}K'
    return f'R$ {valor:,.0f}'

total_faturamento = df_f['price'].sum()
total_frete = df_f['freight_value'].sum()
total_pedidos = df_f['order_id'].nunique()
ticket_medio = df_f.groupby('order_id')['price'].sum().mean() if total_pedidos > 0 else 0
tempo_medio = df_entregues['tempo_entrega'].mean() if len(df_entregues) > 0 else float('nan')
pct_atraso = df_entregues['tempo_atraso'].mean() * 100 if len(df_entregues) > 0 else 0
pedidos_entregues = df_entregues['order_id'].nunique()
taxa_entrega = (pedidos_entregues / total_pedidos * 100) if total_pedidos > 0 else 0

# Calcular frete como % do faturamento
pct_frete = (total_frete / total_faturamento * 100) if total_faturamento > 0 else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric('💰 Faturamento', formatar_valor(total_faturamento))
k2.metric('🚚 Frete Total', formatar_valor(total_frete), delta=f'{pct_frete:.1f}% do faturamento', delta_color='off')
k3.metric('📦 Pedidos', f'{total_pedidos:,}')
k4.metric('🎯 Ticket Medio', f'R$ {ticket_medio:,.2f}')
k5.metric('⏱️ Entrega Media', f'{tempo_medio:.1f} dias' if not np.isnan(tempo_medio) else 'N/A')
k6.metric('✅ Taxa de Entrega', f'{taxa_entrega:.1f}%', delta=f'{pct_atraso:.1f}% atrasados', delta_color='inverse')

st.markdown('')

# ---------------------------------------------------------------------------
# Abas
# ---------------------------------------------------------------------------
tab_vendas, tab_entregas, tab_frete, tab_detalhes, tab_dados = st.tabs([
    '📈 Vendas', '🚚 Entregas', '💲 Frete', '🔍 Detalhamento', '📋 Dados',
])

# Paleta de cores padrao
COR_PRIMARIA = '#e0e0ff'
COR_ACCENT = '#4cc9f0'
COR_SUCCESS = '#06d6a0'
COR_DANGER = '#ef476f'
COR_WARN = '#ffd166'
PALETTE_SEQ = px.colors.sequential.Blues_r

# Layout padrao escuro para todos os graficos Plotly
DARK_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#b0b0cc',
    title_font_color='#e0e0ff',
    xaxis=dict(gridcolor='#2a2a4a'),
    yaxis=dict(gridcolor='#2a2a4a'),
)

# ===========================================================================
# ABA 1 - VENDAS
# ===========================================================================
with tab_vendas:
    c1, c2 = st.columns(2)

    # --- Faturamento mensal (area) ---
    with c1:
        fat_mes = df_f.groupby('mes_ano')['price'].sum().reset_index()
        fat_mes.columns = ['Mes', 'Receita']
        fig = px.area(fat_mes, x='Mes', y='Receita',
                      title='Faturamento Mensal',
                      color_discrete_sequence=[COR_ACCENT])
        fig.update_layout(**DARK_LAYOUT, xaxis_title='', yaxis_title='Receita (R$)',
                          hovermode='x unified',
                          yaxis_tickprefix='R$ ', yaxis_tickformat=',.0f',
                          template='plotly_dark', height=400)
        st.plotly_chart(fig, width='stretch')
        insight('Crescimento continuo em 2017 com pico na Black Friday (nov/2017, mais de 7 mil pedidos). '
                'Apos o pico, o patamar se manteve alto ao longo de 2018, indicando consolidacao. '
                'Os dados vao de set/2016 a ago/2018 (set/2018 tem apenas 1 registro, mes incompleto).', '📈')

    # --- Top 10 categorias ---
    with c2:
        top_cat = (df_f.groupby('product_category_name')['price']
                   .sum().sort_values(ascending=True).tail(10).reset_index())
        top_cat.columns = ['Categoria', 'Receita']
        fig2 = px.bar(top_cat, x='Receita', y='Categoria', orientation='h',
                      title='Top 10 Categorias por Faturamento',
                      color='Receita', color_continuous_scale='Blues')
        fig2.update_layout(**DARK_LAYOUT, yaxis_title='', xaxis_title='Receita (R$)',
                           xaxis_tickprefix='R$ ', xaxis_tickformat=',.0f',
                           coloraxis_showscale=False,
                           template='plotly_dark', height=400)
        st.plotly_chart(fig2, width='stretch')
        insight('Beleza e Saude lidera isolada. O perfil de compra revela preferencia '
                'por cuidado pessoal, conforto para o lar e presentes.', '🏆')

    c3, c4 = st.columns(2)

    # --- Volume de pedidos ---
    with c3:
        ped_mes = df_f.groupby('mes_ano')['order_id'].nunique().reset_index()
        ped_mes.columns = ['Mes', 'Pedidos']
        fig3 = px.bar(ped_mes, x='Mes', y='Pedidos',
                      title='Volume de Pedidos por Mes',
                      color_discrete_sequence=[COR_WARN])
        fig3.update_layout(**DARK_LAYOUT, xaxis_title='', yaxis_title='Pedidos',
                           template='plotly_dark', height=380)
        st.plotly_chart(fig3, width='stretch')
        insight('A curva de pedidos acompanha o faturamento — o crescimento da receita '
                'foi tracionado por ganho de escala (mais clientes), nao por aumento de precos. '
                'Pico em nov/2017 com 7.259 pedidos unicos.', '📦')

    # --- Status dos pedidos (donut) ---
    with c4:
        status_df = df_f['order_status'].value_counts().reset_index()
        status_df.columns = ['Status', 'Qtd']
        fig4 = px.pie(status_df, names='Status', values='Qtd',
                      title='Status dos Pedidos', hole=0.45,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_traces(textinfo='percent+label')
        fig4.update_layout(**DARK_LAYOUT, template='plotly_dark', height=380,
                           showlegend=False)
        st.plotly_chart(fig4, width='stretch')
        insight('Concentracao esmagadora em "delivered" — a base reflete vendas finalizadas '
                'com taxa de sucesso altissima e indice de cancelamento quase insignificante.', '✅')

    # --- Receita por categoria ao longo do tempo (heatmap) ---
    top5 = df_f.groupby('product_category_name')['price'].sum().nlargest(5).index
    heat = (df_f[df_f['product_category_name'].isin(top5)]
            .groupby(['mes_ano', 'product_category_name'])['price']
            .sum().reset_index())
    heat.columns = ['Mes', 'Categoria', 'Receita']
    heat_pivot = heat.pivot(index='Categoria', columns='Mes', values='Receita').fillna(0)
    fig_heat = px.imshow(heat_pivot, text_auto='.0f', aspect='auto',
                         color_continuous_scale='Blues',
                         title='Heatmap - Receita Mensal das Top 5 Categorias')
    fig_heat.update_layout(**DARK_LAYOUT, template='plotly_dark', height=350)
    st.plotly_chart(fig_heat, width='stretch')


# ===========================================================================
# ABA 2 - ENTREGAS
# ===========================================================================
with tab_entregas:
    e1, e2 = st.columns(2)

    # --- Histograma tempo de entrega ---
    with e1:
        fig5 = px.histogram(df_entregues, x='tempo_entrega', nbins=40,
                            title='Distribuicao do Tempo de Entrega (dias)',
                            color_discrete_sequence=[COR_SUCCESS])
        fig5.update_layout(**DARK_LAYOUT, xaxis_title='Dias', yaxis_title='Frequencia',
                           template='plotly_dark', height=400, bargap=0.05)
        st.plotly_chart(fig5, width='stretch')
        insight('A maioria das entregas ocorre entre 0 e 20 dias. Porem, a cauda longa '
                'revela casos extremos (50 a 200 dias) que precisam ser investigados.', '⏱️')

    # --- Gauge de pontualidade + % atraso ---
    with e2:
        pontualidade = 100 - pct_atraso
        fig_gauge = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=pontualidade,
            number={'suffix': '%', 'font': {'size': 48, 'color': '#e0e0ff'}},
            delta={'reference': 90, 'increasing': {'color': COR_SUCCESS}, 'decreasing': {'color': COR_DANGER}},
            title={'text': 'Taxa de Pontualidade', 'font': {'size': 18, 'color': '#e0e0ff'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#b0b0cc'},
                'bar': {'color': COR_SUCCESS if pontualidade >= 90 else COR_WARN},
                'bgcolor': '#1a1a2e',
                'bordercolor': '#2a2a4a',
                'steps': [
                    {'range': [0, 70], 'color': 'rgba(239,71,111,0.15)'},
                    {'range': [70, 90], 'color': 'rgba(255,209,102,0.15)'},
                    {'range': [90, 100], 'color': 'rgba(6,214,160,0.15)'},
                ],
                'threshold': {'line': {'color': '#ff4b4b', 'width': 3}, 'thickness': 0.8, 'value': 90},
            }
        ))
        fig_gauge.update_layout(**DARK_LAYOUT, template='plotly_dark', height=400)
        st.plotly_chart(fig_gauge, width='stretch')
        insight(f'Pontualidade atual: {pontualidade:.1f}%. A meta de 90% esta marcada como referencia. '
                f'Apenas {pct_atraso:.1f}% dos pedidos entregues sofrem atraso.', '🎯')

    # --- % atraso por mes ---
    atraso_mes = (df_entregues.groupby('mes_ano')['tempo_atraso']
                  .mean().mul(100).reset_index())
    atraso_mes.columns = ['Mes', 'Pct_Atraso']
    fig6 = px.line(atraso_mes, x='Mes', y='Pct_Atraso',
                   title='Percentual de Atrasos por Mes', markers=True,
                   color_discrete_sequence=[COR_DANGER])
    fig6.update_layout(**DARK_LAYOUT, xaxis_title='', yaxis_title='% Atrasados',
                       yaxis_ticksuffix='%',
                       template='plotly_dark', height=380)
    st.plotly_chart(fig6, width='stretch')

    # --- Boxplot tempo por top 10 categorias ---
    top10_cat = df_f['product_category_name'].value_counts().head(10).index
    df_box = df_entregues[df_entregues['product_category_name'].isin(top10_cat)]
    fig7 = px.box(df_box, x='product_category_name', y='tempo_entrega',
                  title='Tempo de Entrega por Categoria (Top 10)',
                  color='product_category_name',
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig7.update_layout(**DARK_LAYOUT, xaxis_title='', yaxis_title='Dias',
                       showlegend=False, template='plotly_dark', height=420)
    fig7.update_xaxes(tickangle=-45)
    st.plotly_chart(fig7, width='stretch')
    insight('O tempo padrao de entrega e uniforme entre categorias (~10-12 dias). '
            'Os outliers severos aparecem em todas, mas moveis e itens volumosos '
            'registram os piores extremos, ultrapassando 200 dias.', '📦')


# ===========================================================================
# ABA 3 - FRETE
# ===========================================================================
with tab_frete:
    f1, f2 = st.columns(2)

    # --- Scatter preco x frete ---
    with f1:
        sample_size = min(4000, len(df_f))
        df_sample = df_f.sample(sample_size, random_state=42) if sample_size > 0 else df_f
        fig8 = px.scatter(df_sample, x='price', y='freight_value',
                          opacity=0.35, title='Preco x Frete',
                          color_discrete_sequence=[COR_ACCENT])
        fig8.update_layout(**DARK_LAYOUT, xaxis_title='Preco (R$)', yaxis_title='Frete (R$)',
                           template='plotly_dark', height=400)
        st.plotly_chart(fig8, width='stretch')
        insight('Nao ha correlacao clara entre preco e frete. O custo logistico depende '
                'de peso, volume e distancia geografica, nao do valor comercial do produto.', '🔍')

    # --- Top 10 frete medio ---
    with f2:
        frete_cat = (df_f.groupby('product_category_name')['freight_value']
                     .mean().sort_values(ascending=True).tail(10).reset_index())
        frete_cat.columns = ['Categoria', 'Frete_Medio']
        fig9 = px.bar(frete_cat, x='Frete_Medio', y='Categoria', orientation='h',
                      title='Top 10 Categorias - Frete Medio',
                      color='Frete_Medio', color_continuous_scale='Oranges')
        fig9.update_layout(**DARK_LAYOUT, yaxis_title='', xaxis_title='Frete Medio (R$)',
                           xaxis_tickprefix='R$ ', coloraxis_showscale=False,
                           template='plotly_dark', height=400)
        st.plotly_chart(fig9, width='stretch')
        insight('PCs, colchoes, estofados e moveis lideram — itens grandes e pesados '
                'encarecem a logistica, com frete medio de R$ 35 a R$ 42.', '💲')

    # --- Boxplot frete: pontual vs atrasado ---
    df_atraso = df_entregues.copy()
    df_atraso['Entrega'] = df_atraso['tempo_atraso'].map({True: 'Atrasado', False: 'Pontual'})
    fig10 = px.box(df_atraso, x='Entrega', y='freight_value',
                   color='Entrega',
                   color_discrete_map={'Pontual': COR_SUCCESS, 'Atrasado': COR_DANGER},
                   title='Frete - Pontual vs Atrasado')
    fig10.update_layout(**DARK_LAYOUT, xaxis_title='', yaxis_title='Frete (R$)',
                        showlegend=False, template='plotly_dark', height=380)
    st.plotly_chart(fig10, width='stretch')
    insight('Pagar frete mais caro nao garante entrega sem atraso. Fretes altos '
            'indicam produtos volumosos ou destinos distantes, que naturalmente '
            'tem logistica mais complexa.', '⚠️')


# ===========================================================================
# ABA 4 - DETALHAMENTO
# ===========================================================================
with tab_detalhes:
    d1, d2 = st.columns(2)

    # --- Ticket medio ---
    with d1:
        ticket_df = df_f.groupby('order_id')['price'].sum().reset_index()
        ticket_df.columns = ['order_id', 'Ticket']
        fig11 = px.histogram(ticket_df, x='Ticket', nbins=40,
                             title='Distribuicao do Ticket por Pedido',
                             color_discrete_sequence=['goldenrod'])
        fig11.update_layout(**DARK_LAYOUT, xaxis_title='Valor (R$)', yaxis_title='Frequencia',
                            template='plotly_dark', height=400, bargap=0.05)
        st.plotly_chart(fig11, width='stretch')
        insight('Maioria das vendas concentrada ate R$ 200 — operacao de alto giro '
                'com produtos acessiveis. Politicas de desconto e frete gratis '
                'devem considerar margens apertadas nessa faixa.', '🎯')

    # --- Itens por pedido ---
    with d2:
        itens_df = df_f.groupby('order_id')['order_item_id'].count().reset_index()
        itens_df.columns = ['order_id', 'Itens']
        fig12 = px.histogram(itens_df, x='Itens', nbins=20,
                             title='Quantidade de Itens por Pedido',
                             color_discrete_sequence=[COR_SUCCESS])
        fig12.update_layout(**DARK_LAYOUT, xaxis_title='Itens', yaxis_title='Frequencia',
                            template='plotly_dark', height=400, bargap=0.05)
        st.plotly_chart(fig12, width='stretch')
        insight('A maioria compra apenas 1 item por pedido. Grande oportunidade '
                'para cross-sell: sugerir produtos complementares no checkout '
                'ou desconto no frete ao adicionar segundo item.', '🛒')

    # --- Preco medio por status ---
    preco_status = df_f.groupby('order_status')['price'].mean().sort_values().reset_index()
    preco_status.columns = ['Status', 'Preco_Medio']
    fig13 = px.bar(preco_status, x='Status', y='Preco_Medio',
                   title='Preco Medio por Status do Pedido',
                   color='Preco_Medio', color_continuous_scale='RdBu_r')
    fig13.update_layout(**DARK_LAYOUT, xaxis_title='', yaxis_title='Preco Medio (R$)',
                        yaxis_tickprefix='R$ ', coloraxis_showscale=False,
                        template='plotly_dark', height=380)
    st.plotly_chart(fig13, width='stretch')
    insight('Pedidos entregues tem ticket medio mais baixo. Itens mais caros sofrem '
            'mais friccao: mais cancelamentos, mais tempo em processamento e mais '
            'rupturas de estoque.', '⚡')

    # --- Peso medio x Frete medio por categoria ---
    if 'product_weight_g' in df_f.columns:
        peso_frete = (df_f.groupby('product_category_name')
                      .agg(peso_medio=('product_weight_g', 'mean'),
                           frete_medio=('freight_value', 'mean'),
                           qtd=('order_id', 'count'))
                      .reset_index()
                      .sort_values('qtd', ascending=False)
                      .head(15))
        fig14 = px.scatter(peso_frete, x='peso_medio', y='frete_medio',
                           size='qtd', hover_name='product_category_name',
                           title='Peso Medio x Frete Medio (Top 15 categorias por volume)',
                           color='frete_medio', color_continuous_scale='Viridis')
        fig14.update_layout(**DARK_LAYOUT, xaxis_title='Peso Medio (g)', yaxis_title='Frete Medio (R$)',
                            coloraxis_showscale=False,
                            template='plotly_dark', height=420)
        st.plotly_chart(fig14, width='stretch')
        insight('Quanto maior o peso, maior o frete — confirma que o custo logistico '
                'e definido por fatores fisicos. O tamanho das bolhas mostra o volume '
                'de vendas de cada categoria.', '⚖️')


# ===========================================================================
# ABA 5 - DADOS
# ===========================================================================
with tab_dados:
    st.subheader('📋 Dados Filtrados')
    colunas_exibir = [
        'order_id', 'order_status', 'product_category_name',
        'price', 'freight_value', 'mes_ano', 'tempo_entrega', 'tempo_atraso',
    ]
    st.dataframe(
        df_f[colunas_exibir].head(500),
        width='stretch',
        height=500,
    )

    # Botao de download
    csv_export = df_f[colunas_exibir].to_csv(index=False).encode('utf-8')
    st.download_button(
        label='⬇️ Baixar dados filtrados (.csv)',
        data=csv_export,
        file_name='olist_dados_filtrados.csv',
        mime='text/csv',
    )

    st.markdown('---')
    st.subheader('📊 Resumo Estatistico')
    st.dataframe(
        df_f[['price', 'freight_value', 'tempo_entrega', 'product_weight_g']].describe().T,
        width='stretch',
    )

    st.markdown('---')
    st.subheader('🎯 Conclusoes e Recomendacoes')

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("""
        **Pontos Fortes da Operacao:**
        - ✅ Taxa de pontualidade acima de 90%
        - ✅ Crescimento sustentavel pos-Black Friday
        - ✅ Base consolidada com taxa de cancelamento minima
        - ✅ Tempo medio de entrega competitivo (~12 dias)
        """)
    with col_c2:
        st.markdown("""
        **Oportunidades de Melhoria:**
        - 🔄 Implementar cross-sell (maioria compra 1 item)
        - 📦 Investigar entregas extremas (>50 dias)
        - 💰 Reduzir friccao em pedidos de alto valor
        - 🚚 Otimizar logistica de itens volumosos
        """)


# ---------------------------------------------------------------------------
# Rodape
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="footer">'
    '📊 Dashboard Olist - Analise de Vendas | Dados: Olist Public Dataset (Kaggle) | '
    'Desenvolvido por <b>Wisley Oliveira</b>'
    '</div>',
    unsafe_allow_html=True,
)
