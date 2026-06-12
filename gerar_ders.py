"""
Gerador do DERS (Documento de Especificação de Requisitos de Software)
PitchIQ — Plataforma Multi-Agente de Validação Estratégica de Negócios
Disciplina: ESW308 — Tópicos Especiais em Software
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date

# ─── Constantes ──────────────────────────────────────────────────────────────
OUTPUT = r"C:\ESW308  TES  174\projetoFinal\DERS_PitchIQ.pdf"
TODAY  = date.today().strftime("%d/%m/%Y")

# Paleta de cores
INDIGO  = colors.HexColor("#6366f1")
PURPLE  = colors.HexColor("#8b5cf6")
DARK    = colors.HexColor("#0f172a")
GRAY    = colors.HexColor("#64748b")
LIGHT   = colors.HexColor("#f1f5f9")
WHITE   = colors.white
RED     = colors.HexColor("#ef4444")
GREEN   = colors.HexColor("#22c55e")
YELLOW  = colors.HexColor("#f59e0b")

# ─── Estilos ─────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

S_TITLE   = style("s_title",   fontSize=28, textColor=WHITE,  alignment=TA_CENTER, leading=34, fontName="Helvetica-Bold")
S_SUBTITLE= style("s_sub",     fontSize=14, textColor=colors.HexColor("#c7d2fe"), alignment=TA_CENTER, leading=20, fontName="Helvetica")
S_COVER   = style("s_cover",   fontSize=11, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER, leading=16, fontName="Helvetica")
S_H1      = style("s_h1",      fontSize=16, textColor=DARK,   spaceBefore=18, spaceAfter=8,  fontName="Helvetica-Bold", borderPad=4)
S_H2      = style("s_h2",      fontSize=13, textColor=INDIGO, spaceBefore=14, spaceAfter=6,  fontName="Helvetica-Bold")
S_H3      = style("s_h3",      fontSize=11, textColor=DARK,   spaceBefore=10, spaceAfter=4,  fontName="Helvetica-Bold")
S_BODY    = style("s_body",    fontSize=10, textColor=DARK,   leading=15, spaceAfter=6,  fontName="Helvetica", alignment=TA_JUSTIFY)
S_BULLET  = style("s_bullet",  fontSize=10, textColor=DARK,   leading=15, spaceAfter=3,  fontName="Helvetica", leftIndent=16, bulletIndent=6)
S_CODE    = style("s_code",    fontSize=9,  textColor=DARK,   leading=13, spaceAfter=4,  fontName="Courier", backColor=LIGHT, leftIndent=12, rightIndent=12, borderPad=6)
S_CAPTION = style("s_caption", fontSize=8,  textColor=GRAY,   alignment=TA_CENTER, fontName="Helvetica-Oblique")
S_TOC1    = style("s_toc1",    fontSize=11, textColor=DARK,   fontName="Helvetica-Bold", spaceBefore=4)
S_TOC2    = style("s_toc2",    fontSize=10, textColor=GRAY,   fontName="Helvetica",      leftIndent=16, spaceBefore=2)
S_VERSION = style("s_ver",     fontSize=9,  textColor=GRAY,   fontName="Helvetica")

def sp(h=6):
    return Spacer(1, h)

def hr(color=INDIGO, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=8, spaceBefore=4)

def h1(text):
    return [sp(12), hr(INDIGO, 2), Paragraph(text, S_H1), hr(colors.HexColor("#e2e8f0"), 0.5)]

def h2(text):
    return [sp(8), Paragraph(text, S_H2)]

def h3(text):
    return [sp(6), Paragraph(text, S_H3)]

def body(text):
    return Paragraph(text, S_BODY)

def bullet(text):
    return Paragraph(f"• {text}", S_BULLET)

def req_table(rows, header_color=INDIGO):
    col_widths = [2*cm, 3.5*cm, 8*cm, 2.8*cm]
    t = Table([["ID", "Nome", "Descrição", "Prioridade"]] + rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  header_color),
        ("TEXTCOLOR",    (0,0), (-1,0),  WHITE),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  9),
        ("ALIGN",        (0,0), (-1,0),  "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LIGHT]),
        ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",     (0,1), (-1,-1), 9),
        ("ALIGN",        (0,1), (1,-1),  "CENTER"),
        ("ALIGN",        (3,1), (3,-1),  "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("WORDWRAP",     (2,1), (2,-1),  True),
    ]))
    return t

def priority_badge(p):
    colors_map = {"Alta": RED, "Média": YELLOW, "Baixa": GREEN}
    c = colors_map.get(p, GRAY)
    return Paragraph(f'<font color="#{c.hexval()[1:]}"><b>{p}</b></font>', style("pb", fontSize=9, fontName="Helvetica-Bold", alignment=TA_CENTER))

def uc_table(rows):
    col_widths = [2*cm, 3*cm, 8.5*cm, 2.8*cm]
    t = Table([["ID", "Caso de Uso", "Descrição", "Atores"]] + rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  PURPLE),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("ALIGN",         (0,0), (-1,0),  "CENTER"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("ALIGN",         (0,1), (1,-1),  "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ]))
    return t

# ─── Número de página ─────────────────────────────────────────────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawRightString(A4[0] - 2*cm, 1.2*cm, f"Página {doc.page}")
        canvas.drawString(2*cm, 1.2*cm, "PitchIQ — DERS v1.0")
        canvas.setStrokeColor(colors.HexColor("#e2e8f0"))
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.5*cm, A4[0]-2*cm, 1.5*cm)
    canvas.restoreState()

# ─── Capa ─────────────────────────────────────────────────────────────────────
def cover_page(story):
    from reportlab.platypus import Frame
    story.append(Spacer(1, 3*cm))

    # Fundo visual simulado com uma tabela colorida
    cover_data = [[""]]
    cover_table = Table(cover_data, colWidths=[16.5*cm], rowHeights=[0.3*cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), INDIGO),
        ("LINEBELOW",  (0,0), (-1,-1), 3, PURPLE),
    ]))
    story.append(cover_table)
    story.append(sp(24))

    story.append(Paragraph("PitchIQ", S_TITLE))
    story.append(sp(8))
    story.append(Paragraph(
        "Plataforma Multi-Agente de Validação Estratégica de Negócios",
        S_SUBTITLE
    ))
    story.append(sp(6))
    story.append(Paragraph(
        "Documento de Especificação de Requisitos de Software — DERS",
        S_SUBTITLE
    ))
    story.append(sp(3*cm))

    info = [
        ["Disciplina",  "ESW308 — Tópicos Especiais em Software"],
        ["Aluno",       "Samuel Guimarães Lopes"],
        ["Versão",      "1.0"],
        ["Data",        TODAY],
        ["Status",      "Em desenvolvimento"],
    ]
    info_table = Table(info, colWidths=[4*cm, 11*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",     (1,0), (1,-1),  "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("TEXTCOLOR",    (0,0), (0,-1),  INDIGO),
        ("TEXTCOLOR",    (1,0), (1,-1),  DARK),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LINEBELOW",    (0,0), (-1,-2), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(info_table)
    story.append(PageBreak())

# ─── Histórico ────────────────────────────────────────────────────────────────
def historico(story):
    story += h1("Histórico de Revisões")
    rev = [
        ["Versão", "Data",    "Autor",                  "Descrição"],
        ["1.0",    TODAY,     "Samuel Guimarães Lopes",  "Versão inicial do documento"],
    ]
    t = Table(rev, colWidths=[2*cm, 3*cm, 6*cm, 5.3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(t)

# ─── 1. Introdução ────────────────────────────────────────────────────────────
def introducao(story):
    story += h1("1. Introdução")

    story += h2("1.1 Objetivo do Documento")
    story.append(body(
        "Este documento descreve os requisitos de software do sistema <b>PitchIQ</b>, "
        "uma plataforma multi-agente de validação estratégica de ideias de negócio. "
        "O DERS apresenta os requisitos funcionais, não-funcionais, restrições e casos de uso "
        "que guiarão o desenvolvimento e avaliação do produto ao longo do semestre."
    ))

    story += h2("1.2 Escopo do Sistema")
    story.append(body(
        "O PitchIQ é uma aplicação web que recebe uma descrição textual de uma ideia de negócio "
        "e aciona autonomamente uma equipe de <b>9 agentes de inteligência artificial</b> para "
        "pesquisar, debater e sintetizar uma análise estratégica completa. O sistema produz "
        "relatórios executivos com análise de mercado, mapeamento de concorrentes, perfil de "
        "cliente, debate adversarial (Advocate vs. Devil's Advocate) e score de viabilidade."
    ))
    story.append(body(
        "O sistema <b>NÃO</b> se propõe a: fornecer aconselhamento financeiro formal, "
        "garantir precisão absoluta dos dados de mercado, substituir due diligence "
        "profissional ou gerenciar implementação de negócios."
    ))

    story += h2("1.3 Definições, Acrônimos e Abreviações")
    defs = [
        ["Termo",            "Definição"],
        ["Agente de IA",     "Sistema autônomo baseado em LLM que executa tarefas com uso de ferramentas"],
        ["LLM",              "Large Language Model — modelo de linguagem de grande escala (ex: Claude)"],
        ["Tool Use",         "Capacidade do agente de invocar ferramentas externas (busca web, APIs)"],
        ["SSE",              "Server-Sent Events — protocolo de streaming do servidor para o cliente"],
        ["ICP",              "Ideal Customer Profile — perfil do cliente ideal"],
        ["TAM/SAM/SOM",      "Total/Serviceable/Obtainable Addressable Market"],
        ["SWOT",             "Strengths, Weaknesses, Opportunities, Threats"],
        ["Debate Mode",      "Módulo com Advocate, Devil's Advocate e Mediator Agents"],
        ["Pipeline",         "Sequência orquestrada de execução dos agentes"],
        ["FastAPI",          "Framework Python para construção de APIs assíncronas"],
        ["Next.js",          "Framework React para aplicações web com renderização híbrida"],
        ["Tavily",           "API de busca web otimizada para agentes de IA"],
    ]
    t = Table(defs, colWidths=[4*cm, 12.3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("TEXTCOLOR",     (0,1), (0,-1),  INDIGO),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)

    story += h2("1.4 Referências")
    refs = [
        "Anthropic API Documentation — https://docs.anthropic.com",
        "Tavily Search API — https://docs.tavily.com",
        "FastAPI Documentation — https://fastapi.tiangolo.com",
        "Next.js 14 Documentation — https://nextjs.org/docs",
        "IEEE 830-1998 — Software Requirements Specifications",
    ]
    for r in refs:
        story.append(bullet(r))

# ─── 2. Descrição Geral ───────────────────────────────────────────────────────
def descricao_geral(story):
    story += h1("2. Descrição Geral do Sistema")

    story += h2("2.1 Perspectiva do Produto")
    story.append(body(
        "O PitchIQ é um produto independente desenvolvido como projeto final da disciplina ESW308. "
        "O sistema integra a API da Anthropic (Claude Sonnet) como motor de raciocínio dos agentes "
        "e a API Tavily para busca web em tempo real. A arquitetura segue o padrão cliente-servidor "
        "com frontend em Next.js e backend em Python/FastAPI."
    ))

    story += h2("2.2 Arquitetura Multi-Agente")
    story.append(body(
        "O núcleo do sistema é composto por 9 agentes especializados organizados em 3 fases:"
    ))

    arch = [
        ["Fase",  "Agente",             "Responsabilidade"],
        ["1 — Pesquisa\n(paralela)",
         "Market Agent\nCompetitor Agent\nAudience Agent\nRisk Agent",
         "Pesquisa mercado (TAM/SAM/SOM)\nMapeia concorrentes e gaps\nDefine ICP e canais\nAvalia riscos regulatórios e de execução"],
        ["2 — Debate",
         "Advocate Agent\nDevil's Advocate\nMediator Agent",
         "Defende a ideia com dados\nDesafia premissas e riscos\nArbitragem e veredicto balanceado"],
        ["3 — Síntese",
         "Synthesis Agent\nQ&A Agent",
         "Consolida relatório executivo + score\nResponde perguntas sobre o relatório"],
    ]
    t = Table(arch, colWidths=[2.8*cm, 4*cm, 9.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1),  INDIGO),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(t)

    story += h2("2.3 Funções Principais do Produto")
    funcoes = [
        "Receber descrição textual de uma ideia de negócio em linguagem natural",
        "Orquestrar pipeline de 9 agentes de IA em fases sequenciais e paralelas",
        "Realizar busca web em tempo real via Tavily para embasar a análise",
        "Executar debate adversarial automatizado (Advocate vs. Devil's Advocate)",
        "Gerar relatório executivo estruturado com 9 seções e score de viabilidade",
        "Exibir progresso dos agentes em tempo real via Server-Sent Events (SSE)",
        "Permitir consultas (Q&A) ao relatório gerado via agente especializado",
    ]
    for f in funcoes:
        story.append(bullet(f))

    story += h2("2.4 Características dos Usuários")
    usuarios = [
        ["Perfil",            "Empreendedores, estudantes, profissionais de produto e estratégia"],
        ["Conhecimento técnico", "Nenhum — interface intuitiva sem jargão técnico"],
        ["Frequência de uso",  "Pontual (1-5 análises por sessão)"],
        ["Dispositivo",        "Desktop/notebook (interface otimizada para telas >= 1024px)"],
    ]
    t = Table(usuarios, colWidths=[4.5*cm, 11.8*cm])
    t.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("TEXTCOLOR",    (0,0), (0,-1),  INDIGO),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, LIGHT]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    story += h2("2.5 Restrições Gerais")
    restricoes = [
        "Requer conexão com a internet para acesso às APIs externas (Anthropic + Tavily)",
        "Chaves de API válidas e com crédito disponível são obrigatórias para funcionamento",
        "O tempo de análise varia entre 1 e 5 minutos dependendo da complexidade da ideia",
        "A sessão de análise é mantida em memória (não persistida entre reinicializações do servidor)",
        "Limite de taxa da API Anthropic: 30.000 tokens/minuto no plano inicial",
    ]
    for r in restricoes:
        story.append(bullet(r))

    story += h2("2.6 Suposições e Dependências")
    story.append(body(
        "O sistema depende de: (a) disponibilidade das APIs externas (Anthropic e Tavily), "
        "(b) ambiente Python 3.11+ com dependências instaladas, (c) ambiente Node.js 18+ "
        "para o frontend. Assume-se que o usuário possui navegador moderno com suporte a "
        "Server-Sent Events."
    ))

# ─── 3. Requisitos Funcionais ─────────────────────────────────────────────────
def req_funcionais(story):
    story += h1("3. Requisitos Funcionais")
    story.append(body(
        "Os requisitos funcionais descrevem o comportamento esperado do sistema. "
        "Prioridades: <b>Alta</b> = essencial para o MVP, <b>Média</b> = importante mas não bloqueante, "
        "<b>Baixa</b> = desejável para versões futuras."
    ))

    story += h2("3.1 Entrada e Validação da Ideia")
    rows = [
        ["RF001", "Entrada de ideia",      "O sistema deve aceitar ideias de negócio em texto livre (mínimo 10, máximo 1000 caracteres), em português ou inglês.",                                           "Alta"],
        ["RF002", "Validação de entrada",  "O sistema deve rejeitar entradas vazias ou muito curtas com mensagem de erro explicativa.",                                                                     "Alta"],
        ["RF003", "Exemplos pré-carregados","O sistema deve oferecer ao menos 4 exemplos de ideias clicáveis que preenchem o campo automaticamente.",                                                       "Média"],
    ]
    story.append(req_table(rows))

    story += h2("3.2 Orquestração do Pipeline Multi-Agente")
    rows = [
        ["RF004", "Disparo do pipeline",   "Ao submeter uma ideia, o sistema deve iniciar automaticamente o pipeline de 9 agentes sem intervenção do usuário.",                                            "Alta"],
        ["RF005", "Execução paralela",     "Os 4 agentes da Fase 1 (Market, Competitor, Audience, Risk) devem ser executados em paralelo para reduzir o tempo total de análise.",                          "Alta"],
        ["RF006", "Execução sequencial",   "A Fase 2 (Debate) deve iniciar somente após a conclusão de todos os agentes da Fase 1. A Fase 3 inicia após o término da Fase 2.",                            "Alta"],
        ["RF007", "Identificação de sessão","O sistema deve gerar e retornar um ID único de sessão para cada análise, permitindo recuperação posterior dos resultados.",                                    "Alta"],
        ["RF008", "Retry automático",      "O sistema deve realizar até 5 tentativas com backoff exponencial em caso de erros de rate limit, timeout ou conexão nas chamadas à API.",                      "Alta"],
    ]
    story.append(req_table(rows))

    story += h2("3.3 Agentes de Pesquisa (Fase 1)")
    rows = [
        ["RF009", "Market Agent",          "Deve realizar ao menos 2 buscas web e retornar análise de TAM/SAM/SOM, tendências do setor e contexto do mercado brasileiro.",                                "Alta"],
        ["RF010", "Competitor Agent",      "Deve identificar ao menos 3 concorrentes reais (nacionais ou internacionais), com forças, fraquezas e gaps de mercado.",                                       "Alta"],
        ["RF011", "Audience Agent",        "Deve definir o ICP com perfil demográfico, dores, comportamento de compra, canais de aquisição e disposição a pagar.",                                         "Alta"],
        ["RF012", "Risk Agent",            "Deve mapear riscos regulatórios, de mercado e de execução, cada um com avaliação de probabilidade e impacto.",                                                 "Alta"],
        ["RF013", "Busca web real",        "Os agentes de pesquisa devem usar a ferramenta Tavily para buscar informações atualizadas na internet (não apenas conhecimento do modelo).",                   "Alta"],
    ]
    story.append(req_table(rows))

    story += h2("3.4 Debate Adversarial (Fase 2)")
    rows = [
        ["RF014", "Advocate Agent",        "Deve apresentar os argumentos mais fortes a favor da ideia, usando dados da Fase 1, em formato narrativo persuasivo de até 400 palavras.",                     "Alta"],
        ["RF015", "Devil's Advocate",      "Deve contra-argumentar diretamente os pontos do Advocate, identificando premissas não validadas, riscos ignorados e falhas de timing.",                        "Alta"],
        ["RF016", "Mediator Agent",        "Deve mediar o debate, reconhecer pontos válidos de ambos os lados, definir as 3 principais hipóteses a validar e emitir um veredicto final.",                 "Alta"],
        ["RF017", "Contexto compartilhado","O Devil's Advocate deve receber como input o argumento do Advocate. O Mediator deve receber ambos os argumentos.",                                             "Alta"],
    ]
    story.append(req_table(rows))

    story += h2("3.5 Síntese e Relatório (Fase 3)")
    rows = [
        ["RF018", "Relatório executivo",   "O Synthesis Agent deve consolidar todas as análises em relatório com: Resumo Executivo, Mercado, Concorrentes, ICP, Debate, SWOT, GTM, Score e Riscos.",       "Alta"],
        ["RF019", "Score de viabilidade",  "O relatório deve incluir uma nota global de 0-100 e scores individuais para: mercado, competição, execução, timing, monetização e inovação.",                  "Alta"],
        ["RF020", "Score em JSON",         "O Synthesis Agent deve emitir os scores em bloco JSON padronizado ao final do relatório para consumo pelo frontend.",                                           "Alta"],
        ["RF021", "Q&A Agent",             "Após a conclusão da análise, o usuário deve poder fazer perguntas em linguagem natural e receber respostas baseadas exclusivamente no relatório gerado.",       "Alta"],
        ["RF022", "Anti-alucinação Q&A",   "O Q&A Agent deve declarar explicitamente quando uma informação não foi coberta na análise, em vez de inventar dados.",                                         "Alta"],
    ]
    story.append(req_table(rows))

    story += h2("3.6 Interface e Streaming")
    rows = [
        ["RF023", "Streaming em tempo real","O frontend deve exibir o status de cada agente (idle, running, done) em tempo real via SSE durante todo o pipeline.",                                         "Alta"],
        ["RF024", "AgentTimeline",          "A interface deve exibir uma linha do tempo visual com os 8 agentes do pipeline, indicando a fase atual e o status de cada um.",                              "Alta"],
        ["RF025", "DebateView",             "O frontend deve apresentar o debate com identidade visual distinta para cada agente (cores e rótulos diferenciados para Advocate, Devil e Mediator).",         "Alta"],
        ["RF026", "ScoreRadar",             "O frontend deve exibir os scores por dimensão em um gráfico radar interativo.",                                                                               "Média"],
        ["RF027", "Abas de resultado",      "A interface deve organizar os resultados em abas: Relatório, Debate e Score.",                                                                               "Alta"],
        ["RF028", "Cópia do relatório",     "O usuário deve poder copiar o relatório completo para a área de transferência com um clique.",                                                               "Média"],
    ]
    story.append(req_table(rows))

# ─── 4. Requisitos Não-Funcionais ─────────────────────────────────────────────
def req_nao_funcionais(story):
    story += h1("4. Requisitos Não-Funcionais")

    story += h2("4.1 Desempenho")
    rows = [
        ["RNF001", "Tempo total de análise",  "O pipeline completo (9 agentes) deve concluir em no máximo 5 minutos em condições normais de rede.",                                                       "Alta"],
        ["RNF002", "Paralelismo",             "A Fase 1 deve processar os 4 agentes simultaneamente, reduzindo o tempo em relação à execução sequencial.",                                                "Alta"],
        ["RNF003", "Latência do streaming",   "O frontend deve exibir a mudança de status de cada agente em no máximo 2 segundos após o evento ocorrer no backend.",                                      "Média"],
        ["RNF004", "Resposta do Q&A",         "O Q&A Agent deve retornar resposta em no máximo 30 segundos após a pergunta.",                                                                             "Média"],
    ]
    story.append(req_table(rows, DARK))

    story += h2("4.2 Usabilidade")
    rows = [
        ["RNF005", "Onboarding zero",         "Um usuário sem conhecimento técnico deve conseguir submeter uma ideia e interpretar o relatório sem treinamento prévio.",                                   "Alta"],
        ["RNF006", "Feedback visual",         "O sistema deve sempre informar visualmente o estado do processamento (loading, running, done, error) sem deixar o usuário sem feedback.",                   "Alta"],
        ["RNF007", "Mensagens de erro claras","Em caso de falha, o sistema deve exibir mensagem em português explicando o problema e a ação recomendada.",                                                 "Alta"],
        ["RNF008", "Responsividade",          "A interface deve ser utilizável em telas a partir de 1024px de largura.",                                                                                  "Média"],
    ]
    story.append(req_table(rows, DARK))

    story += h2("4.3 Confiabilidade")
    rows = [
        ["RNF009", "Retry automático",        "O sistema deve recuperar-se automaticamente de erros temporários de API (rate limit, timeout) sem exigir ação do usuário.",                                "Alta"],
        ["RNF010", "Isolamento de falhas",    "A falha de um agente não deve interromper os demais agentes em execução paralela.",                                                                        "Alta"],
        ["RNF011", "Disponibilidade local",   "O sistema deve funcionar no ambiente local sem dependências de infraestrutura em nuvem própria (exceto APIs externas).",                                   "Alta"],
    ]
    story.append(req_table(rows, DARK))

    story += h2("4.4 Segurança")
    rows = [
        ["RNF012", "Proteção de chaves",      "Chaves de API devem ser armazenadas em variáveis de ambiente (.env) e nunca expostas no código-fonte ou no frontend.",                                     "Alta"],
        ["RNF013", "CORS configurado",        "O backend deve aceitar requisições apenas de origens autorizadas (localhost:3000 e domínios Vercel configurados).",                                        "Alta"],
        ["RNF014", "Dados em memória",        "Sessões de análise são armazenadas apenas em memória do processo, sem persistência de dados sensíveis do usuário.",                                        "Média"],
    ]
    story.append(req_table(rows, DARK))

    story += h2("4.5 Manutenibilidade")
    rows = [
        ["RNF015", "Modularidade dos agentes","Cada agente deve ser implementado em módulo Python independente, permitindo substituição ou atualização sem afetar os demais.",                             "Alta"],
        ["RNF016", "Sem framework de agentes","A orquestração deve usar Claude Tool Use nativo, sem dependência de LangChain ou CrewAI, para facilitar manutenção e debug.",                              "Média"],
        ["RNF017", "Documentação inline",     "Funções críticas do pipeline devem ter docstrings descritivos.",                                                                                           "Baixa"],
    ]
    story.append(req_table(rows, DARK))

# ─── 5. Casos de Uso ──────────────────────────────────────────────────────────
def casos_de_uso(story):
    story += h1("5. Casos de Uso")
    story.append(body(
        "Os casos de uso descrevem as interações entre os atores e o sistema. "
        "O ator principal é o <b>Usuário</b> (empreendedor, estudante ou profissional). "
        "O ator secundário é o <b>Sistema de Agentes</b> (execução autônoma do pipeline)."
    ))

    story += h2("5.1 Diagrama de Casos de Uso (textual)")
    rows_uc = [
        ["UC001", "Submeter ideia de negócio",   "O usuário digita ou seleciona uma ideia de negócio e solicita a análise.",                               "Usuário"],
        ["UC002", "Acompanhar pipeline ao vivo", "O usuário visualiza o progresso dos agentes em tempo real durante a análise.",                           "Usuário / Agentes"],
        ["UC003", "Visualizar relatório",         "O usuário acessa o relatório executivo completo gerado pelo Synthesis Agent.",                           "Usuário"],
        ["UC004", "Explorar debate estratégico",  "O usuário lê a transcrição do debate entre Advocate, Devil's Advocate e Mediator.",                     "Usuário"],
        ["UC005", "Consultar score de viabilidade","O usuário visualiza o score global e por dimensão no gráfico radar.",                                  "Usuário"],
        ["UC006", "Fazer pergunta ao Q&A Agent",  "O usuário digita uma pergunta sobre o relatório e recebe resposta do Q&A Agent.",                       "Usuário / Q&A Agent"],
        ["UC007", "Copiar relatório",             "O usuário copia o conteúdo completo do relatório para a área de transferência.",                        "Usuário"],
        ["UC008", "Iniciar nova análise",         "O usuário retorna à tela inicial para analisar uma nova ideia.",                                        "Usuário"],
    ]
    story.append(uc_table(rows_uc))

    story += h2("5.2 Fluxo Principal — UC001: Submeter Ideia de Negócio")
    fluxo = [
        ("Pré-condição",    "Backend e frontend em execução. Chaves de API configuradas."),
        ("Ator",            "Usuário"),
        ("Fluxo básico",    "1. Usuário acessa http://localhost:3000\n"
                            "2. Usuário digita a ideia de negócio no campo de texto\n"
                            "3. Usuário clica em 'Analisar ideia'\n"
                            "4. Sistema redireciona para página de análise com SSE\n"
                            "5. Sistema retorna session_id e inicia pipeline\n"
                            "6. Interface exibe AgentTimeline com agentes 'running'\n"
                            "7. Cada agente conclui e emite evento 'done'\n"
                            "8. Pipeline emite evento 'complete'\n"
                            "9. Interface exibe relatório completo com abas"),
        ("Fluxo alternativo","3a. Usuário clica em um dos exemplos pré-carregados → campo preenchido automaticamente"),
        ("Fluxo de exceção", "5a. Falha de conexão com API → mensagem de erro exibida → usuário pode tentar novamente"),
        ("Pós-condição",    "Relatório disponível nas abas. Q&A Agent ativo para consultas."),
    ]
    for label, desc in fluxo:
        t = Table([[Paragraph(f"<b>{label}</b>", style("fl", fontSize=9, fontName="Helvetica-Bold", textColor=INDIGO)),
                    Paragraph(desc, style("fd", fontSize=9, fontName="Helvetica", leading=13))]],
                  colWidths=[3.5*cm, 12.8*cm])
        t.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LINEBELOW",    (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
        ]))
        story.append(t)

# ─── 6. Stack Técnica ─────────────────────────────────────────────────────────
def stack_tecnica(story):
    story += h1("6. Stack Técnica e Arquitetura")

    story += h2("6.1 Tecnologias Utilizadas")
    stack = [
        ["Camada",       "Tecnologia",               "Versão",  "Função"],
        ["LLM",          "Claude Sonnet (Anthropic)", "4.6",     "Motor de raciocínio de todos os agentes"],
        ["Backend",      "Python / FastAPI",          "3.13 / 0.115", "API REST + SSE streaming"],
        ["Busca web",    "Tavily API",                "latest",  "Pesquisa em tempo real para agentes"],
        ["Frontend",     "Next.js / React",           "16 / 19", "Interface web com streaming ao vivo"],
        ["Estilo",       "Tailwind CSS",              "4.x",     "Design system utility-first"],
        ["Gráficos",     "Recharts",                  "2.x",     "Gráfico radar do score de viabilidade"],
        ["Env vars",     "python-dotenv",             "1.x",     "Gestão de chaves de API"],
    ]
    t = Table(stack, colWidths=[3*cm, 4.5*cm, 2.5*cm, 6.3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1),  INDIGO),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)

    story += h2("6.2 Estrutura de Diretórios")
    struct = (
        "pitchiq/\n"
        "├── backend/\n"
        "│   ├── main.py              # FastAPI app (endpoints /analyze, /qa, /session)\n"
        "│   ├── agents/\n"
        "│   │   ├── base.py          # Cliente Anthropic + retry logic + call_llm()\n"
        "│   │   ├── orchestrator.py  # Pipeline principal + SSE generator\n"
        "│   │   ├── market.py        # Market Research Agent\n"
        "│   │   ├── competitor.py    # Competitor Analysis Agent\n"
        "│   │   ├── audience.py      # Audience/ICP Agent\n"
        "│   │   ├── risk.py          # Risk Assessment Agent\n"
        "│   │   ├── advocate.py      # Advocate Agent\n"
        "│   │   ├── devil.py         # Devil's Advocate Agent\n"
        "│   │   ├── mediator.py      # Mediator Agent\n"
        "│   │   ├── synthesis.py     # Synthesis Agent\n"
        "│   │   └── qa.py            # Q&A Agent\n"
        "│   └── tools/web_search.py  # Tavily wrapper\n"
        "└── frontend/\n"
        "    ├── app/\n"
        "    │   ├── page.tsx         # Landing page\n"
        "    │   └── analysis/        # Página de análise com SSE\n"
        "    └── components/\n"
        "        ├── AgentTimeline    # Status em tempo real\n"
        "        ├── DebateView       # Visualização do debate\n"
        "        ├── ReportCard       # Relatório por seções\n"
        "        └── ScoreRadar       # Gráfico radar Recharts"
    )
    story.append(Paragraph(struct, S_CODE))

    story += h2("6.3 Fluxo de Dados SSE")
    story.append(body(
        "O endpoint <b>/analyze</b> utiliza StreamingResponse com media type "
        "<i>text/event-stream</i>. Cada evento SSE carrega um JSON com campos: "
        "<i>agent</i> (identificador), <i>status</i> (running/done/complete) e "
        "<i>data</i> (output do agente quando concluído). O frontend processa cada "
        "linha <code>data: {json}</code> para atualizar o estado React dos agentes em tempo real."
    ))

# ─── Montar documento ─────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
        title="DERS — PitchIQ",
        author="Samuel Guimarães Lopes",
        subject="Documento de Especificação de Requisitos de Software",
    )

    story = []

    # Capa (sem número de página)
    cover_page(story)

    # Histórico de revisões
    historico(story)
    story.append(PageBreak())

    # Seções
    introducao(story)
    story.append(PageBreak())
    descricao_geral(story)
    story.append(PageBreak())
    req_funcionais(story)
    story.append(PageBreak())
    req_nao_funcionais(story)
    story.append(PageBreak())
    casos_de_uso(story)
    story.append(PageBreak())
    stack_tecnica(story)

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF gerado: {OUTPUT}")

if __name__ == "__main__":
    build()
