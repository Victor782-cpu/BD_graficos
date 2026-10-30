"""
========================================================================================
ANÁLISE EXPLORATÓRIA DE DADOS (EDA): INDICADORES EDUCACIONAIS POR REGIÃO (INEP / MEC)
========================================================================================
Especialista: Ciência de Dados & Visualização de Informação
Objetivo: Transformar dados educacionais brutos em diagnósticos visuais interativos,
          autoexplicativos e de alto impacto para gestores públicos, pedagogos e cidadãos.
========================================================================================
"""

import os
import sys
import csv
import webbrowser

# Garante compatibilidade de saída UTF-8 no console Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# ======================================================================================
# CONFIGURAÇÕES GLOBAIS E COORDENADAS GEOGRÁFICAS
# ======================================================================================

# Coordenadas geográficas dos centróides das 5 macrorregiões do Brasil
COORDENADAS_REGIOES = {
    'Norte':        {'lat': -3.4653, 'lon': -62.2159},
    'Nordeste':     {'lat': -8.2815, 'lon': -39.4674},
    'Centro-Oeste': {'lat': -14.6508, 'lon': -52.4934},
    'Sudeste':      {'lat': -20.3155, 'lon': -45.0528},
    'Sul':          {'lat': -27.6326, 'lon': -51.3304}
}

# Paleta de cores institucionais e acessíveis
PALETA_CORES = {
    'Nordeste':     '#E65100',  # Laranja quente
    'Norte':        '#2E7D32',  # Verde floresta
    'Centro-Oeste': '#F57F17',  # Âmbar dourado
    'Sudeste':      '#1565C0',  # Azul safira
    'Sul':          '#6A1B9A'   # Roxo ametista
}

TEMPLATE_PLOTLY = 'plotly_white'


# ======================================================================================
# 1. CARREGAMENTO E TRATAMENTO SEGURO DOS DADOS
# ======================================================================================

def detectar_encoding(caminho_arquivo: str) -> str:
    """
    Identifica automaticamente a codificação (encoding) do arquivo CSV.
    Testa sequencialmente as opções mais frequentes no ecossistema de dados brasileiro.
    """
    encodings_candidatos = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    for enc in encodings_candidatos:
        try:
            with open(caminho_arquivo, 'r', encoding=enc) as f:
                f.read(8192)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return 'utf-8'


def detectar_separador(caminho_arquivo: str, encoding: str = 'utf-8') -> str:
    """
    Identifica de forma segura o delimitador (vírgula, ponto e vírgula, tabulação).
    """
    try:
        with open(caminho_arquivo, 'r', encoding=encoding) as f:
            amostra = f.read(4096)
            sniffer = csv.Sniffer()
            delimitador = sniffer.sniff(amostra).delimiter
            if delimitador in [',', ';', '\t']:
                return delimitador
    except Exception:
        pass

    # Fallback por contagem de ocorrência na primeira linha
    with open(caminho_arquivo, 'r', encoding=encoding) as f:
        primeira_linha = f.readline()
        qtd_ponto_virgula = primeira_linha.count(';')
        qtd_virgula = primeira_linha.count(',')
        qtd_tab = primeira_linha.count('\t')

        if qtd_ponto_virgula > qtd_virgula and qtd_ponto_virgula > qtd_tab:
            return ';'
        elif qtd_tab > qtd_virgula:
            return '\t'
        return ','


