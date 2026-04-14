# Dashboard de Vendas - Olist

Dashboard interativo de analise de vendas do e-commerce Olist, construido com Streamlit e Plotly.

**Acesse online:** [dashboard-olist-wisley.streamlit.app](https://dashboard-olist-wisley.streamlit.app)

---

## Visao Geral

Este projeto apresenta um painel completo para explorar dados de vendas da Olist, permitindo filtrar por categorias de produto, status de pedido e periodo. O dashboard oferece visualizacoes interativas sobre faturamento, entregas, frete e comportamento de compra.

## Funcionalidades

- **6 KPIs principais** — Faturamento, Frete Total, Pedidos, Ticket Medio, Entrega Media e Taxa de Entrega
- **15+ graficos interativos** com Plotly (area, barras, pizza, linha, box, scatter, heatmap, histograma)
- **5 abas organizadas** — Vendas, Entregas, Frete, Detalhamento e Dados
- **Filtros no sidebar** — Categorias, status do pedido e periodo (slider)
- **Tema escuro** profissional com CSS customizado
- **Download de dados** filtrados em CSV
- **Resumo estatistico** dos dados filtrados

## Screenshots

| KPIs | Graficos |
|------|----------|
| Faturamento, Pedidos, Ticket Medio... | Area, Barras, Pizza, Heatmap... |

## Tecnologias

| Tecnologia | Versao | Uso |
|------------|--------|-----|
| Python | 3.10+ | Linguagem base |
| Streamlit | >= 1.51 | Framework web |
| Pandas | >= 2.3 | Manipulacao de dados |
| NumPy | >= 2.0 | Operacoes numericas |
| Plotly | >= 6.0 | Graficos interativos |

## Estrutura do Projeto

```
dashboard-olist/
├── dashboard.py                          # Aplicacao principal
├── olist_limpo_categorizado_projeto.csv  # Dataset limpo e categorizado
├── requirements.txt                      # Dependencias
├── .streamlit/
│   └── config.toml                       # Configuracao de tema
├── .gitignore
└── README.md
```

## Como Executar Localmente

1. Clone o repositorio:
```bash
git clone https://github.com/Wisleyoliveira/dashboard-olist.git
cd dashboard-olist
```

2. Instale as dependencias:
```bash
pip install -r requirements.txt
```

3. Execute o dashboard:
```bash
streamlit run dashboard.py
```

O dashboard abrira automaticamente em `http://localhost:8501`.

## Dataset

Os dados sao originarios do [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) no Kaggle. O arquivo utilizado (`olist_limpo_categorizado_projeto.csv`) e uma versao limpa e consolidada, resultado do tratamento feito no notebook de analise exploratoria.

Tratamentos aplicados:
- Merge de 3 datasets (pedidos, itens e produtos)
- Conversao de datas
- Remocao de valores nulos
- Filtragem de outliers (percentis 1-99 para preco e frete)
- Categorizacao de produtos

## Autor

**Wisley Oliveira** — [GitHub](https://github.com/Wisleyoliveira)

---

> Projeto desenvolvido como parte de avaliacao academica de analise de dados.
