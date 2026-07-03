# 🎮 BrasCo - Gaming Ltd: Visão Estratégica & ROI

Dashboard analítico para direcionar a alocação de capital da BrasCo no mercado global de video games, com painel interativo em produção no Streamlit Cloud.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.7-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

⚠️ O app pode levar ~30s para inicializar se estiver inativo.

Link para o projeto: https://brasco-videogames-sales.streamlit.app

<p align="center">
<img src="./assets/img/fluxo.png" alt="Projeto Estratégico da BrasCo - Gaming Ltd" width="800px">
</p>

### 🎯 Destaques
- Construí um dashboard de 7 páginas que consolida o histórico global de vendas de games em um score de Oportunidade x Risco por gênero, dando ao CEO da BrasCo uma recomendação de investimento acionável em minutos.
- Identifiquei que o gênero Shooter é a melhor aposta de investimento (alta venda + alto alcance geográfico + baixo custo por ponto de crítica com a Microsoft), enquanto RPG é alto risco por concentração de mercado no Japão.
- Implementei uma arquitetura de dados em camadas (Bronze/Silver/Gold) para garantir rastreabilidade da limpeza até os KPIs de negócio (ROI, Attach Rate, Market Share) consumidos no dashboard.

---

## 🚨 Problema de Negócio

A BrasCo é uma holding em expansão no setor de entretenimento e enfrenta o desafio de alocar capital de forma eficiente em um mercado de games saturado e de alto risco.

Até então, decisões de investimento em novos títulos eram tomadas sem uma leitura consolidada do histórico de mercado — sem visibilidade clara sobre quais gêneros, plataformas, regiões e parcerias realmente maximizam retorno e minimizam risco.

**Pergunta central:** Onde a BrasCo deve investir para maximizar o sucesso comercial de novos lançamentos, minimizando o risco de mercado?

**Minha tarefa:** projetar e construir um dashboard analítico que traduzisse o histórico global de vendas em decisões acionáveis de investimento para o CEO da BrasCo.

---

## 🗺️ Planejamento da Solução

A solução foi estruturada em uma arquitetura de dados em camadas (**Medallion Architecture**), seguida de um dashboard com 7 páginas de análise estratégica:

1. **Camada Bronze (Raw)** — preservação do dataset original do Kaggle.

2. **Camada Silver (Trusted)** — limpeza, tratamento e padronização de nomes de holdings, remoção de duplicatas e ingestão de dados históricos, incluindo classificação Premium (critic_score >= 9), fabricantes, geração dos consoles, anos de atividade e datas de lançamento, além dos países de developers e publishers.

3. **Camada Gold (Refined)** — agregação de dados para criação dos KPIs de negócio (ROI, Attach Rate, Market Share) prontos para consumo no dashboard.

4. **Construção do dashboard** — 7 páginas interativas cobrindo visão de mercado, ciclos de hardware, eficiência de ativos, comportamento do consumidor, inteligência competitiva, validade preditiva e uma síntese executiva final, todas filtráveis por geração de console e principais empresas do mercado.

**Ferramentas:** Python 3.10 (Pandas, NumPy, Plotly), Streamlit, pip.

---

## 🛠️ Desenvolvimento

### Dataset