def carregar_e_tratar_dados(caminho_arquivo: str) -> pd.DataFrame:
    """
    Executa o pipeline seguro de carregamento, auditoria e tipagem de dados.
    - Detecta automaticamente separador e encoding.
    - Garante tipos categóricos para texto e numéricos com precisão decimal.
    - Elimina duplicidades e trata dados nulos com rigor estatístico.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não localizado no caminho: {caminho_arquivo}")

    encoding = detectar_encoding(caminho_arquivo)
    separador = detectar_separador(caminho_arquivo, encoding=encoding)

    print(f"\n" + "="*70)
    print(f"[INFO] INGESTÃO DE DADOS SEGURO")
    print(f"="*70)
    print(f" Arquivo detectado: {os.path.basename(caminho_arquivo)}")
    print(f" Encoding identificado: {encoding}")
    print(f" Separador identificado: '{separador}'")

    # Leitura inicial do CSV
    df = pd.read_csv(caminho_arquivo, sep=separador, encoding=encoding, low_memory=False)

    # 1. Higienização das colunas categóricas essenciais
    colunas_categoricas = ['regiao', 'localizacao', 'rede']
    for col in colunas_categoricas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 2. Conversão da coluna de ano
    if 'ano' in df.columns:
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce').fillna(0).astype(int)

    # 3. Conversão de colunas numéricas (indicadores, taxas, médias)
    colunas_metadados = {'ano', 'regiao', 'localizacao', 'rede'}
    colunas_numericas = [c for c in df.columns if c not in colunas_metadados]

    for col in colunas_numericas:
        if df[col].dtype == object:
            # Substitui vírgula decimal brasileira por ponto se necessário
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. Tratamento de registros duplicados nas chaves fundamentais
    duplicados = df.duplicated(subset=['ano', 'regiao', 'localizacao', 'rede']).sum()
    if duplicados > 0:
        print(f"  Aviso: {duplicados} registros duplicados detectados e consolidados.")
        df = df.drop_duplicates(subset=['ano', 'regiao', 'localizacao', 'rede']).copy()

    # Auditoria resumida dos dados
    anos_disponiveis = sorted(df['ano'].unique())
    regioes_disponiveis = df['regiao'].unique().tolist()

    print(f" Dimensões finais limpas: {df.shape[0]} linhas × {df.shape[1]} colunas")
    print(f" Período temporal coberto: de {anos_disponiveis[0]} até {anos_disponiveis[-1]}")
    print(f" Macrorregiões presentes: {', '.join(regioes_disponiveis)}")
    print(f"="*70)

    return df


# ======================================================================================
# 2. ANÁLISES EDUCACIONAIS E VISUALIZAÇÕES INTERATIVAS COM PLOTLY
# ======================================================================================

def plot_ranking_regional_aprovacao(df: pd.DataFrame, ano_referencia: int = 2024) -> go.Figure:
    """
    [GRÁFICO 1 - COMPARATIVO ENTRE REGIÕES]
    Gráfico de barras horizontais ordenadas (do melhor para o pior resultado).
    Compara a Taxa de Aprovação no Ensino Médio consolidada (Rede Total e Localização Total).
    
    Insight Educacional:
    Permite identificar instantaneamente o ranking de eficiência escolar do país,
    destacando o protagonismo ou necessidade de intervenção pedagógica regional.
    """
    df_filtrado = df[
        (df['ano'] == ano_referencia) &
        (df['localizacao'] == 'Total') &
        (df['rede'] == 'Total')
    ].copy()

    if df_filtrado.empty:
        ano_referencia = df[df['taxa_aprovacao_em'].notna()]['ano'].max()
        df_filtrado = df[
            (df['ano'] == ano_referencia) &
            (df['localizacao'] == 'Total') &
            (df['rede'] == 'Total')
        ].copy()

    df_ordenado = df_filtrado.sort_values(by='taxa_aprovacao_em', ascending=True)

    fig = px.bar(
        df_ordenado,
        x='taxa_aprovacao_em',
        y='regiao',
        orientation='h',
        text=df_ordenado['taxa_aprovacao_em'].apply(lambda v: f"{v:.1f}%"),
        color='taxa_aprovacao_em',
        color_continuous_scale='Teal',
        template=TEMPLATE_PLOTLY,
        title=f"<b>Ranking Regional: Taxa de Aprovação no Ensino Médio ({ano_referencia})</b><br>"
              f"<span style='font-size:13px; color:#555;'>Média consolidada por Macrorregião (Redes Públicas e Privadas integradas)</span>"
    )

    fig.update_traces(
        textposition='outside',
        textfont=dict(size=13, color='#111', family='Segoe UI, Arial'),
        marker_line_width=1,
        marker_line_color='#2c3e50',
        hovertemplate=(
            "<b>Macrorregião:</b> %{y}<br>"
            "<b>Taxa de Aprovação:</b> %{x:.2f}%<br>"
            "<b>Ano Letivo:</b> " + str(ano_referencia) + "<br>"
            "<extra></extra>"
        )
    )

    media_nacional = df_ordenado['taxa_aprovacao_em'].mean()
    fig.add_vline(
        x=media_nacional,
        line_dash="dash",
        line_color="#E53935",
        line_width=2,
        annotation_text=f"Média Nacional: {media_nacional:.1f}%",
        annotation_position="top right",
        annotation_font=dict(color="#B71C1C", size=11, family='Segoe UI, Arial')
    )

    fig.update_layout(
        xaxis=dict(
            title="<b>Taxa de Aprovação (%)</b>",
            range=[min(70, df_ordenado['taxa_aprovacao_em'].min() - 5), 103],
            ticksuffix="%",
            gridcolor="#E0E0E0"
        ),
        yaxis=dict(title="<b>Macrorregião Brasileira</b>"),
        coloraxis_showscale=False,
        height=450,
        margin=dict(l=100, r=60, t=80, b=60)
    )

    return fig


def plot_desigualdade_regional_boxplot(df: pd.DataFrame, ano_referencia: int = 2024) -> go.Figure:
    """
    [GRÁFICO 2 - DESIGUALDADE E DISPARIDADE INTRA-REGIONAL]
    Gráfico de Caixa (Box Plot) com pontos individuais sobrepostos mostrando a dispersão
    da Taxa de Abandono Escolar no Ensino Médio entre as diferentes redes de ensino e localizações.
    
    Insight Educacional:
    Métricas agregadas escondem abismos sociais. Este gráfico expõe a severidade da desigualdade
    interna em cada região, apontando onde estão os casos mais alarmantes de evasão.
    """
    df_box = df[
        (df['ano'] == ano_referencia) &
        (df['rede'] != 'Total') &
        (df['localizacao'] != 'Total') &
        (df['taxa_abandono_em'].notna())
    ].copy()

    ordem_regioes = df_box.groupby('regiao')['taxa_abandono_em'].median().sort_values(ascending=False).index.tolist()

    fig = px.box(
        df_box,
        x='regiao',
        y='taxa_abandono_em',
        color='regiao',
        color_discrete_map=PALETA_CORES,
        category_orders={'regiao': ordem_regioes},
        points='all',
        hover_data={
            'regiao': False,
            'rede': True,
            'localizacao': True,
            'taxa_abandono_em': ':.1f'
        },
        template=TEMPLATE_PLOTLY,
        title=f"<b>Desigualdade Regional: Disparidade da Taxa de Abandono Escolar no Ensino Médio ({ano_referencia})</b><br>"
              f"<span style='font-size:13px; color:#555;'>Distribuição entre Redes (Municipal, Estadual, Federal, Privada) e Zonas (Urbana e Rural)</span>"
    )

    for trace in fig.data:
        trace.hovertemplate = (
            "<b>Região:</b> %{x}<br>"
            "<b>Taxa de Abandono:</b> %{y:.2f}%<br>"
            "<b>Rede de Ensino:</b> %{customdata[0]}<br>"
            "<b>Localização:</b> %{customdata[1]}<br>"
            "<extra></extra>"
        )

    fig.update_layout(
        xaxis=dict(title="<b>Macrorregião Brasileira</b>"),
        yaxis=dict(
            title="<b>Taxa de Abandono Escolar (%)</b>",
            ticksuffix="%",
            gridcolor="#E0E0E0"
        ),
        showlegend=False,
        height=520,
        margin=dict(l=80, r=40, t=80, b=60)
    )

    return fig


def plot_mapa_interativo_brasil(df: pd.DataFrame, ano_referencia: int = 2024) -> go.Figure:
    """
    [GRÁFICO 3 - VISÃO GEOGRÁFICA INTERATIVA]
    Mapa interativo com centróides das 5 macrorregiões brasileiras.
    Marcadores circulares com tamanho proporcional à Taxa de Aprovação,
    coloridos por intensidade térmica e dotados de cartão hover com síntese diagnóstica.
    
    Insight Educacional:
    Fornece ao gestor visão territorial imediata sobre a geografia da educação no país,
    associando indicadores de fluxo (aprovação e abandono) com esforço docente.
    """
    df_mapa = df[
        (df['ano'] == ano_referencia) &
        (df['localizacao'] == 'Total') &
        (df['rede'] == 'Total')
    ].copy()

    df_mapa['lat'] = df_mapa['regiao'].map(lambda r: COORDENADAS_REGIOES.get(r, {}).get('lat', np.nan))
    df_mapa['lon'] = df_mapa['regiao'].map(lambda r: COORDENADAS_REGIOES.get(r, {}).get('lon', np.nan))

    for col in ['taxa_aprovacao_em', 'taxa_abandono_em', 'tdi_em', 'dsu_em', 'had_em']:
        if col not in df_mapa.columns:
            df_mapa[col] = 0.0
        else:
            df_mapa[col] = df_mapa[col].fillna(0.0)

    try:
        fig = px.scatter_map(
            df_mapa,
            lat='lat',
            lon='lon',
            size='taxa_aprovacao_em',
            color='taxa_aprovacao_em',
            color_continuous_scale='Viridis',
            size_max=38,
            zoom=3.0,
            center={'lat': -14.2350, 'lon': -53.1805},
            template=TEMPLATE_PLOTLY,
            title=f"<b>Panorama Geográfico: Taxa de Aprovação Escolar por Macrorregião ({ano_referencia})</b><br>"
                  f"<span style='font-size:13px; color:#555;'>Dimensão territorial brasileira — Passe o cursor sobre os pontos para diagnóstico completo</span>"
        )
    except Exception:
        fig = px.scatter_geo(
            df_mapa,
            lat='lat',
            lon='lon',
            size='taxa_aprovacao_em',
            color='taxa_aprovacao_em',
            color_continuous_scale='Viridis',
            size_max=38,
            scope='south america',
            center={'lat': -14.2350, 'lon': -53.1805},
            template=TEMPLATE_PLOTLY,
            title=f"<b>Panorama Geográfico: Taxa de Aprovação Escolar por Macrorregião ({ano_referencia})</b><br>"
                  f"<span style='font-size:13px; color:#555;'>Dimensão territorial brasileira — Passe o cursor sobre os pontos para diagnóstico completo</span>"
        )

    fig.update_traces(
        customdata=df_mapa[['regiao', 'taxa_aprovacao_em', 'taxa_abandono_em', 'tdi_em', 'dsu_em', 'had_em']].values,
        hovertemplate=(
            "<div style='font-family: Segoe UI, Arial; padding: 4px;'>"
            "<b style='font-size:15px; color:#0D47A1;'>Macrorregião %{customdata[0]}</b><br><hr style='margin:4px 0;'>"
            "• <b>Taxa de Aprovação (EM):</b> %{customdata[1]:.1f}%<br>"
            "• <b>Taxa de Abandono Escolar:</b> %{customdata[2]:.1f}%<br>"
            "• <b>Distorção Idade-Série:</b> %{customdata[3]:.1f}%<br>"
            "• <b>Docentes c/ Ensino Superior:</b> %{customdata[4]:.1f}%<br>"
            "• <b>Carga Horária Média:</b> %{customdata[5]:.1f} horas/dia"
            "</div><extra></extra>"
        )
    )

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="<b>Aprovação (%)</b>",
            ticksuffix="%"
        ),
        height=540,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig


def plot_extremos_top_bottom(df: pd.DataFrame, ano_referencia: int = 2024, n_extremos: int = 5) -> go.Figure:
    """
    [GRÁFICO 4 - DESTAQUES DE EXTREMOS: TOP 5 MELHORES VS BOTTOM 5 GARGALOS]
    Compara os 5 melhores cenários com menor taxa de abandono (evasão zero/quase zero)
    com os 5 maiores gargalos educacionais do país (altas taxas de abandono).
    Cada cenário identifica: Região + Rede de Ensino + Localização (Rural/Urbana).
    
    Insight Educacional:
    Direciona os recursos públicos exatamente onde a evasão escolar é alarmante,
    ao mesmo tempo em que identifica as redes de excelência para replicação de boas práticas.
    """
    df_filtrado = df[
        (df['ano'] == ano_referencia) &
        (df['rede'] != 'Total') &
        (df['localizacao'] != 'Total') &
        (df['taxa_abandono_em'].notna())
    ].copy()

    df_filtrado['cenario'] = (
        df_filtrado['regiao'] + " | Rede " +
        df_filtrado['rede'] + " (" + df_filtrado['localizacao'] + ")"
    )

    top_melhores = df_filtrado.nsmallest(n_extremos, 'taxa_abandono_em').copy()
    top_melhores['Classificação'] = f"Top {n_extremos} Menor Abandono (Excelência)"

    bottom_piores = df_filtrado.nlargest(n_extremos, 'taxa_abandono_em').copy()
    bottom_piores['Classificação'] = f"Bottom {n_extremos} Maior Abandono (Gargalo Crítico)"

    df_extremos = pd.concat([bottom_piores, top_melhores]).sort_values(by='taxa_abandono_em', ascending=True)

    fig = px.bar(
        df_extremos,
        x='taxa_abandono_em',
        y='cenario',
        color='Classificação',
        orientation='h',
        text=df_extremos['taxa_abandono_em'].apply(lambda x: f"{x:.1f}%"),
        color_discrete_map={
            f"Top {n_extremos} Menor Abandono (Excelência)": "#2E7D32",       # Verde
            f"Bottom {n_extremos} Maior Abandono (Gargalo Crítico)": "#C62828" # Vermelho
        },
        template=TEMPLATE_PLOTLY,
        title=f"<b>Destaques de Extremos: Melhores Práticas vs Gargalos Críticos de Evasão Escolar ({ano_referencia})</b><br>"
              f"<span style='font-size:13px; color:#555;'>Ensino Médio: Identificação dos polos com menor vs maior taxa de abandono por Região, Rede e Zona</span>"
    )

    fig.update_traces(
        textposition='outside',
        textfont=dict(size=12, family='Segoe UI, Arial'),
        hovertemplate=(
            "<b>Cenário Específico:</b> %{y}<br>"
            "<b>Taxa de Abandono Escolar:</b> %{x:.2f}%<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="<b>Taxa de Abandono Escolar (%)</b>",
            ticksuffix="%",
            range=[0, max(df_extremos['taxa_abandono_em']) * 1.15],
            gridcolor="#E0E0E0"
        ),
        yaxis=dict(title="<b>Segmento Educacional Analisado</b>"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None
        ),
        height=520,
        margin=dict(l=220, r=50, t=90, b=60)
    )

    return fig


def plot_disparidade_publica_privada(df: pd.DataFrame, ano_referencia: int = 2024) -> go.Figure:
    """
    [GRÁFICO 5 - O ABISMO EDUCACIONAL: REDE PÚBLICA VS REDE PRIVADA]
    Compara lado a lado o desempenho de Aprovação no Ensino Médio entre
    as redes Pública e Privada em cada macrorregião.
    
    Insight Educacional:
    Mede com precisão a equidade educacional: onde a distância entre o ensino público
    e privado é mais estreita e onde o fosso de oportunidades é mais profundo.
    """
    df_comp = df[
        (df['ano'] == ano_referencia) &
        (df['localizacao'] == 'Total') &
        (df['rede'].isin(['Publica', 'Privada']))
    ].copy()

    df_comp = df_comp.sort_values(by=['regiao', 'rede'])

    fig = px.bar(
        df_comp,
        x='regiao',
        y='taxa_aprovacao_em',
        color='rede',
        barmode='group',
        text=df_comp['taxa_aprovacao_em'].apply(lambda x: f"{x:.1f}%"),
        color_discrete_map={'Publica': '#1976D2', 'Privada': '#388E3C'},
        template=TEMPLATE_PLOTLY,
        title=f"<b>Equidade de Ensino: Comparativo Rede Pública vs Rede Privada ({ano_referencia})</b><br>"
              f"<span style='font-size:13px; color:#555;'>Taxa de Aprovação no Ensino Médio segundo a dependência administrativa</span>"
    )

    fig.update_traces(
        textposition='outside',
        textfont=dict(size=12, family='Segoe UI, Arial'),
        hovertemplate=(
            "<b>Região:</b> %{x}<br>"
            "<b>Rede de Ensino:</b> %{legendgroup}<br>"
            "<b>Taxa de Aprovação:</b> %{y:.2f}%<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis=dict(title="<b>Macrorregião Brasileira</b>"),
        yaxis=dict(
            title="<b>Taxa de Aprovação (%)</b>",
            ticksuffix="%",
            range=[75, 103],
            gridcolor="#E0E0E0"
        ),
        legend=dict(
            title="<b>Dependência Administrativa</b>",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=480,
        margin=dict(l=80, r=40, t=90, b=60)
    )

    return fig


def plot_correlacao_docentes_aprovacao(df: pd.DataFrame, ano_referencia: int = 2024) -> go.Figure:
    """
    [GRÁFICO 6 - QUALIDADE ESTRUTURAL: FORMAÇÃO DOCENTE VS SUCESSO DO ALUNO]
    Gráfico de Dispersão (Scatter Plot) interativo correlacionando o percentual de docentes
    com curso superior (dsu_em) e a Taxa de Aprovação (taxa_aprovacao_em).
    O tamanho das bolhas reflete a Média de Alunos por Turma (atu_em).
    
    Insight Educacional:
    Avalia a hipótese pedagógica central: a maior qualificação de professores se traduz
    diretamente em maior retenção e aprovação estudantil nas diferentes regiões?
    """
    df_scatter = df[
        (df['ano'] == ano_referencia) &
        (df['rede'] != 'Total') &
        (df['localizacao'] != 'Total') &
        (df['dsu_em'].notna()) &
        (df['taxa_aprovacao_em'].notna())
    ].copy()

    df_scatter['tamanho_turma'] = df_scatter['atu_em'].fillna(25).clip(lower=10, upper=40)

    fig = px.scatter(
        df_scatter,
        x='dsu_em',
        y='taxa_aprovacao_em',
        color='regiao',
        color_discrete_map=PALETA_CORES,
        size='tamanho_turma',
        hover_data=['rede', 'localizacao', 'atu_em'],
        template=TEMPLATE_PLOTLY,
        title=f"<b>Impacto Pedagógico: Formação Docente Superior vs Taxa de Aprovação ({ano_referencia})</b><br>"
              f"<span style='font-size:13px; color:#555;'>O diâmetro dos círculos reflete o tamanho médio das turmas (Alunos por Sala)</span>"
    )

    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1, color='#2c3e50')),
        hovertemplate=(
            "<b>Macrorregião:</b> %{fullData.name}<br>"
            "<b>Docentes c/ Ensino Superior:</b> %{x:.1f}%<br>"
            "<b>Taxa de Aprovação:</b> %{y:.1f}%<br>"
            "<b>Tamanho Médio da Turma:</b> %{marker.size:.1f} alunos<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="<b>Percentual de Docentes com Formação Superior (DSU) (%)</b>",
            ticksuffix="%",
            gridcolor="#E0E0E0"
        ),
        yaxis=dict(
            title="<b>Taxa de Aprovação no Ensino Médio (%)</b>",
            ticksuffix="%",
            gridcolor="#E0E0E0"
        ),
        legend=dict(title="<b>Macrorregião</b>"),
        height=520,
        margin=dict(l=80, r=40, t=80, b=60)
    )

    return fig


def plot_evolucao_historica_temporal(df: pd.DataFrame) -> go.Figure:
    """
    [GRÁFICO 7 - TRAJETÓRIA HISTÓRICA: SÉRIE TEMPORAL 2013 A 2024]
    Evolução longitudinal das Taxas de Aprovação no Ensino Médio
    consolidada por Macrorregião ao longo dos últimos anos.
    
    Insight Educacional:
    Exibe a tendência histórica, os avanços educacionais alcançados na década
    e o impacto das políticas públicas pós-pandemia.
    """
    df_tempo = df[
        (df['localizacao'] == 'Total') &
        (df['rede'] == 'Total') &
        (df['ano'] >= 2013) &
        (df['taxa_aprovacao_em'].notna())
    ].sort_values(by=['regiao', 'ano']).copy()

    fig = px.line(
        df_tempo,
        x='ano',
        y='taxa_aprovacao_em',
        color='regiao',
        color_discrete_map=PALETA_CORES,
        markers=True,
        template=TEMPLATE_PLOTLY,
        title="<b>Trajetória Histórica: Evolução da Taxa de Aprovação no Ensino Médio (2013 a 2024)</b><br>"
              f"<span style='font-size:13px; color:#555;'>Acompanhamento longitudinal por Macrorregião (Rede e Localização Totais)</span>"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate=(
            "<b>Ano Letivo:</b> %{x}<br>"
            "<b>Região:</b> %{fullData.name}<br>"
            "<b>Taxa de Aprovação:</b> %{y:.2f}%<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="<b>Ano Letivo</b>",
            tickmode='linear',
            tick0=2013,
            dtick=1,
            gridcolor="#E0E0E0"
        ),
        yaxis=dict(
            title="<b>Taxa de Aprovação (%)</b>",
            ticksuffix="%",
            gridcolor="#E0E0E0"
        ),
        legend=dict(
            title="<b>Macrorregião</b>",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=480,
        margin=dict(l=80, r=40, t=90, b=60)
    )

    return fig


# ======================================================================================
# 3. GERAÇÃO DO DASHBOARD HTML EXECUTIVO INTERATIVO
# ======================================================================================

def compilar_dashboard_html(
    figuras: dict,
    estatisticas_kpi: dict,
    caminho_saida: str = "relatorio_eda_educacional.html"
) -> str:
    """
    Gera um relatório executivo web responsivo e autocontido com design profissional,
    cartões de métricas (KPIs), explicações didáticas e gráficos Plotly 100% interativos.
    """
    html_figuras = {}
    for chave, fig in figuras.items():
        html_figuras[chave] = fig.to_html(full_html=False, include_plotlyjs=False)

    template_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Executivo: Indicadores Educacionais por Região (INEP)</title>
    <!-- Plotly Core JS -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        :root {{
            --primary: #1A365D;
            --secondary: #2B6CB0;
            --accent: #319795;
            --bg-light: #F7FAFC;
            --text-dark: #2D3748;
            --card-bg: #FFFFFF;
            --border-color: #E2E8F0;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background-color: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
            padding-bottom: 60px;
        }}
        header {{
            background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%);
            color: #FFFFFF;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        header h1 {{
            font-size: 2.2rem;
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        header p {{
            font-size: 1.1rem;
            opacity: 0.92;
            max-width: 850px;
            margin: 0 auto;
        }}
        .container {{
            max-width: 1200px;
            margin: -25px auto 0;
            padding: 0 20px;
        }}
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }}
        .kpi-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid var(--border-color);
            border-top: 5px solid var(--secondary);
            text-align: center;
            transition: transform 0.2s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
        }}
        .kpi-label {{
            font-size: 0.85rem;
            text-transform: uppercase;
            font-weight: 600;
            color: #718096;
            letter-spacing: 0.5px;
        }}
        .kpi-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--primary);
            margin: 8px 0;
        }}
        .kpi-subtext {{
            font-size: 0.85rem;
            color: #4A5568;
        }}
        /* Section Containers */
        .section-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 28px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid var(--border-color);
        }}
        .section-header {{
            margin-bottom: 18px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 12px;
        }}
        .section-header h2 {{
            font-size: 1.35rem;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-desc {{
            font-size: 0.95rem;
            color: #4A5568;
            margin-top: 6px;
        }}
        .chart-box {{
            width: 100%;
            overflow-x: auto;
        }}
        footer {{
            text-align: center;
            margin-top: 50px;
            font-size: 0.85rem;
            color: #718096;
        }}
    </style>
</head>
<body>

    <header>
        <h1>📊 Painel de Análise Exploratória: Indicadores Educacionais por Região</h1>
        <p>Diagnóstico Estratégico sobre Desempenho Escolar, Desigualdades Regionais e Fatores Estruturais no Brasil (Fonte: INEP / MEC)</p>
    </header>

    <main class="container">
        
        <!-- Cartões de Métricas Estratégicas (KPIs) -->
        <section class="kpi-grid">
            <div class="kpi-card" style="border-top-color: #319795;">
                <div class="kpi-label">Taxa Média de Aprovação</div>
                <div class="kpi-value">{estatisticas_kpi.get('taxa_aprovacao_media', 0):.1f}%</div>
                <div class="kpi-subtext">Ensino Médio Consolidado ({estatisticas_kpi.get('ano_ref', 2024)})</div>
            </div>
            <div class="kpi-card" style="border-top-color: #E53E3E;">
                <div class="kpi-label">Taxa Média de Abandono</div>
                <div class="kpi-value">{estatisticas_kpi.get('taxa_abandono_media', 0):.1f}%</div>
                <div class="kpi-subtext">Evasão Escolar no Ensino Médio</div>
            </div>
            <div class="kpi-card" style="border-top-color: #DD6B20;">
                <div class="kpi-label">Distorção Idade-Série</div>
                <div class="kpi-value">{estatisticas_kpi.get('tdi_media', 0):.1f}%</div>
                <div class="kpi-subtext">Alunos com 2+ anos de atraso</div>
            </div>
            <div class="kpi-card" style="border-top-color: #3182CE;">
                <div class="kpi-label">Docentes com Superior</div>
                <div class="kpi-value">{estatisticas_kpi.get('dsu_media', 0):.1f}%</div>
                <div class="kpi-subtext">Corpo docente qualificado (DSU)</div>
            </div>
        </section>

        <!-- Análise 1: Ranking Regional -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>🏆</span> 1. Comparativo Regional: Ranking de Aprovação Escolar</h2>
                <p class="section-desc">
                    Comparação direta entre as 5 macrorregiões brasileiras ordenada da maior para a menor taxa de aprovação.
                    A linha pontilhada vermelha demarca a média nacional consolidada.
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('ranking', '')}
            </div>
        </article>

        <!-- Análise 2: Desigualdade Intra-regional -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>⚖️</span> 2. Desigualdade Intra-Regional: Disparidade de Abandono</h2>
                <p class="section-desc">
                    Gráfico Box Plot com pontos individuais. Demonstra que médias regionais ocultam realidades díspares:
                    cada ponto representa uma combinação de rede escolar (Municipal, Estadual, Federal, Privada) e zona (Urbana e Rural).
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('desigualdade', '')}
            </div>
        </article>

        <!-- Análise 3: Visão Geográfica -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>🗺️</span> 3. Panorama Geográfico Interativo do Brasil</h2>
                <p class="section-desc">
                    Distribuição espacial dos indicadores nas macrorregiões. O diâmetro e a intensidade térmica refletem a taxa de aprovação.
                    Passe o cursor sobre os pontos para acessar o diagnóstico completo de cada macrorregião.
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('mapa', '')}
            </div>
        </article>

        <!-- Análise 4: Destaques de Extremos -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>🚨</span> 4. Polos de Extremos: Melhores Cenários vs Gargalos Críticos</h2>
                <p class="section-desc">
                    Destaque dos 5 polos de excelência com as menores taxas de abandono escolar frente aos 5 gargalos mais críticos
                    de evasão escolar no país, permitindo alocação focalizada de programas de permanência estudantil.
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('extremos', '')}
            </div>
        </article>

        <!-- Análise 5: Abismo Público vs Privado -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>🏫</span> 5. O Fosso Educacional: Rede Pública vs Rede Privada</h2>
                <p class="section-desc">
                    Avaliação direta da equidade educacional: compara o desempenho das escolas públicas estaduais/municipais
                    frente às instituições privadas em cada macrorregião brasileira.
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('publica_privada', '')}
            </div>
        </article>

        <!-- Análise 6: Fatores Pedagógicos e Formação Docente -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>🎓</span> 6. Qualidade Pedagógica: Formação Docente vs Aprovação</h2>
                <p class="section-desc">
                    Relação entre o percentual de professores com ensino superior e os resultados de aprovação dos alunos.
                    O tamanho de cada círculo representa a média de alunos atendidos por sala de aula.
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('docentes', '')}
            </div>
        </article>

        <!-- Análise 7: Trajetória Histórica -->
        <article class="section-card">
            <div class="section-header">
                <h2><span>📈</span> 7. Trajetória Histórica e Séries Temporais (2013 - 2024)</h2>
                <p class="section-desc">
                    Evolução longitudinal da taxa de aprovação escolar na última década. Mostra a capacidade de recuperação
                    e a estabilização dos fluxos escolares em cada macrorregião brasileira.
                </p>
            </div>
            <div class="chart-box">
                {html_figuras.get('historico', '')}
            </div>
        </article>

        <footer>
            <p>Relatório gerado automaticamente por Análise Exploratória de Dados em Python (Plotly & Pandas).</p>
            <p>Fonte primária: Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP / MEC).</p>
        </footer>

    </main>

</body>
</html>
"""

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write(template_html)

    return os.path.abspath(caminho_saida)


