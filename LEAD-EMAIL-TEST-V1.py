#!/usr/bin/env python3
"""
LEAD-EMAIL-TEST-V1.py
Simula um lead preenchendo o formulário e envia dois emails para otimizaestoque@gmail.com:
  1. Email "do lead" → confirmação que o lead receberia (light theme, tom de resposta)
  2. Email "para mim" → notificação interna de novo lead (dark theme premium)
"""
import smtplib, ssl, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ─── Config SMTP (igual ao server.py) ────────────────────────────────────────
SMTP_HOST    = "smtp-relay.brevo.com"
SMTP_PORT    = 465
SMTP_USER    = "chaos4455@gmail.com"
SMTP_PASS    = "pZz9rCt2I5SdjKsY"
SENDER_EMAIL = "contato@o2data.com.br"
SENDER_NAME  = "O2 Data Solutions"
TEST_RCPT    = "otimizaestoque@gmail.com"   # destino de ambos os emails no teste

# ─── Lead simulado ────────────────────────────────────────────────────────────
LEAD = {
    "name":      "Carlos Eduardo Mendes",
    "company":   "Distribuidora Mendes & Filhos Ltda",
    "email":     "carlos.mendes@mendesfilhos.com.br",
    "phone":     "+55 (44) 9 9812-3456",
    "challenge": "Reduzir ruptura de estoque e melhorar previsão de demanda",
    "message":   (
        "Temos uma operação com mais de 8.000 SKUs e estamos perdendo vendas por ruptura "
        "frequente nos itens A. Nosso ERP é o TOTVS Protheus mas não temos nenhum modelo "
        "de previsão de demanda estruturado. Gostaria de entender como a O2 pode nos ajudar "
        "a resolver isso nos próximos 3 meses."
    ),
}

ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

