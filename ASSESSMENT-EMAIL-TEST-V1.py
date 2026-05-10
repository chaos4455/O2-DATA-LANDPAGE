#!/usr/bin/env python3
"""
ASSESSMENT-EMAIL-TEST-V1.py
Simula um assessment completo de maturidade analítica e envia dois emails para otimizaestoque@gmail.com:
  1. Email INTERNO (dark theme premium) — notificação com score, perfil e pontuação por questão
  2. Email PARA O CLIENTE (light theme) — relatório de diagnóstico com recomendações personalizadas
Replica exatamente o comportamento do send_assessment_email_sync() do server.py.
"""
import smtplib, ssl, datetime, sys, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ─── Config SMTP (igual ao server.py) ────────────────────────────────────────
SMTP_HOST    = "smtp-relay.brevo.com"
SMTP_PORT    = 465
SMTP_USER    = "chaos4455@gmail.com"
SMTP_PASS    = "pZz9rCt2I5SdjKsY"
SENDER_EMAIL = "contato@o2data.com.br"
SENDER_NAME  = "O2 Data Solutions"
TEST_RCPT    = "otimizaestoque@gmail.com"

# ─── Assessment simulado ──────────────────────────────────────────────────────
ASSESSMENT = {
    "name":           "Rodrigo Almeida Ferreira",
    "email":          "rodrigo.ferreira@distribuidoraferreira.com.br",
    "company":        "Distribuidora Ferreira & Cia Ltda",
    "role":           "Diretor de Operações",
    "sector":         "Distribuição & Atacado",
    "employees":      "51-200",
    "revenue":        "R$ 20M – R$ 100M",
    "urgency":        "imediata",
    "budget":         "R$ 50k – R$ 150k",
    "main_challenge": (
        "Temos ruptura frequente nos itens A e ao mesmo tempo estoque parado nos itens C. "
        "Compramos de forma reativa, sem previsão de demanda estruturada. "
        "Nosso ERP é o TOTVS Protheus mas não temos integração com o WMS."
    ),
    "area":           "supply_chain",
    # Scores simulados para Supply Chain & Compras (22 questões, escala 0-10)
    "scores": {
        "sc_01": 3.0,  "sc_02": 4.0,  "sc_03": 2.0,  "sc_04": 2.0,  "sc_05": 3.0,
        "sc_06": 4.0,  "sc_07": 2.0,  "sc_08": 3.0,  "sc_09": 3.0,  "sc_10": 2.0,
        "sc_11": 4.0,  "sc_12": 2.0,  "sc_13": 3.0,  "sc_14": 2.0,  "sc_15": 3.0,
        "sc_16": 3.0,  "sc_17": 2.0,  "sc_18": 3.0,  "sc_19": 3.0,  "sc_20": 2.0,
        "sc_21": 3.0,  "sc_22": 2.0,
    },
}

# ─── Labels das questões (Supply Chain) ──────────────────────────────────────
QUESTION_LABELS = {
    "sc_01": "Previsão de demanda",
    "sc_02": "Visibilidade de estoque em tempo real",
    "sc_03": "Planejamento de compras e reposição",
    "sc_04": "Integração com fornecedores",
    "sc_05": "Monitoramento de desempenho de fornecedores",
    "sc_06": "Controle do custo total de aquisição (TCO)",
    "sc_07": "Identificação e gestão de rupturas",
    "sc_08": "Análise de sazonalidade e tendências",
    "sc_09": "Gestão de estoque de segurança e giro",
    "sc_10": "Rastreabilidade dos produtos",
    "sc_11": "Análise e otimização de custos logísticos",
    "sc_12": "Automação de cotação e negociação",
    "sc_13": "Medição e redução de lead time",
    "sc_14": "Análise de risco na cadeia de suprimentos",
    "sc_15": "Uso de dados para negociação com fornecedores",
    "sc_16": "Integração Supply Chain × Vendas (S&OP)",
    "sc_17": "Gestão de produtos com baixo giro / obsoletos",
    "sc_18": "Analytics para otimização do mix de produtos",
    "sc_19": "Monitoramento de qualidade dos produtos recebidos",
    "sc_20": "Maturidade do processo de S&OP",
    "sc_21": "Análise do impacto financeiro das decisões de estoque",
    "sc_22": "Uso de dados externos no planejamento",
}