| Atributo | Detalhe |
|---|---|
| Fonte | [Kaggle — Video Game Sales 2024](https://www.kaggle.com/datasets/asaniczka/video-game-sales-2024) |
| Granularidade | 1 linha = 1 título de jogo por plataforma |
| Integridade | Verificação de valores nulos e anomalias de volume nas vendas (total_sales, na_sales, jp_sales, pal_sales, other_sales) |

### Páginas do Dashboard

1. **Marketplace Overview**
- Focada em métricas de volume total do mercado e dominância geográfica.
- Métricas Chave (KPIs): Volume Total de Vendas (Global), Contagem de Títulos Únicos e Market Share por Região (NA, EU, JP).
- Gráficos: Mapa de Distribuição de Vendas por País e Gráfico de Market Share Regional.

2. **Market Cycles**
- Focada em métricas de evolução temporal das vendas e comportamento das gerações de consoles.
- Métricas Chave: Crescimento de 123% nas vendas a partir do 3º ano da geração, Relação de Transição 70/30 (Antiga/Nova) e Ano de Pico de Vendas.
- Gráficos: Gráfico de Linhas de Ciclo de Vendas Geracional e Gráfico de Gantt de Ciclo de Vida de Hardware.

3. **Asset Efficiency**
- Focada em métricas de eficiência de conversão de hardware em software e longevidade de plataformas.
- Métricas Chave: Attach Rate (Vendas por Título), Longevidade Média de Consoles (11 anos para Sony) e Dias até o Primeiro Hit.
- Gráficos: Gráfico de Barras de Attach Ratio por Console e Heatmap de Vitalidade de Hardware.

4. **Consumer Behavior**
- Focada em métricas de afinidade cultural por gêneros e rentabilidade por tipo de jogo.
- Métricas Chave: Índice de Afinidade Regional (0.8+ para Shooters/Action), Rentabilidade por Gênero e Popularidade Geracional.
- Gráficos: Heatmap de Afinidade de Gênero por Região e Matriz de Rentabilidade vs. Recepção Crítica.

5. **Competitive Intelligence**
- Focada em métricas de performance comparativa entre Holdings e influência geopolítica na publicação.
- Métricas Chave: Ticket por Ponto de Score ($0.32M para Microsoft), Market Share Global das Top Holdings (37% EA/MS) e Índice de Exportação.
- Gráficos: Treemap de Market Share por Holding e Heatmap de Sinergia Nacional (Desenvolvedor x Distribuidor).

6. **Predictive Validity**
- Focada em métricas de correlação entre qualidade (Score) e retorno financeiro para mitigação de risco.
- Métricas Chave: Multiplicador de Vendas por Score, Threshold de Nota Alvo (8) e Index do Critic_Score.
- Gráficos: Gráfico de Dispersão com Quadrantes (Hype vs. Pérolas Escondidas), Nota Ótima de Aumento de Vendas.

7. **Launch Recommendation**
- Síntese executiva que combina as 6 dimensões de análise em um score composto por gênero.
- Métricas Chave: Score de Oportunidade (0–100), Score de Risco (0–100), Melhor Plataforma por Gênero e Nota Mínima Sugerida.
- Gráficos: Ranking Horizontal de Oportunidade vs Risco (barras + marcadores) e Tabela de Sub-métricas por Gênero.

### Estrutura do Projeto

```text
video_games_sales/
├── assets/             # Imagens e recursos visuais utilizados no README e os dados brutos video_game_sales.csv e dataset_limpeza.
├── notebooks/          # Jupyter Notebook com o código da limpeza de dados e enriquecimento de informações do dataset
├── pages/              # Páginas secundárias do dashboard Streamlit
├── utils/              # Funções relacionadas a limpeza de dados e carregamento do sidebar com os filtros como funções úteis
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git.
├── app.py              # Arquivo principal que renderiza a página inicial do dashboard com as principais instruções.
├── LICENSE             # Licença MIT do projeto.
├── README.md           # Documentação principal do projeto.
└── requirements.txt    # Lista de bibliotecas Python necessárias.
```

### Como Executar Localmente

```bash
git clone https://github.com/guigrandim/video_games_sales.git
cd video_games_sales
pip install -r requirements.txt
streamlit run app.py
```

---

## 💡 Top Insights

### 1. 🌎 América do Norte concentra o maior market share global

Direcionar os esforços para o mercado da América do Norte (NA) garante acesso a **37% do mercado global**, tornando-a a região prioritária para lançamentos.

---

### 2. 🔄 A janela de transição de geração começa no 3º ano do console

A partir do 3º ano de vida de um console, a relação de vendas entre a geração antiga e a nova atinge **70/30**, sinalizando o ponto seguro para migrar investimentos em novos títulos para a plataforma seguinte.

---

### 3. 🎯 Shooter é o gênero de melhor relação crítica x vendas com a Microsoft

A associação com a Microsoft Corporation garante maior receita com menor exigência no Ticket por Ponto de Score (**$0,32M**), com o gênero **Shooter** apresentando a melhor relação entre média da crítica e média de vendas — performando bem a partir de nota 7.2.

---

### 4. 🚨 RPG é um investimento de alto risco apesar da boa avaliação crítica

Apesar da boa recepção crítica, as vendas de RPG são altamente concentradas no Japão, elevando o score de risco regional. Viabilizar esse gênero exige parceria com a Bandai e um estúdio local para garantir apelo regional.

---

## 📊 Resultados

### Resultado da Entrega

O dashboard substituiu a análise manual e pontual do histórico de vendas por um painel de autoatendimento: o CEO e os times de investimento passaram a consultar 7 dimensões de mercado (volume, ciclo de hardware, eficiência, comportamento, competição, validade preditiva e recomendação de lançamento) em minutos, com filtros por geração de console e por empresa, sem depender de uma nova análise ad-hoc a cada decisão.

### Dashboard

| Competitive Intelligence — Treemap de Market Share | Consumer Behavior — Heatmap de Afinidade de Gênero |
|:---:|:---:|
| ![Competitive Intelligence](./assets/img/competitive_intelligence.png) | ![Consumer Behavior](./assets/img/consumer_behavior.png) |

| Market Cycles — Gantt de Ciclo de Vida de Hardware | Market Cycles — Curva de Vendas por Geração |
|:---:|:---:|
| ![Market Cycles Gantt](./assets/img/market_cycles_gantt.png) | ![Market Cycles](./assets/img/market_cycles.png) |

### Síntese — Launch Recommendation (Página 7)

O score composto de **Oportunidade** (40% volume de vendas + 30% alcance geográfico + 30% multiplicador de crítica) e **Risco** (40% concentração regional + 30% sensibilidade de vendas + 30% saturação de mercado) confirma o **Shooter como melhor aposta histórica**: alta média de vendas, amplo alcance geográfico e forte multiplicador de crítica.

A visão por geração revela ainda que a última geração de consoles apresenta reconfiguração de gêneros líderes, com Sports e Racing crescendo em penetração — uma oportunidade de diversificação de portfólio.

---

## ✅ Conclusões

Os resultados demonstram que, com base na análise histórica de mercado, o foco de investimento deve ser na **América do Norte** (37% do market share), em parceria com a **Microsoft Corporation** para otimizar a receita com baixo custo por ponto de score ($0,32M), desenvolvendo títulos do gênero **Shooter** e observando o 3º ano da geração de novos consoles — ponto em que a curva de vendas começa a migrar para a nova plataforma.

A página de síntese **Launch Recommendation** consolida as seis dimensões de análise em um único score de oportunidade e risco por gênero, transformando seis painéis de análise em uma recomendação de lançamento acionável e baseada em evidências históricas.

**Próximos passos:**
- Incorporar dados de vendas mais recentes à medida que novas gerações de consoles ganharem tração
- Expandir o score de oportunidade/risco para o nível de plataforma, além de gênero
- Adicionar simulação de cenários (what-if) para testar hipóteses de investimento diretamente no dashboard

**Limitações:** O dataset reflete o histórico de vendas disponível publicamente no Kaggle, sem dados proprietários de custo de desenvolvimento por título, o que limita o cálculo de ROI a proxies como o Ticket por Ponto de Score.

---

*📁 Dados: [Video Game Sales 2024 (Kaggle)](https://www.kaggle.com/datasets/asaniczka/video-game-sales-2024) · 🥇 Medallion Architecture · 🎮 Streamlit + Plotly*

## 🧰 Skills Demonstradas

- **Engenharia de dados:** arquitetura em camadas (Bronze/Silver/Gold), limpeza e padronização de dados históricos, verificação de integridade (nulos, anomalias de volume).
- **Análise de negócio:** tradução de métricas de mercado em KPIs acionáveis (ROI, Attach Rate, Market Share, Score de Oportunidade x Risco).
- **Visualização de dados:** dashboards interativos multi-página com Plotly/Streamlit, incluindo treemap, heatmap, Gantt e gráficos de dispersão com quadrantes.
- **Comunicação executiva:** síntese de 6 dimensões analíticas em uma única recomendação de lançamento para tomada de decisão do CEO.

## 👩‍💻 Autor

Desenvolvido por Guilherme Grandim como um projeto de portfólio em Ciências/Análise de Dados.
Sinta-se à vontade para entrar em contato ou contribuir com o projeto!
Linkedin: [ℹ️](https://www.linkedin.com/in/guilherme-grandim/)
Gmail: [📧](mailto:gui.grandim@gmail.com)

## 📄 Licença

Este projeto está sob a licença MIT — veja [LICENSE](./LICENSE) para detalhes.