# ─────────────────────────────────────────────────────────────────────────────
# EMAIL 1: Para o LEAD (light theme — confirmação de recebimento)
# Simula o que o lead receberia como resposta automática
# ─────────────────────────────────────────────────────────────────────────────
html_lead = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recebemos seu contato — O2 Data Solutions</title></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 16px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <!-- HEADER -->
  <tr><td style="background:linear-gradient(135deg,#1e40af 0%,#6d28d9 100%);border-radius:16px 16px 0 0;padding:32px 36px">
    <p style="margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:2px">O2 Data Solutions</p>
    <h1 style="margin:0;font-size:22px;font-weight:800;color:#fff;line-height:1.2">Recebemos seu contato! 🎯</h1>
    <p style="margin:10px 0 0;font-size:13px;color:rgba(255,255,255,.75)">{ts}</p>
  </td></tr>

  <!-- BODY -->
  <tr><td style="background:#fff;padding:32px 36px">
    <p style="margin:0 0 16px;font-size:15px;color:#334155;line-height:1.7">
      Olá, <strong style="color:#1e293b">{LEAD['name']}</strong>!
    </p>
    <p style="margin:0 0 16px;font-size:14px;color:#475569;line-height:1.7">
      Recebemos sua mensagem e nossa equipe já foi notificada. Entraremos em contato em breve
      para entender melhor o desafio da <strong>{LEAD['company']}</strong> e apresentar
      como podemos ajudar.
    </p>
    <p style="margin:0 0 24px;font-size:14px;color:#475569;line-height:1.7">
      Enquanto isso, você pode nos chamar diretamente pelo WhatsApp para uma conversa rápida:
    </p>

    <!-- Resumo do contato -->
    <div style="background:#f8fafc;border-radius:12px;padding:20px 24px;margin-bottom:24px;border:1px solid #e2e8f0">
      <p style="margin:0 0 12px;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px">Resumo do seu contato</p>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="padding:6px 0;font-size:12px;color:#94a3b8;width:120px">Empresa</td>
          <td style="padding:6px 0;font-size:13px;font-weight:600;color:#1e293b">{LEAD['company']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:12px;color:#94a3b8">Desafio</td>
          <td style="padding:6px 0;font-size:13px;font-weight:600;color:#7c3aed">{LEAD['challenge']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:12px;color:#94a3b8">WhatsApp</td>
          <td style="padding:6px 0;font-size:13px;font-weight:600;color:#16a34a">{LEAD['phone']}</td>
        </tr>
      </table>
    </div>

    <!-- CTA WhatsApp -->
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding-right:8px" width="50%">
          <a href="https://wa.me/5511913353137?text=Ola%21+Acabei+de+enviar+meu+contato+pelo+site+da+O2+Data+Solutions+e+gostaria+de+agendar+uma+reuniao+de+diagnostico."
             style="display:block;background:#16a34a;color:#fff;padding:14px 20px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;text-align:center">
            💬 Falar no WhatsApp
          </a>
        </td>
        <td style="padding-left:8px" width="50%">
          <a href="mailto:contato@o2data.com.br?subject=Re: Contato de {LEAD['name']}"
             style="display:block;background:#2563eb;color:#fff;padding:14px 20px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;text-align:center">
            📧 Enviar E-mail
          </a>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- DIFERENCIAIS -->
  <tr><td style="background:#f8fafc;padding:24px 36px;border-top:1px solid #e2e8f0">
    <p style="margin:0 0 14px;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px">Por que a O2 Data Solutions?</p>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding:8px 12px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;margin-bottom:8px;display:block">
          <span style="font-size:13px;color:#334155">🚀 <strong>Resultados em semanas</strong>, não meses</span>
        </td>
      </tr>
      <tr><td style="height:8px"></td></tr>
      <tr>
        <td style="padding:8px 12px;background:#fff;border-radius:8px;border:1px solid #e2e8f0">
          <span style="font-size:13px;color:#334155">🧠 <strong>IA e ML aplicados</strong> ao seu negócio real</span>
        </td>
      </tr>
      <tr><td style="height:8px"></td></tr>
      <tr>
        <td style="padding:8px 12px;background:#fff;border-radius:8px;border:1px solid #e2e8f0">
          <span style="font-size:13px;color:#334155">📊 <strong>Dashboards e automações</strong> que a equipe realmente usa</span>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- FOOTER -->
  <tr><td style="background:#f1f5f9;border-radius:0 0 16px 16px;padding:20px 36px;border-top:1px solid #e2e8f0">
    <p style="margin:0;font-size:11px;color:#94a3b8;text-align:center">
      O2 Data Solutions · Maringá, PR ·
      <a href="mailto:contato@o2data.com.br" style="color:#2563eb;text-decoration:none">contato@o2data.com.br</a> ·
      <a href="https://wa.me/5511913353137" style="color:#16a34a;text-decoration:none">(11) 9 1335-3137</a>
    </p>
    <p style="margin:8px 0 0;font-size:10px;color:#cbd5e1;text-align:center">
      Você recebeu este e-mail porque preencheu o formulário de contato em o2data.com.br
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body></html>"""

# ─────────────────────────────────────────────────────────────────────────────
# EMAIL 2: Para MIM (dark theme premium — notificação interna de lead)
# Mesmo design do send_email_sync do server.py
# ─────────────────────────────────────────────────────────────────────────────
msg_block = (
    f"<div style='margin-top:20px;padding:16px 18px;background:#0f172a;"
    f"border-radius:10px;border-left:4px solid #7c3aed'>"
    f"<p style='margin:0 0 6px;font-size:11px;font-weight:700;color:#a78bfa;"
    f"text-transform:uppercase;letter-spacing:.5px'>Mensagem</p>"
    f"<p style='margin:0;font-size:13px;color:#cbd5e1;line-height:1.6'>{LEAD['message']}</p>"
    f"</div>"
)

html_interno = f"""<!DOCTYPE html>
<html lang='pt-BR'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'></head>
<body style='margin:0;padding:0;background:#060b18;font-family:Segoe UI,Arial,sans-serif'>
<table width='100%' cellpadding='0' cellspacing='0' style='background:#060b18;padding:32px 16px'>
<tr><td align='center'>
<table width='620' cellpadding='0' cellspacing='0' style='max-width:620px;width:100%'>
  <tr><td style='background:linear-gradient(135deg,#1e3a8a 0%,#5b21b6 100%);border-radius:16px 16px 0 0;padding:30px 36px'>
    <table width='100%' cellpadding='0' cellspacing='0'><tr>
      <td>
        <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:2px'>O2 Data Solutions — CRM Interno</p>
        <h1 style='margin:0;font-size:22px;font-weight:800;color:#fff'>🎯 Novo Lead Recebido</h1>
        <p style='margin:8px 0 0;font-size:12px;color:rgba(255,255,255,.65)'>{ts} · Formulário de Contato · <span style='color:#fbbf24'>⚡ TESTE</span></p>
      </td>
      <td align='right' style='vertical-align:middle'>
        <div style='background:rgba(255,255,255,.12);border-radius:12px;padding:10px 14px;font-size:22px;line-height:1'>🎯</div>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style='background:#0d1526;padding:28px 36px'>
    <p style='margin:0 0 14px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.5px'>Dados do Contato</p>
    <table width='100%' cellpadding='0' cellspacing='0' style='border-collapse:collapse'>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>👤 Nome</span>
        <span style='font-size:15px;font-weight:700;color:#f1f5f9'>{LEAD['name']}</span>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>🏢 Empresa</span>
        <span style='font-size:15px;font-weight:700;color:#f1f5f9'>{LEAD['company']}</span>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>📧 E-mail</span>
        <a href='mailto:{LEAD['email']}' style='font-size:15px;font-weight:700;color:#60a5fa;text-decoration:none'>{LEAD['email']}</a>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>📱 WhatsApp</span>
        <span style='font-size:15px;font-weight:700;color:#4ade80'>{LEAD['phone']}</span>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>🎯 Principal Desafio</span>
        <span style='font-size:15px;font-weight:700;color:#c084fc'>{LEAD['challenge']}</span>
      </td></tr>
    </table>
    {msg_block}
    <table width='100%' cellpadding='0' cellspacing='0' style='margin-top:24px'><tr>
      <td style='padding-right:6px' width='50%'>
        <a href='https://wa.me/5511913353137' style='display:block;background:#16a34a;color:#fff;padding:13px 16px;border-radius:10px;text-decoration:none;font-weight:700;font-size:13px;text-align:center'>💬 WhatsApp</a>
      </td>
      <td style='padding-left:6px' width='50%'>
        <a href='mailto:{LEAD['email']}?subject=Re: Contato O2 Data Solutions' style='display:block;background:#2563eb;color:#fff;padding:13px 16px;border-radius:10px;text-decoration:none;font-weight:700;font-size:13px;text-align:center'>📧 E-mail</a>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style='background:#060b18;border-radius:0 0 16px 16px;padding:18px 36px;border-top:1px solid #0d1526'>
    <p style='margin:0;font-size:11px;color:#334155;text-align:center'>
      O2 Data Solutions · Maringá, PR · <a href='mailto:contato@o2data.com.br' style='color:#3b82f6;text-decoration:none'>contato@o2data.com.br</a>
    </p>
  </td></tr>
</table></td></tr></table>
</body></html>"""

# ─── Envia os dois emails ─────────────────────────────────────────────────────
def send(subject, html, from_name, from_email, to, reply_to=None):
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{from_name} <{from_email}>"
        msg["To"]      = to
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.attach(MIMEText(html, "html", "utf-8"))
        srv.sendmail(from_email, to, msg.as_string())

print(f"\n{'='*60}")
print(f"  LEAD-EMAIL-TEST-V1 — O2 Data Solutions")
print(f"  Lead simulado: {LEAD['name']} | {LEAD['company']}")
print(f"  Destino de teste: {TEST_RCPT}")
print(f"{'='*60}\n")

# Email 1: confirmação para o lead (enviado "como" o lead receberia)
print(f"[1/2] Enviando email DO LEAD (confirmação) → {TEST_RCPT} ...")
try:
    send(
        subject   = f"Recebemos seu contato — O2 Data Solutions",
        html      = html_lead,
        from_name = SENDER_NAME,
        from_email= SENDER_EMAIL,
        to        = TEST_RCPT,
        reply_to  = LEAD["email"],
    )
    print(f"  ✅ Email do lead enviado!")
except Exception as e:
    print(f"  ❌ ERRO: {e}")

# Email 2: notificação interna (o que eu recebo quando um lead chega)
print(f"\n[2/2] Enviando email PARA MIM (notificação interna) → {TEST_RCPT} ...")
try:
    send(
        subject   = f"[O2 Lead] {LEAD['name']} — {LEAD['company']} | {LEAD['challenge']}",
        html      = html_interno,
        from_name = SENDER_NAME,
        from_email= SENDER_EMAIL,
        to        = TEST_RCPT,
        reply_to  = LEAD["email"],
    )
    print(f"  ✅ Email interno enviado!")
except Exception as e:
    print(f"  ❌ ERRO: {e}")

print(f"\n{'='*60}")
print(f"  Teste concluído — verifique {TEST_RCPT}")
print(f"{'='*60}\n")
