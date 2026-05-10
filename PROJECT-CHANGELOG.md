# O2 Data Solutions — Project Changelog

**Projeto:** o2-landpage  
**Stack:** FastAPI + SQLite + Tailwind CSS + Brevo SMTP  
**URL:** https://o2data.com.br  

---

## Funcionalidades e Recursos (v2.0.0 — baseline)

### Frontend
- Landing page B2B completa (`index.html`) com partials modulares
- Dark/light mode com persistência em cookie
- Navbar responsiva com scroll effect
- Seções: Hero, Logos, Serviços, Problemas, Metodologia, Métricas, CTA, Footer
- Cookie consent banner (LGPD)
- WAF challenge page

### Assessment de Maturidade Analítica (`avaliacao.html`)
- Wizard 4 passos: Perfil → Área → Questionário → Resultado
- 6 áreas avaliadas: Supply Chain & Compras, Inteligência Comercial & RevOps, Crédito & Risco, Dados & Machine Learning, Automação RPA & Alertas, Dashboards & Analytics
- 128 questões no total (20-22 por área), escala 0-10 com slider
- Score de maturidade: Crítico (0-3.9), Em Desenvolvimento (4-6.9), Avançado (7-10)
- Resultado com círculo SVG de progresso, barras de score, recomendações
- Formulário de perfil: nome, email, empresa, cargo, setor, funcionários, faturamento, urgência, orçamento, desafio principal

### Backend (server.py v2.0.0)
- FastAPI com lifespan management
- WAF: detecção de SQLi, XSS, scanner bots, path traversal, caminhos suspeitos
- Rate limiting configurável com auto-ban de IPs
- IP ban persistente em SQLite (bans.db)
- Visitor tracking: cookie persistente, UA parser, logs em SQLite/YAML/JSON/MD
- Email queue thread-safe (max 500 items) com worker não-bloqueante
- Event queue para DB writes assíncronos (max 5000 items)
- Rotas: GET /, POST /api/contact, POST /api/assessment, POST /api/event, GET /api/metrics, GET /api/health, GET /api/bans, DELETE /api/bans/{ip}
- Hot reload (exclui data/, logs/, __pycache__)
- KPI ticker em tempo real (colorama + rich)
- Security headers em todas as respostas

### Banco de Dados (SQLite)
- `o2_metrics.db`: requests, leads, kpis, waf_events, assessments
- `visitors.db`: visitors, page_views, events
- `bans.db`: ip_bans

### Configuração (YAML)
- app.yaml, email.yaml, server.yaml, security.yaml, performance.yaml, consent.yaml, visitors.yaml, assessment.yaml

### Email (Brevo SMTP)
- Email de lead para equipe interna (2 destinatários)
- Email de assessment para equipe interna + cópia para cliente
- HTML responsivo com gradient azul-roxo

---

## v2.1.0 — 2026-05-09

### Email System — Upgrade Completo

**`send_email_sync` (email de lead interno):**
- Redesign completo: dark theme premium (#060b18 background)
- Header com gradient azul-roxo e badge de ícone
- Dados do lead em cards empilhados com labels uppercase
- Bloco de mensagem com border-left colorida (quando preenchida)
- CTAs WhatsApp (verde) e E-mail (azul) lado a lado
- Footer minimalista dark

**`send_assessment_email_sync` (email de assessment):**
- Dois emails distintos: interno (dark) e cliente (light)
- **Email interno (dark):**
  - Score badge com background colorido por nível (crítico/desenvolvimento/avançado)
  - Perfil completo: nome, empresa, cargo, setor, funcionários, faturamento, urgência, budget
  - Scores por questão com **nomes completos das dimensões** (via `email_data.QUESTION_LABELS`)
  - Barras de progresso coloridas por score (vermelho/amarelo/verde)
  - Bloco de recomendações completo por nível e área (via `email_data.RECOMMENDATIONS`)
  - CTAs de resposta (WhatsApp + e-mail)
- **Email cliente (light):**
  - Saudação personalizada com nome e empresa
  - Score com barra de progresso visual
  - Badge da área avaliada com cor específica por área
  - Scores por dimensão com nomes legíveis
  - Recomendações prioritárias formatadas em cards
  - CTA para agendar diagnóstico completo via WhatsApp
  - Footer com aviso de opt-out

**Novo módulo `email_data.py`:**
- `AREA_LABELS`: nomes completos das 6 áreas
- `AREA_ICONS_EMOJI`: ícones por área
- `AREA_COLORS`: cores hex por área
- `QUESTION_LABELS`: 128 labels de questões (todos os IDs sc_01..sc_22, com_01..com_22, etc.)
- `RECOMMENDATIONS`: recomendações por área × nível (critico/desenvolvimento/avancado), 6 por combinação

**Novo módulo `email_helpers.py`:**
- `score_rows_internal()`: HTML de barras de score para email dark
- `score_rows_client()`: HTML de barras de score para email light
- `recs_internal()`: HTML de recomendações para email dark
- `recs_client()`: HTML de recomendações para email light

**Limpeza de arquivos temporários:**
- Removidos: `_fix_email.py`, `_s1_build_email_data.py`, `_s2_build_new_email_func.py` (placeholders vazios)

**Versão incrementada:** 2.0.0 → 2.1.0 (app.yaml, server.py)