RECOMMENDATIONS = {
    "critico": [
        "Implemente controle de estoque com alertas automáticos de ruptura por SKU",
        "Crie previsão de demanda baseada em histórico dos últimos 12 meses com decomposição de sazonalidade",
        "Estabeleça KPIs básicos: giro de estoque, cobertura e taxa de ruptura por categoria",
        "Automatize cotação com pelo menos 3 fornecedores por item crítico (curva A)",
        "Defina política de estoque de segurança para os 20% de itens mais críticos (Pareto)",
    ],
    "desenvolvimento": [
        "Implemente modelos de previsão com decomposição de sazonalidade e variáveis externas",
        "Automatize reposição com ponto de pedido dinâmico baseado em variabilidade de demanda",
        "Integre dados de fornecedores via API para visibilidade em tempo real do lead time",
        "Implemente análise ABC-XYZ para otimizar políticas de estoque por categoria",
        "Desenvolva scorecard de fornecedores com KPIs automatizados e alertas de desvio",
    ],
    "avancado": [
        "Explore IA generativa para otimização de contratos e negociação com fornecedores",
        "Implemente digital twin da cadeia para simulações avançadas de cenários",
        "Desenvolva modelos de otimização de rede logística multi-objetivo",
        "Implemente IoT e RFID para rastreabilidade end-to-end em tempo real",
        "Explore blockchain para transparência e auditabilidade na cadeia de fornecimento",
    ],
}

AREA_LABELS = {
    "supply_chain": "Supply Chain & Compras",
    "comercial":    "Inteligência Comercial & RevOps",
    "credito_risco":"Crédito & Risco",
    "dados_ml":     "Dados & Machine Learning",
    "automacao":    "Automação, RPA & Alertas",
    "dashboards":   "Dashboards & Analytics",
}

AREA_ICONS = {
    "supply_chain": "🚚",
    "comercial":    "📈",
    "credito_risco":"🛡️",
    "dados_ml":     "🧠",
    "automacao":    "🤖",
    "dashboards":   "📊",
}

AREA_COLORS = {
    "supply_chain": "#3b82f6",
    "comercial":    "#8b5cf6",
    "credito_risco":"#ef4444",
    "dados_ml":     "#06b6d4",
    "automacao":    "#f59e0b",
    "dashboards":   "#22c55e",
}

# ─── Calcular score ───────────────────────────────────────────────────────────
scores  = ASSESSMENT["scores"]
values  = list(scores.values())
total   = sum(values)
n_q     = len(values)
avg     = total / n_q
pct     = round((total / (n_q * 10)) * 100)

if avg <= 3.9:
    level_label   = "Crítico"
    level_color   = "#ef4444"
    level_bg_int  = "#1a0a0a"
    level_bg_cli  = "#fef2f2"
    level_msg_int = "Oportunidades imediatas de melhoria com alto impacto. Prioridade máxima."
    level_msg_cli = "Sua empresa está nos estágios iniciais da jornada analítica. Há oportunidades significativas de melhoria que podem gerar retorno rápido."
    level_key     = "critico"
elif avg <= 6.9:
    level_label   = "Em Desenvolvimento"
    level_color   = "#f59e0b"
    level_bg_int  = "#1a1200"
    level_bg_cli  = "#fffbeb"
    level_msg_int = "Jornada iniciada, lacunas importantes identificadas. Potencial de aceleração alto."
    level_msg_cli = "Você já iniciou a jornada analítica. Com as iniciativas certas, pode acelerar significativamente os resultados."
    level_key     = "desenvolvimento"
else:
    level_label   = "Avançado"
    level_color   = "#22c55e"
    level_bg_int  = "#0a1a0a"
    level_bg_cli  = "#f0fdf4"
    level_msg_int = "Maturidade elevada. Foco em otimização, escala e tecnologias emergentes."
    level_msg_cli = "Sua empresa demonstra maturidade analítica elevada. O foco agora é otimizar, escalar e explorar IA generativa."
    level_key     = "avancado"

