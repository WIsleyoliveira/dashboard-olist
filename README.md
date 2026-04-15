# Dashboard de Vendas - Olist E-Commerce

Analise completa de mais de 100 mil registros de vendas do marketplace Olist, desde o tratamento e limpeza dos dados ate a construcao de um dashboard interativo em producao.

**Acesse o dashboard:** [dashboard-olist-wisley.streamlit.app](https://dashboard-olist-wisley.streamlit.app)

---

## Contexto do Projeto

O Olist e a maior plataforma de e-commerce para pequenos lojistas do Brasil. Este projeto analisa dados publicos de vendas entre 2016 e 2018, cobrindo todo o ciclo do pedido: compra, pagamento, logistica e entrega ao cliente.

O trabalho foi dividido em duas etapas:
1. **Analise exploratoria** (`Projeto.ipynb`) — Limpeza, tratamento e visualizacao dos dados com Pandas, Seaborn e Matplotlib
2. **Dashboard interativo** (`dashboard.py`) — Painel de controle com filtros dinamicos, KPIs e graficos interativos usando Streamlit e Plotly

## Principais Descobertas

### Vendas
- O faturamento cresceu continuamente ao longo de 2017, com pico expressivo na **Black Friday de novembro** (mais de 8 mil pedidos)
- Apos a Black Friday, o patamar de vendas se manteve alto em 2018, indicando **crescimento real da operacao** e nao apenas sazonalidade
- A categoria **Beleza e Saude** lidera isolada com mais de R$ 1 milhao em receita, seguida por Cama/Mesa/Banho e Relogios/Presentes

### Logistica
- Tempo medio de entrega: **~12 dias**
- Taxa de pontualidade: **92% dos pedidos** chegam no prazo
- O valor do frete **nao depende do preco do produto** — depende de peso, volume e distancia geografica
- Categorias com maior frete medio: PCs, colchoes, estofados e moveis (itens grandes e pesados)

### Comportamento de Compra
- A maioria dos clientes compra **apenas 1 item por pedido** — grande oportunidade para cross-sell
- Ticket medio concentrado ate R$ 200, caracterizando uma operacao de **alto giro com produtos acessiveis**
- Pedidos com itens mais caros sofrem mais cancelamentos e ficam mais tempo em processamento

## O que tem no Dashboard

### KPIs
Faturamento total, frete total, numero de pedidos, ticket medio, tempo medio de entrega e taxa de entrega — todos respondem aos filtros em tempo real.

### Aba Vendas
- Grafico de area: evolucao do faturamento mensal
- Barras horizontais: top 10 categorias por receita
- Barras: volume de pedidos por mes
- Donut: distribuicao de status dos pedidos
- Heatmap: receita mensal das top 5 categorias ao longo do tempo

### Aba Entregas
- Histograma: distribuicao do tempo de entrega (mostra a cauda longa de atrasos extremos)
- Linha: percentual de atrasos por mes
- Boxplot: tempo de entrega por categoria (top 10)

### Aba Frete
- Scatter: relacao preco x frete (sem correlacao clara)
- Barras: top 10 categorias com maior frete medio
- Boxplot: comparacao de frete entre entregas pontuais e atrasadas

### Aba Detalhamento
- Histograma: distribuicao do ticket por pedido
- Histograma: quantidade de itens por pedido
- Barras: preco medio por status do pedido
- Scatter bolha: peso medio x frete medio por categoria (tamanho = volume de pedidos)

### Aba Dados
- Tabela interativa com os dados filtrados (500 linhas)
- Botao para download em CSV
- Resumo estatistico (describe) das variaveis numericas

### Filtros
- Categorias de produto (multiselect)
- Status do pedido (multiselect)
- Periodo de compra (slider por mes/ano)

## Tratamento dos Dados (Notebook)

O arquivo `Projeto.ipynb` documenta todo o processo de preparacao:

1. **Merge** de 3 datasets: `olist_orders`, `olist_order_items` e `olist_products`
2. **Conversao** de 6 colunas de data para datetime
3. **Preenchimento de nulos**: `order_approved_at` preenchido com data de compra; entregas nulas de pedidos delivered preenchidas com data estimada
4. **Correcao de status**: pedidos cancelados mas com entrega confirmada foram reclassificados como delivered
5. **Criacao de colunas**: `tempo_entrega` (dias) e `tempo_atraso` (booleano)
6. **Remocao de outliers**: percentis 1-99 para preco e frete
7. **Tratamento de nulos restantes**: categorias sem nome, descricoes, fotos; drop de linhas sem medidas fisicas

## Tecnologias

| Ferramenta | Uso |
|------------|-----|
| **Python** | Linguagem base |
| **Pandas / NumPy** | Manipulacao e limpeza de dados |
| **Seaborn / Matplotlib** | Visualizacoes na analise exploratoria |
| **Plotly** | Graficos interativos no dashboard |
| **Streamlit** | Framework web do dashboard |
| **Streamlit Cloud** | Deploy em producao |

## Estrutura

```
dashboard-olist/
├── Projeto.ipynb                         # Analise exploratoria completa
├── dashboard.py                          # Aplicacao Streamlit
├── olist_limpo_categorizado_projeto.csv  # Dataset tratado (gerado pelo notebook)
├── requirements.txt                      # Dependencias
├── .streamlit/
│   └── config.toml                       # Tema escuro
└── README.md
```

## Como Rodar Localmente

```bash
git clone https://github.com/Wisleyoliveira/dashboard-olist.git
cd dashboard-olist
pip install -r requirements.txt
streamlit run dashboard.py
```

## Dataset

Fonte: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)

Os arquivos originais (CSVs brutos) nao estao no repositorio. O dataset utilizado (`olist_limpo_categorizado_projeto.csv`) ja e o resultado do tratamento completo documentado no notebook.

## Autor

**Wisley Oliveira** — [GitHub](https://github.com/Wisleyoliveira)

---

> Projeto desenvolvido como avaliacao academica de analise de dados.