# ======================================================================================
# 4. EXECUÇÃO PRINCIPAL DO PIPELINE DE CIÊNCIA DE DADOS
# ======================================================================================

def executar_eda(
    caminho_csv: str = "br_inep_indicadores_educacionais_regiao.csv",
    ano_analise: int = 2024,
    gerar_relatorio_web: bool = True,
    exibir_navegador: bool = False
):
    """
    Função orquestradora da Análise Exploratória de Dados (EDA).
    """
    print("\n" + "="*70)
    print(" INICIANDO ANÁLISE EXPLORATÓRIA DE DADOS EDUCACIONAIS")
    print("="*70)

    # 1. Carregamento e Tratamento Seguro
    df = carregar_e_tratar_dados(caminho_csv)

    if ano_analise not in df['ano'].values:
        ano_analise = df['ano'].max()
        print(f" Ano de referência ajustado automaticamente para {ano_analise} (mais recente).")

    # 2. Cálculo dos Indicadores-Chave (KPIs)
    df_kpi = df[
        (df['ano'] == ano_analise) &
        (df['localizacao'] == 'Total') &
        (df['rede'] == 'Total')
    ]

    estatisticas_kpi = {
        'ano_ref': ano_analise,
        'taxa_aprovacao_media': float(df_kpi['taxa_aprovacao_em'].mean()) if 'taxa_aprovacao_em' in df_kpi else 0.0,
        'taxa_abandono_media': float(df_kpi['taxa_abandono_em'].mean()) if 'taxa_abandono_em' in df_kpi else 0.0,
        'tdi_media': float(df_kpi['tdi_em'].mean()) if 'tdi_em' in df_kpi else 0.0,
        'dsu_media': float(df_kpi['dsu_em'].mean()) if 'dsu_em' in df_kpi else 0.0
    }

    print("\n--- PRINCIPAIS MÉTRICAS NACIONAIS (ENSINO MÉDIO 2024) ---")
    print(f"• Taxa Média de Aprovação: {estatisticas_kpi['taxa_aprovacao_media']:.2f}%")
    print(f"• Taxa Média de Abandono Escolar: {estatisticas_kpi['taxa_abandono_media']:.2f}%")
    print(f"• Taxa de Distorção Idade-Série: {estatisticas_kpi['tdi_media']:.2f}%")
    print(f"• Docentes com Ensino Superior: {estatisticas_kpi['dsu_media']:.2f}%")

    # 3. Construção dos Gráficos Interativos com Plotly
    print("\n Construindo visualizações interativas com Plotly...")
    figuras = {}

    print("  [1/7] Gerando Comparativo Regional de Aprovação (Barras Horizontais)...")
    figuras['ranking'] = plot_ranking_regional_aprovacao(df, ano_referencia=ano_analise)

    print("  [2/7] Gerando Desigualdade Intra-Regional (Box Plot)...")
    figuras['desigualdade'] = plot_desigualdade_regional_boxplot(df, ano_referencia=ano_analise)

    print("  [3/7] Gerando Panorama Geográfico Interativo (Mapa)...")
    figuras['mapa'] = plot_mapa_interativo_brasil(df, ano_referencia=ano_analise)

    print("  [4/7] Gerando Destaques de Extremos (Top 5 Melhores vs Bottom 5 Gargalos)...")
    figuras['extremos'] = plot_extremos_top_bottom(df, ano_referencia=ano_analise, n_extremos=5)

    print("  [5/7] Gerando Comparativo Rede Pública vs Rede Privada...")
    figuras['publica_privada'] = plot_disparidade_publica_privada(df, ano_referencia=ano_analise)

    print("  [6/7] Gerando Correlação Docência vs Desempenho (Scatter Plot)...")
    figuras['docentes'] = plot_correlacao_docentes_aprovacao(df, ano_referencia=ano_analise)

    print("  [7/7] Gerando Trajetória Histórica (Linha do Tempo 2013-2024)...")
    figuras['historico'] = plot_evolucao_historica_temporal(df)

    # 4. Geração do Relatório Web Executivo
    if gerar_relatorio_web:
        caminho_relatorio = compilar_dashboard_html(figuras, estatisticas_kpi)
        print(f"\n Relatório Executivo Interativo gerado com sucesso!")
        print(f" Arquivo disponível em: {caminho_relatorio}")

        if exibir_navegador:
            webbrowser.open(f"file:///{caminho_relatorio}")

    print("\n" + "="*70)
    print(" ANÁLISE EXPLORATÓRIA CONCLUÍDA COM SUCESSO!")
    print("="*70)

    return df, figuras


if __name__ == '__main__':
    ARQUIVO_PADRAO = "br_inep_indicadores_educacionais_regiao.csv"
    df_resultado, figs = executar_eda(
        caminho_csv=ARQUIVO_PADRAO,
        ano_analise=2024,
        gerar_relatorio_web=True,
        exibir_navegador=False
    )