area       = ASSESSMENT["area"]
area_label = AREA_LABELS.get(area, area)
area_icon  = AREA_ICONS.get(area, "📊")
area_color = AREA_COLORS.get(area, "#2563eb")
name       = ASSESSMENT["name"]
email_addr = ASSESSMENT["email"]
company    = ASSESSMENT["company"]
role       = ASSESSMENT["role"]
sector     = ASSESSMENT["sector"]
employees  = ASSESSMENT["employees"]
revenue    = ASSESSMENT["revenue"]
urgency    = ASSESSMENT["urgency"]
budget     = ASSESSMENT["budget"]
challenge  = ASSESSMENT["main_challenge"]
ts         = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

# ─── Gerar linhas de score (interno dark) ────────────────────────────────────
def score_rows_int(sc):
    rows = []
    for qid, sv in sc.items():
        lbl = QUESTION_LABELS.get(qid, qid)
        bc  = "#ef4444" if sv <= 3 else "#f59e0b" if sv <= 6 else "#22c55e"
        bp  = int(sv * 10)
        rows.append(
            f'<tr>'
            f'<td style="padding:7px 0;font-size:12px;color:#94a3b8;width:55%;border-bottom:1px solid #1e293b">{lbl}</td>'
            f'<td style="padding:7px 8px;width:35%;border-bottom:1px solid #1e293b">'
            f'<div style="background:#1e293b;border-radius:4px;height:7px;overflow:hidden">'
            f'<div style="width:{bp}%;height:7px;background:{bc};border-radius:4px"></div></div></td>'
            f'<td style="padding:7px 0;text-align:right;font-weight:700;font-size:12px;color:{bc};border-bottom:1px solid #1e293b">{sv:.1f}/10</td>'
            f'</tr>'
        )
    return "".join(rows)

# ─── Gerar linhas de score (cliente light) ───────────────────────────────────
def score_rows_cli(sc):
    rows = []
    for qid, sv in sc.items():
        lbl = QUESTION_LABELS.get(qid, qid)
        bc  = "#ef4444" if sv <= 3 else "#f59e0b" if sv <= 6 else "#22c55e"
        bp  = int(sv * 10)
        rows.append(
            f'<tr>'
            f'<td style="padding:8px 0;font-size:13px;color:#475569;width:55%;border-bottom:1px solid #e2e8f0">{lbl}</td>'
            f'<td style="padding:8px 8px;width:35%;border-bottom:1px solid #e2e8f0">'
            f'<div style="background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden">'
            f'<div style="width:{bp}%;height:8px;background:{bc};border-radius:4px"></div></div></td>'
            f'<td style="padding:8px 0;text-align:right;font-weight:700;font-size:13px;color:{bc};border-bottom:1px solid #e2e8f0">{sv:.1f}/10</td>'
            f'</tr>'
        )
    return "".join(rows)

# ─── Recomendações (interno dark) ────────────────────────────────────────────
def recs_int(level_k):
    recs = RECOMMENDATIONS.get(level_k, [])
    if not recs:
        return ""
    items = "".join(
        f'<li style="margin-bottom:10px;padding:10px 12px;background:#0f172a;border-radius:8px;'
        f'border-left:3px solid #3b82f6;font-size:12px;color:#cbd5e1;line-height:1.5">{r}</li>'
        for r in recs
    )
    return (
        f'<div style="margin-top:24px">'
        f'<p style="margin:0 0 12px;font-size:10px;font-weight:700;color:#475569;'
        f'text-transform:uppercase;letter-spacing:1.5px">📋 Recomendações Prioritárias</p>'
        f'<ul style="margin:0;padding:0;list-style:none">{items}</ul></div>'
    )

