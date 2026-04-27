# BrasCo - Gaming Ltd.: Visão Estratégica & ROI

<p align="center">
<img src="./assets/img/fluxo.png" alt="Projeto Estratégico da BrasCo - Gaming Ltd" width="800px">
</p>

## 🎯 Problema de Negócio
A BrasCo é uma holding em expansão no setor de entretenimento, enfrenta o desafio de alocar capital de forma eficiente em um mercado de games saturado e de alto risco. O problema central é a fragmentação de dados que impede a BrasCo. de prever o sucesso comercial de novos títulos. Esta solução busca responder:
1. Quais estúdios apresentam o melhor custo-benefício de desenvolvimento (Ticket por Ponto de Score)?
2. Onde estão as oportunidades de mercado negligenciadas pela concorrência (Pérolas Escondidas)?
3. Qual melhor oportunidade de faturamento levando em conta o custo beneficio para lançamento de jogos ?

## 📈 Principas Resultados
Os insights trazidos por esse painel KPIs de negocio respondem as perguntas acima:
- Direcionar os esforços para o mercado da América do Norte (NA) garantindo o acesso a 37% do mercado global
- Associação com a Microsoft Corporation (atingimos todos os mercados) garantindo maior receita com menor exigência no Ticket por Ponto de Score ($0.32M) e focando no desenvolvimento do genero Shooter (excelente relação de "Média da Crítica vs. Média de Vendas")
- Para mitigação de risco, devemos construir títulos com nota alvo de 7.5 (Shooters são ótimo estando na casa do 7.2)
- Ficar atento com a mudança de geração (janela de oportunidade a partir do 3º ano do console quando a relação de vendas atinge 70/30 (Antiga/Nova) migrando os investimentos em novos titulos com segurança)
- Investimento de Alto Risco🚨: O Genero de RPG de boa avaliação com baixa venda devido a nicho ser concentrado no Japão (temos que buscar a Bandai como parceira e um estúdio local para produzir uma história com apelo ao local)

## 📂 Fonte de Dados
Os dados utilizados são públicos e foram coletados via Kaggle:

https://www.kaggle.com/datasets/asaniczka/video-game-sales-2024

## 🛠️ Stack Técnica
As seguintes ferramentas e bibliotecas foram utilizadas no desenvolvimento deste projeto:
- Linguagem: Python 3.8+
- Framework Web: Streamlit
- Manipulação de Dados: Pandas, NumPy
- Visualização de Dados: Plotly
- Gerenciamento de Ambiente: pip

## 🧱 Processo de Analise: Arquitetura de Dados (Medallion Architecture)
Para garantir a confiabilidade, implementei uma lógica de processamento em camadas, otimizada em Python:
-🥉 Camada Bronze (Raw): Preservação do dataset original do kaggle.
-🥈 Camada Silver (Trusted): Processo intensivo de limpeza, tratamento e padronização de nomes de holdings, remoção de duplicatas e ingestão de dados históricos dentre os principais a classificação do jogo pelo critic_score, fabricantes, geração dos consoles, anos de atividade do console, data de lançamentos dos consoles e paises de developers e publishers
-🥇 Camada Gold (Refined): Agregação de dados para criação dos KPIs de negócio (ROI, Attach Rate, Market Share) prontos para consumo no Dashboard.

## Integridade dos Dados
A integridade dos dados foi conferida por check de nulos e anomalia de volume nas vendas (total_sales; na_sales, jp_sales, pal_sales, other_sales)

## 📂 Arquitetura do Projeto
### A estrutura do repositório está organizada da seguinte forma:

```text
video_games_sales/
├── assets/             # Imagens e recursos visuais utilizados no README e os dados brutos video_game_sales.csv e dataset_limpeza.
├── notebooks           # Jupyter Notebook com o código da limpeza de dados e enriquecimento de informações do dataset
├── pages/              # Páginas secundárias do dashboard Streamlit
├── utils/              # Funções relacionadas a limpeza de dados e carregamento do sidebar com os filtros como funçõe úteis
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git.
├── app.py              # Arquivo principal que renderiza a página inicial do dashboard com as principais instruções.
├── LICENSE             # Licença MIT do projeto.
├── README.md           # Documentação principal do projeto.
└── requirements.txt    # Lista de bibliotecas Python necessárias.
```

## 📈 Funcionalidades e Visualizações
#### O dashboard está dividido em seis paginas com visão estratégicas do mercado com relação a empresas, consoles e consumidores. Todas as páginas são acessíveis pelo menu lateral e os gráficos são interativos podendo ser filtrados pela geração dos consoles e as principais empresas do mercado, além de um filtro avançado com o genero e o console no menu lateral:

1. Marketplace Overview (Página Inicial)
- Focada em métricas de volume total do mercado e dominância geográfica.
- Métricas Chave (KPIs): Volume Total de Vendas (Global), Contagem de Títulos Únicos e Market Share por Região (NA, EU, JP).
- Gráficos: Mapa de Distribuição de Vendas por País e Gráfico de Market Share Regional.

2. Market Cycles
- Focada em métricas de evolução temporal das vendas e comportamento das gerações de consoles.
- Métricas Chave: Crescimento de 123% nas vendas a partir do 3º ano da geração, Relação de Transição 70/30 (Antiga/Nova) e Ano de Pico de Vendas.
- Gráficos: Gráfico de Linhas de Ciclo de Vendas Geracional e Gráfico de Gantt de Ciclo de Vida de Hardware.

3. Asset Efficieny
- Focada em métricas de eficiência de conversão de hardware em software e longevidade de plataformas.
- Métricas Chave: Attach Rate (Vendas por Título), Longevidade Média de Consoles (11 anos para Sony) e Dias até o Primeiro Hit.
- Gráficos: Gráfico de Barras de Attach Ratio por Console e Heatmap de Vitalidade de Hardware.

4. Consumer Behavior
- Focada em métricas de afinidade cultural por gêneros e rentabilidade por tipo de jogo.
- Métricas Chave: Índice de Afinidade Regional (0.8+ para Shooters/Action), Rentabilidade por Gênero e Popularidade Geracional.
- Gráficos: Heatmap de Afinidade de Gênero por Região e Matriz de Rentabilidade vs. Recepção Crítica.

5. Competitive Intelligence
- Focada em métricas de performance comparativa entre Holdings e influência geopolítica na publicação.
- Métricas Chave: Ticket por Ponto de Score ($0.32M para Microsoft), Market Share Global das Top Holdings (37% EA/MS) e Índice de Exportação.
- Gráficos: Treemap de Market Share por Holding e Heatmap de Sinergia Nacional (Desenvolvedor x Distribuidor).

6. Predictive Vality
- Focada em métricas de correlação entre qualidade (Score) e retorno financeiro para mitigação de risco.
- Métricas Chave: Multiplicador de Vendas por Score, Threshold de Nota Alvo (7.5) e Data Reliability Index.
- Gráficos: Gráfico de Dispersão com Quadrantes (Hype vs. Pérolas Escondidas) e Curva de Valor Exponencial por Critic Score.

## 👩‍💻 Autor
 Desenvolvido por Guilherme Grandim como um projeto de portifólio em Ciencias/Analise de Dados</br>
 Sinta-se à vontade para entrar em contato ou contribuir com o projeto!

