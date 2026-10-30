# 📊 Portal de Inteligência Educacional: Indicadores por Região (INEP / MEC)

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Plotly](https://img.shields.io/badge/Plotly-7.1.0-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Produção-34D399)](#)
[![Interface](https://img.shields.io/badge/Design-Dark%20Premium-0F172A)](#)

Análise Exploratória de Dados (EDA) Avançada e Dashboard Executivo Interativo desenvolvidos com foco em **Censo Escolar da Educação Básica (INEP / MEC)**. A solução combina modelagem estatística em Python, matrizes de correlação, detecção de anomalias (IQR) e um Dashboard Web Dark Premium com **filtros reativos client-side em tempo real** e **drill-down geográfico**.

---

## ⚡ Direto ao Ponto: O que é cada Indicador? (TDAH Friendly)

* 📈 **Taxa de Aprovação:** A porcentagem de estudantes que passaram de série.
* 🚪 **Taxa de Abandono (Evasão):** Alunos que abandonaram a escola antes do final do ano letivo.
* ⏳ **TDI (Distorção Idade-Série):** Alunos com 2 ou mais anos de atraso escolar para a série ideal.
* 🎓 **DSU (Docentes com Curso Superior):** Proporção de professores com nível superior completo.
* ⏰ **HAD (Horas-Aula Diária):** Média de horas de permanência diária do aluno na escola.
* 👥 **ATU (Alunos por Turma):** Número médio de estudantes por sala de aula.

---

## 🚀 Principais Recursos do Dashboard

1. **Reatividade Instantânea em JavaScript (Client-Side Real):**
   * Mais de 1.700 registros reais higienizados embutidos em JSON.
   * Filtros dinâmicos por **Ano** (2024 a 2013), **Macrorregião**, **Localização** (Urbana/Rural) e **Rede** (Pública, Privada, Estadual, Municipal, Federal).
   * Atualização em tempo real de KPIs, gráficos e tabelas em menos de 10 milissegundos.

2. **Mapa Interativo & Drill-Down Regional:**
   * Navegue pelas 5 macrorregiões do Brasil (Norte, Nordeste, Centro-Oeste, Sudeste, Sul).
   * Ficha Diagnóstica Exclusiva com pontos fortes e alertas para políticas públicas.

3. **Design Dark Premium:**
   * Fundo escuro tecnológico (`#080C14` / `#0F172A`), destaques em ciano, esmeralda, âmbar e carmesim.
   * Cards com microinterações, glassmorphism e tipografia moderna.

4. **Investigação Estatística Aprofundada:**
   * Matriz de Correlação Linear de Pearson (Heatmap).
   * Detecção de Outliers e gargalos críticos pelo método IQR.
   * Série Temporal Histórica (2013–2024).

---

## 📂 Estrutura do Repositório

```
BD_graficos/
├── README.md                                  # Documentação executiva completa
├── index.html                                 # Dashboard Dark Premium Web Interativo
├── requirements.txt                           # Dependências do projeto Python
├── ATV_avaliativa/
│   ├── br_inep_indicadores_educacionais_regiao.csv  # Base bruta tratada do INEP
│   ├── eda_completa_inep.ipynb                # Jupyter Notebook com análise estatística
│   ├── eda_indicadores_educacionais.ipynb     # Notebook com visualizações Plotly
│   ├── eda_indicadores_educacionais.py        # Script Python modularizado
│   ├── build_full_project.py                  # Script gerador do ecossistema
│   ├── index.html                             # Cópia do Dashboard
│   ├── relatorio_eda_educacional.html         # Relatório autônomo offline
│   └── requirements.txt                       # Dependências
```

---

## 🛠️ Como Executar Localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/Victor782-cpu/BD_graficos.git
cd BD_graficos
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Abrir o Dashboard no Navegador
Basta abrir o arquivo `index.html` em qualquer navegador (Chrome, Edge, Firefox) ou iniciar um servidor local:
```bash
python -m http.server 8050
```
E acesse: [http://localhost:8050/](http://localhost:8050/)

### 4. Executar os Scripts de Análise
```bash
python ATV_avaliativa/eda_indicadores_educacionais.py
```

---

## 📌 Principais Descobertas Científicas (Censo 2024)

1. **Impacto da Distorção Idade-Série (TDI):** Forte correlação negativa ($r = -0,78$) com a aprovação. Turmas com alto atraso escolar apresentam maior propensão à evasão.
2. **Efeito Protetor da Escola em Tempo Integral (HAD):** Correlação positiva ($r = +0,50$) com aprovação e redução do abandono. O Nordeste lidera o país com média de 6,5 horas/dia.
3. **Vulnerabilidade da Rede Municipal no Ensino Médio:** Redes municipais em zonas periféricas e rurais concentram as maiores taxas de abandono do país (até 21,8%).

---

**Desenvolvido para fins acadêmicos e apoio à tomada de decisão em Políticas Públicas Educacionais.**