# ─── Recomendações (cliente light) ───────────────────────────────────────────
def recs_cli(level_k):
    recs = RECOMMENDATIONS.get(level_k, [])
    if not recs:
        return ""
    items = "".join(
        f'<li style="margin-bottom:12px;padding:14px 16px;background:#f8fafc;border-radius:10px;'
        f'border-left:4px solid #2563eb;font-size:13px;color:#334155;line-height:1.6">'
        f'<span style="font-weight:700;color:#1d4ed8">→</span> {r}</li>'
        for r in recs
    )
    return (
        f'<div style="margin-top:28px">'
        f'<p style="margin:0 0 14px;font-size:14px;font-weight:700;color:#1e293b">'
        f'🎯 Recomendações Prioritárias para Você</p>'
        f'<ul style="margin:0;padding:0;list-style:none">{items}</ul></div>'
    )

srows_int_html = score_rows_int(scores)
srows_cli_html = score_rows_cli(scores)
recs_int_html  = recs_int(level_key)
recs_cli_html  = recs_cli(level_key)


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL 1: INTERNO (dark theme premium) — notificação para a equipe O2
# ═══════════════════════════════════════════════════════════════════════════════
html_int = f"""<!DOCTYPE html>
<html lang='pt-BR'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'></head>
<body style='margin:0;padding:0;background:#060b18;font-family:Segoe UI,Arial,sans-serif'>
<table width='100%' cellpadding='0' cellspacing='0' style='background:#060b18;padding:32px 16px'>
<tr><td align='center'>
<table width='660' cellpadding='0' cellspacing='0' style='max-width:660px;width:100%'>

  <!-- HEADER -->
  <tr><td style='background:linear-gradient(135deg,#1e3a8a 0%,#5b21b6 100%);border-radius:16px 16px 0 0;padding:28px 36px'>
    <table width='100%' cellpadding='0' cellspacing='0'><tr>
      <td>
        <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:2px'>O2 Data Solutions — Assessment Interno · TESTE</p>
        <h1 style='margin:0;font-size:21px;font-weight:800;color:#fff'>📊 Diagnóstico de Maturidade Analítica</h1>
        <p style='margin:8px 0 0;font-size:12px;color:rgba(255,255,255,.6)'>{ts} · {area_icon} {area_label} · <span style="color:#fbbf24">⚡ SIMULADO</span></p>
      </td>
      <td align='right' style='vertical-align:middle'>
        <div style='background:rgba(255,255,255,.1);border-radius:12px;padding:10px 14px;font-size:28px;line-height:1'>{area_icon}</div>
      </td>
    </tr></table>
  </td></tr>

  <!-- SCORE BADGE + PERFIL -->
  <tr><td style='background:#0d1526;padding:24px 36px 0'>
    <table width='100%' cellpadding='0' cellspacing='0'>
      <tr>
        <td style='background:{level_bg_int};border:1px solid {level_color}33;border-radius:12px;padding:20px 24px' width='48%'>
          <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:{level_color};text-transform:uppercase;letter-spacing:1px'>Score Geral</p>
          <p style='margin:0;font-size:42px;font-weight:900;color:{level_color};line-height:1'>{avg:.1f}<span style='font-size:18px;color:#475569'>/10</span></p>
          <p style='margin:6px 0 0;font-size:13px;font-weight:700;color:{level_color}'>{level_label}</p>
          <p style='margin:4px 0 0;font-size:11px;color:#64748b'>{pct}% de maturidade · {n_q} questões</p>
        </td>
        <td width='4%'></td>
        <td style='background:#0f172a;border-radius:12px;padding:20px 24px;vertical-align:top' width='48%'>
          <p style='margin:0 0 8px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px'>Perfil</p>
          <p style='margin:0 0 4px;font-size:14px;font-weight:700;color:#f1f5f9'>{name}</p>
          <p style='margin:0 0 4px;font-size:12px;color:#94a3b8'>{company}</p>
          <p style='margin:0 0 4px;font-size:11px;color:#64748b'>{role} · {sector}</p>
          <p style='margin:0 0 4px;font-size:11px;color:#64748b'>{employees} func. · {revenue}</p>
          <p style='margin:0;font-size:11px;color:#64748b'>Urgência: {urgency} · Budget: {budget}</p>
        </td>
      </tr>
    </table>
    <p style='margin:16px 0 0;font-size:12px;color:#64748b;font-style:italic'>{level_msg_int}</p>
  </td></tr>

  <!-- DESAFIO -->
  <tr><td style='background:#0d1526;padding:20px 36px 0'>
    <div style='background:#0f172a;border-radius:10px;padding:16px 18px;border-left:4px solid #7c3aed'>
      <p style='margin:0 0 6px;font-size:10px;font-weight:700;color:#a78bfa;text-transform:uppercase;letter-spacing:.5px'>Principal Desafio</p>
      <p style='margin:0;font-size:13px;color:#cbd5e1;line-height:1.6'>{challenge}</p>
    </div>
  </td></tr>

  <!-- CONTATO -->
  <tr><td style='background:#0d1526;padding:20px 36px 0'>
    <p style='margin:0 0 12px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.5px'>Contato</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      <tr>
        <td style='padding-right:6px' width='50%'>
          <a href='mailto:{email_addr}' style='display:block;background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:12px 14px;text-decoration:none'>
            <span style='font-size:10px;color:#475569;display:block;margin-bottom:2px'>📧 E-mail</span>
            <span style='font-size:13px;font-weight:700;color:#60a5fa'>{email_addr}</span>
          </a>
        </td>
        <td style='padding-left:6px' width='50%'>
          <a href='https://wa.me/5511913353137' style='display:block;background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:12px 14px;text-decoration:none'>
            <span style='font-size:10px;color:#475569;display:block;margin-bottom:2px'>💬 Responder</span>
            <span style='font-size:13px;font-weight:700;color:#4ade80'>WhatsApp</span>
          </a>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- SCORES POR QUESTÃO -->
  <tr><td style='background:#0d1526;padding:24px 36px 0'>
    <p style='margin:0 0 14px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.5px'>📈 Pontuação por Dimensão — {area_label}</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      {srows_int_html}
    </table>
  </td></tr>

  <!-- RECOMENDAÇÕES -->
  <tr><td style='background:#0d1526;padding:0 36px 28px'>
    {recs_int_html}
  </td></tr>

  <!-- FOOTER -->
  <tr><td style='background:#060b18;border-radius:0 0 16px 16px;padding:18px 36px;border-top:1px solid #0d1526'>
    <p style='margin:0;font-size:11px;color:#334155;text-align:center'>
      O2 Data Solutions · Maringá, PR · <a href='mailto:contato@o2data.com.br' style='color:#3b82f6;text-decoration:none'>contato@o2data.com.br</a>
    </p>
  </td></tr>

</table></td></tr></table>
</body></html>"""

# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL 2: CLIENTE (light theme) — relatório de diagnóstico personalizado
# ═══════════════════════════════════════════════════════════════════════════════
html_cli = f"""<!DOCTYPE html>
<html lang='pt-BR'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'></head>
<body style='margin:0;padding:0;background:#f1f5f9;font-family:Segoe UI,Arial,sans-serif'>
<table width='100%' cellpadding='0' cellspacing='0' style='background:#f1f5f9;padding:32px 16px'>
<tr><td align='center'>
<table width='640' cellpadding='0' cellspacing='0' style='max-width:640px;width:100%'>

  <!-- HEADER -->
  <tr><td style='background:linear-gradient(135deg,#1e40af 0%,#6d28d9 100%);border-radius:16px 16px 0 0;padding:32px 36px'>
    <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:2px'>O2 Data Solutions</p>
    <h1 style='margin:0;font-size:22px;font-weight:800;color:#fff;line-height:1.2'>Seu Diagnóstico de Maturidade Analítica</h1>
    <p style='margin:10px 0 0;font-size:13px;color:rgba(255,255,255,.75)'>{area_icon} {area_label} · {ts}</p>
  </td></tr>

  <!-- SAUDAÇÃO -->
  <tr><td style='background:#fff;padding:28px 36px 0'>
    <p style='margin:0;font-size:15px;color:#334155;line-height:1.6'>
      Olá, <strong>{name}</strong>! Obrigado por completar o diagnóstico de maturidade analítica da <strong>{company}</strong>.
      Abaixo você encontra seu resultado completo com recomendações personalizadas para a área de <strong>{area_label}</strong>.
    </p>
  </td></tr>

  <!-- SCORE -->
  <tr><td style='background:#fff;padding:24px 36px 0'>
    <div style='background:{level_bg_cli};border:2px solid {level_color}33;border-radius:14px;padding:24px 28px'>
      <table width='100%' cellpadding='0' cellspacing='0'><tr>
        <td style='vertical-align:middle' width='30%'>
          <div style='text-align:center'>
            <div style='font-size:52px;font-weight:900;color:{level_color};line-height:1'>{avg:.1f}</div>
            <div style='font-size:12px;color:#64748b;font-weight:600'>de 10</div>
          </div>
        </td>
        <td style='padding-left:20px;vertical-align:middle'>
          <p style='margin:0 0 6px;font-size:18px;font-weight:800;color:{level_color}'>{level_label}</p>
          <p style='margin:0 0 8px;font-size:13px;color:#475569;line-height:1.5'>{level_msg_cli}</p>
          <div style='background:#e2e8f0;border-radius:6px;height:10px;overflow:hidden;margin-top:10px'>
            <div style='width:{pct}%;height:10px;background:{level_color};border-radius:6px'></div>
          </div>
          <p style='margin:6px 0 0;font-size:11px;color:#64748b;font-weight:600'>{pct}% de maturidade analítica · {n_q} dimensões avaliadas</p>
        </td>
      </tr></table>
    </div>
  </td></tr>

  <!-- ÁREA AVALIADA -->
  <tr><td style='background:#fff;padding:20px 36px 0'>
    <div style='background:#f8fafc;border-radius:10px;padding:16px 20px;border-left:4px solid {area_color}'>
      <p style='margin:0 0 4px;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px'>Área Avaliada</p>
      <p style='margin:0;font-size:16px;font-weight:700;color:#1e293b'>{area_icon} {area_label}</p>
    </div>
  </td></tr>

  <!-- SCORES POR DIMENSÃO -->
  <tr><td style='background:#fff;padding:24px 36px 0'>
    <p style='margin:0 0 14px;font-size:14px;font-weight:700;color:#1e293b'>📈 Sua Pontuação por Dimensão</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      {srows_cli_html}
    </table>
  </td></tr>

  <!-- RECOMENDAÇÕES -->
  <tr><td style='background:#fff;padding:0 36px 28px'>
    {recs_cli_html}
  </td></tr>

  <!-- PRÓXIMOS PASSOS -->
  <tr><td style='background:#f8fafc;padding:24px 36px;border-top:1px solid #e2e8f0'>
    <p style='margin:0 0 14px;font-size:14px;font-weight:700;color:#1e293b'>🚀 Próximos Passos</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      <tr><td style='padding:10px 14px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;margin-bottom:8px;display:block'>
        <span style='font-size:13px;color:#334155'>1. <strong>Agende uma reunião de diagnóstico</strong> gratuita de 1 hora com nossa equipe</span>
      </td></tr>
      <tr><td style='height:8px'></td></tr>
      <tr><td style='padding:10px 14px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;display:block'>
        <span style='font-size:13px;color:#334155'>2. <strong>Receba um roadmap personalizado</strong> com as iniciativas de maior impacto e ROI estimado</span>
      </td></tr>
      <tr><td style='height:8px'></td></tr>
      <tr><td style='padding:10px 14px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;display:block'>
        <span style='font-size:13px;color:#334155'>3. <strong>Avalie as outras 5 áreas</strong> do diagnóstico para ter uma visão completa da maturidade analítica</span>
      </td></tr>
    </table>
  </td></tr>

  <!-- CTA -->
  <tr><td style='background:#fff;padding:28px 36px;border-top:1px solid #e2e8f0;text-align:center'>
    <p style='margin:0 0 8px;font-size:15px;font-weight:700;color:#1e293b'>Quer um roadmap personalizado para sua empresa?</p>
    <p style='margin:0 0 20px;font-size:13px;color:#64748b;line-height:1.5'>
      Nossa equipe cria um plano de ação detalhado com base no seu diagnóstico,
      priorizando as iniciativas de maior impacto e ROI mensurável.
    </p>
    <a href='https://wa.me/5511913353137?text=Ola%21+Fiz+o+diagnostico+de+maturidade+analitica+e+gostaria+de+agendar+uma+reuniao+de+diagnostico.'
       style='display:inline-block;background:linear-gradient(135deg,#1e40af,#6d28d9);color:#fff;padding:16px 32px;border-radius:50px;text-decoration:none;font-weight:700;font-size:15px'>
      📅 Agendar Reunião de Diagnóstico
    </a>
    <p style='margin:16px 0 0;font-size:12px;color:#94a3b8'>Gratuita · 1 hora · Sem compromisso · Resposta em até 24h úteis</p>
  </td></tr>

  <!-- FOOTER -->
  <tr><td style='background:#f1f5f9;border-radius:0 0 16px 16px;padding:20px 36px;border-top:1px solid #e2e8f0'>
    <p style='margin:0;font-size:11px;color:#94a3b8;text-align:center'>
      O2 Data Solutions · Maringá, PR ·
      <a href='mailto:contato@o2data.com.br' style='color:#2563eb;text-decoration:none'>contato@o2data.com.br</a> ·
      <a href='https://wa.me/5511913353137' style='color:#16a34a;text-decoration:none'>(11) 9 1335-3137</a>
    </p>
    <p style='margin:8px 0 0;font-size:10px;color:#cbd5e1;text-align:center'>
      Você recebeu este e-mail porque completou o diagnóstico de maturidade analítica em o2data.com.br
    </p>
  </td></tr>

</table></td></tr></table>
</body></html>"""




# ─── Funcao de envio ──────────────────────────────────────────────────────────
def send(subject, html, from_name, from_email, to, reply_to=None):
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = from_name + " <" + from_email + ">"
        msg["To"]      = to
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.attach(MIMEText(html, "html", "utf-8"))
        srv.sendmail(from_email, to, msg.as_string())

# ─── Execucao ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SEP = "=" * 65
    print(f"\n{SEP}")
    print(f"  ASSESSMENT-EMAIL-TEST-V1 -- O2 Data Solutions")
    print(f"  Empresa: {company} | Area: {area_label}")
    print(f"  Score: {avg:.1f}/10 ({level_label}) | {pct}% maturidade")
    print(f"  Destino de teste: {TEST_RCPT}")
    print(f"{SEP}\n")

    print(f"[1/2] Enviando EMAIL INTERNO (dark) -> {TEST_RCPT} ...")
    try:
        send(
            subject    = f"[O2 Assessment] {name} -- {area_label} | Score: {avg:.1f}/10 ({level_label})",
            html       = html_int,
            from_name  = SENDER_NAME,
            from_email = SENDER_EMAIL,
            to         = TEST_RCPT,
            reply_to   = email_addr,
        )
        print("  OK Email interno enviado!")
    except Exception as e:
        print(f"  ERRO: {e}")

    print(f"\n[2/2] Enviando EMAIL CLIENTE (light) -> {TEST_RCPT} ...")
    try:
        send(
            subject    = f"Seu Diagnostico de Maturidade Analitica -- {area_label} | O2 Data Solutions",
            html       = html_cli,
            from_name  = SENDER_NAME,
            from_email = SENDER_EMAIL,
            to         = TEST_RCPT,
            reply_to   = SENDER_EMAIL,
        )
        print("  OK Email cliente enviado!")
    except Exception as e:
        print(f"  ERRO: {e}")

    print(f"\n{SEP}")
    print(f"  Teste concluido -- verifique {TEST_RCPT}")
    print(f"  Score simulado: {avg:.1f}/10 | Nivel: {level_label} | {pct}% maturidade")
    print(f"{SEP}\n")
