/**
 * O2 Data Solutions — Assessment Data
 * assessment-data.js v1
 * Dados completos do questionário de maturidade analítica
 */
window.O2_ASSESSMENT = {
  title: "Diagnóstico de Maturidade Analítica",
  subtitle: "Avalie em 15 minutos o nível de maturidade analítica da sua empresa",
  scoreRanges: {
    critico:      { min: 0,   max: 3.9, label: "Crítico",          color: "#ef4444", bg: "rgba(239,68,68,0.1)",   icon: "fa-solid fa-triangle-exclamation" },
    desenvolvimento: { min: 4, max: 6.9, label: "Em Desenvolvimento", color: "#f59e0b", bg: "rgba(245,158,11,0.1)", icon: "fa-solid fa-seedling" },
    avancado:     { min: 7,   max: 10,  label: "Avançado",          color: "#22c55e", bg: "rgba(34,197,94,0.1)",  icon: "fa-solid fa-rocket" }
  },
  areas: [
    // ── ÁREA 1: Supply Chain & Compras ──────────────────────────────────────
    {
      id: "supply_chain",
      title: "Supply Chain & Compras",
      icon: "fa-solid fa-truck-fast",
      color: "blue",
      colorHex: "#3b82f6",
      description: "Previsão de demanda, gestão de estoque, compras e logística orientadas a dados",
      questions: [
        { id: "sc_01", text: "Como você avalia a capacidade de previsão de demanda da sua empresa?", hint: "0 = sem previsão formal, apenas intuição | 5 = planilhas com histórico | 10 = forecast automatizado com IA/ML, acurácia >90%" },
        { id: "sc_02", text: "Qual o nível de visibilidade em tempo real do seu estoque?", hint: "0 = sem sistema, contagem manual | 5 = ERP com atualização diária | 10 = visibilidade em tempo real com alertas automáticos" },
        { id: "sc_03", text: "Como é feito o planejamento de compras e reposição de estoque?", hint: "0 = compras por feeling/urgência | 5 = baseado em histórico simples | 10 = algoritmos de reposição automática com ponto de pedido dinâmico" },
        { id: "sc_04", text: "Qual o nível de integração de dados entre fornecedores e seu sistema interno?", hint: "0 = sem integração, tudo manual | 5 = integração parcial via planilhas | 10 = EDI/API em tempo real com todos os fornecedores estratégicos" },
        { id: "sc_05", text: "Como você monitora e analisa o desempenho dos fornecedores?", hint: "0 = sem monitoramento formal | 5 = avaliação periódica manual | 10 = scorecard automatizado com KPIs em tempo real e alertas de desvio" },
        { id: "sc_06", text: "Qual o nível de controle sobre o custo total de aquisição (TCO)?", hint: "0 = apenas preço de compra | 5 = inclui frete e impostos | 10 = TCO completo com custo de capital, armazenagem, obsolescência e risco" },
        { id: "sc_07", text: "Como você identifica e gerencia rupturas de estoque?", hint: "0 = só descobre quando o cliente reclama | 5 = relatório diário manual | 10 = alertas preditivos antes da ruptura com sugestão de ação" },
        { id: "sc_08", text: "Qual o nível de análise de sazonalidade e tendências nos seus processos de compra?", hint: "0 = sem análise de sazonalidade | 5 = ajuste manual por experiência | 10 = modelos estatísticos com decomposição de série temporal" },
        { id: "sc_09", text: "Como você gerencia o estoque de segurança e o giro de estoque?", hint: "0 = sem política definida | 5 = política fixa por categoria | 10 = estoque de segurança dinâmico baseado em variabilidade de demanda e lead time" },
        { id: "sc_10", text: "Qual o nível de rastreabilidade dos produtos ao longo da cadeia?", hint: "0 = sem rastreabilidade | 5 = rastreamento por lote/NF | 10 = rastreabilidade end-to-end em tempo real com IoT/RFID" },
        { id: "sc_11", text: "Como você analisa e otimiza os custos logísticos (frete, armazenagem, last mile)?", hint: "0 = sem análise estruturada | 5 = relatório mensal de custos | 10 = otimização contínua com roteirização inteligente e benchmarking" },
        { id: "sc_12", text: "Qual o nível de automação nos processos de cotação e negociação com fornecedores?", hint: "0 = 100% manual por e-mail/telefone | 5 = portal de cotação básico | 10 = leilão reverso automatizado com análise de risco de fornecedor" },
        { id: "sc_13", text: "Como você mede e reduz o lead time de compras e entrega?", hint: "0 = sem medição formal | 5 = acompanhamento manual por pedido | 10 = monitoramento em tempo real com análise de causa raiz de atrasos" },
        { id: "sc_14", text: "Qual o nível de análise de risco na sua cadeia de suprimentos?", hint: "0 = sem análise de risco | 5 = avaliação qualitativa periódica | 10 = mapa de risco quantitativo com planos de contingência e simulações" },
        { id: "sc_15", text: "Como você utiliza dados para negociar melhores condições com fornecedores?", hint: "0 = negociação sem dados estruturados | 5 = usa histórico de compras | 10 = análise de mercado, benchmarking de preços e poder de barganha baseado em dados" },
        { id: "sc_16", text: "Qual o nível de integração entre Supply Chain e as áreas de Vendas/Comercial?", hint: "0 = silos completamente separados | 5 = reuniões periódicas de S&OP | 10 = S&OP integrado com dados em tempo real e planejamento colaborativo" },
        { id: "sc_17", text: "Como você gerencia produtos com baixo giro, obsoletos ou próximos ao vencimento?", hint: "0 = sem processo definido | 5 = relatório mensal manual | 10 = alertas automáticos com sugestões de ação (promoção, transferência, descarte)" },
        { id: "sc_18", text: "Qual o nível de uso de analytics para otimização do mix de produtos?", hint: "0 = sem análise de mix | 5 = análise ABC básica | 10 = análise de rentabilidade por SKU com recomendação de portfólio baseada em dados" },
        { id: "sc_19", text: "Como você monitora indicadores de qualidade dos produtos recebidos?", hint: "0 = sem controle de qualidade sistemático | 5 = inspeção amostral manual | 10 = controle estatístico de processo (CEP) com alertas automáticos" },
        { id: "sc_20", text: "Qual o nível de maturidade do seu processo de S&OP (Sales & Operations Planning)?", hint: "0 = sem processo de S&OP | 5 = reunião mensal com dados básicos | 10 = S&OP integrado com IA, cenários e tomada de decisão baseada em dados" },
        { id: "sc_21", text: "Como você analisa o impacto financeiro das decisões de estoque (capital de giro)?", hint: "0 = sem análise financeira de estoque | 5 = relatório mensal de valor de estoque | 10 = simulação de impacto no capital de giro com otimização automática" },
        { id: "sc_22", text: "Qual o nível de uso de dados externos (clima, câmbio, commodities) no planejamento?", hint: "0 = sem uso de dados externos | 5 = acompanhamento manual de variáveis-chave | 10 = integração automática de dados externos nos modelos de previsão" }
      ]
    },

    // ── ÁREA 2: Inteligência Comercial & RevOps ──────────────────────────────
    {
      id: "comercial",
      title: "Inteligência Comercial & RevOps",
      icon: "fa-solid fa-chart-line",
      color: "purple",
      colorHex: "#8b5cf6",
      description: "Funil de vendas, forecast de receita, churn, CAC/LTV e operações de receita",
      questions: [
        { id: "com_01", text: "Como você monitora e analisa o funil de vendas em tempo real?", hint: "0 = sem funil estruturado | 5 = CRM básico com relatórios manuais | 10 = funil automatizado com análise preditiva de conversão por etapa" },
        { id: "com_02", text: "Qual o nível de segmentação de clientes baseada em dados?", hint: "0 = sem segmentação | 5 = segmentação por porte/setor | 10 = segmentação comportamental com RFM, CLV e propensão de compra" },
        { id: "com_03", text: "Como você mede e analisa o Custo de Aquisição de Clientes (CAC) por canal?", hint: "0 = sem medição de CAC | 5 = CAC total calculado mensalmente | 10 = CAC por canal, campanha e segmento com análise de payback" },
        { id: "com_04", text: "Qual o nível de análise do Lifetime Value (LTV) dos seus clientes?", hint: "0 = sem análise de LTV | 5 = LTV histórico calculado | 10 = LTV preditivo por segmento com estratégias de maximização" },
        { id: "com_05", text: "Como você identifica oportunidades de cross-sell e upsell?", hint: "0 = sem processo estruturado | 5 = baseado em experiência do vendedor | 10 = recomendações automáticas baseadas em análise de cesta e comportamento" },
        { id: "com_06", text: "Qual o nível de previsão de receita (forecast de vendas)?", hint: "0 = sem forecast formal | 5 = meta top-down com ajuste manual | 10 = forecast bottom-up com modelos estatísticos e acurácia monitorada" },
        { id: "com_07", text: "Como você analisa e reduz o churn (perda de clientes)?", hint: "0 = sem análise de churn | 5 = relatório mensal de cancelamentos | 10 = modelo preditivo de churn com intervenção proativa antes da perda" },
        { id: "com_08", text: "Qual o nível de integração entre CRM, marketing e dados financeiros?", hint: "0 = sistemas completamente separados | 5 = integração parcial manual | 10 = plataforma unificada com visão 360° do cliente em tempo real" },
        { id: "com_09", text: "Como você mede o ROI das campanhas de marketing e prospecção?", hint: "0 = sem medição de ROI | 5 = análise de custo por lead | 10 = atribuição multi-touch com ROI por canal, campanha e segmento" },
        { id: "com_10", text: "Qual o nível de personalização das abordagens comerciais baseada em dados?", hint: "0 = abordagem genérica para todos | 5 = segmentação básica por perfil | 10 = personalização em escala com IA, conteúdo e timing otimizados" },
        { id: "com_11", text: "Como você analisa a performance individual e coletiva do time de vendas?", hint: "0 = sem análise estruturada | 5 = relatório mensal de metas | 10 = dashboard em tempo real com coaching baseado em dados e benchmarking" },
        { id: "com_12", text: "Qual o nível de análise de precificação e elasticidade de preço?", hint: "0 = preço fixo sem análise | 5 = análise de margem por produto | 10 = precificação dinâmica com análise de elasticidade e otimização de margem" },
        { id: "com_13", text: "Como você identifica e prioriza os leads com maior potencial de conversão?", hint: "0 = sem priorização formal | 5 = qualificação manual por critérios | 10 = lead scoring automático com IA e priorização dinâmica" },
        { id: "com_14", text: "Qual o nível de análise do ciclo de vendas e tempo de fechamento?", hint: "0 = sem análise de ciclo | 5 = tempo médio calculado | 10 = análise de fatores que aceleram/retardam o fechamento com ações prescritivas" },
        { id: "com_15", text: "Como você monitora a satisfação e NPS dos clientes?", hint: "0 = sem medição formal | 5 = pesquisa anual de satisfação | 10 = NPS contínuo com análise de texto, alertas e ações automáticas" },
        { id: "com_16", text: "Qual o nível de análise de mercado e inteligência competitiva?", hint: "0 = sem monitoramento de mercado | 5 = acompanhamento manual de concorrentes | 10 = inteligência competitiva automatizada com alertas e análise de posicionamento" },
        { id: "com_17", text: "Como você analisa a rentabilidade por cliente, produto e canal de venda?", hint: "0 = sem análise de rentabilidade | 5 = margem bruta por produto | 10 = P&L por cliente/canal com análise de contribuição e decisões de portfólio" },
        { id: "com_18", text: "Qual o nível de automação do processo de follow-up e nutrição de leads?", hint: "0 = follow-up 100% manual | 5 = e-mail marketing básico | 10 = automação completa com sequências personalizadas e gatilhos comportamentais" },
        { id: "com_19", text: "Como você utiliza dados para definir territórios e cotas de vendas?", hint: "0 = definição subjetiva | 5 = baseado em histórico simples | 10 = otimização de territórios e cotas com análise de potencial de mercado" },
        { id: "com_20", text: "Qual o nível de análise de cohort e retenção de clientes?", hint: "0 = sem análise de cohort | 5 = taxa de retenção calculada | 10 = análise de cohort completa com identificação de padrões e estratégias de retenção" },
        { id: "com_21", text: "Como você mede e otimiza a velocidade do pipeline de vendas?", hint: "0 = sem medição de velocidade | 5 = tempo por etapa calculado | 10 = análise de gargalos com ações automáticas para acelerar o pipeline" },
        { id: "com_22", text: "Qual o nível de uso de dados para expansão e entrada em novos mercados?", hint: "0 = expansão por intuição | 5 = análise básica de mercado | 10 = análise de potencial de mercado com dados demográficos, competitivos e de propensão" }
      ]
    },

    // ── ÁREA 3: Crédito & Risco ──────────────────────────────────────────────
    {
      id: "credito_risco",
      title: "Crédito & Risco",
      icon: "fa-solid fa-shield-halved",
      color: "red",
      colorHex: "#ef4444",
      description: "Análise de crédito, scorecard, cobrança, fraude e gestão de risco da carteira",
      questions: [
        { id: "cr_01", text: "Como é feita a análise de crédito para novos clientes?", hint: "0 = sem análise formal, crédito por confiança | 5 = consulta a bureaus + análise manual | 10 = scorecard automatizado com múltiplas variáveis e decisão em tempo real" },
        { id: "cr_02", text: "Qual o nível de automação no processo de concessão de crédito?", hint: "0 = 100% manual e demorado | 5 = processo semi-automatizado | 10 = decisão automática em segundos com alçadas dinâmicas" },
        { id: "cr_03", text: "Como você monitora o risco da carteira de crédito em tempo real?", hint: "0 = sem monitoramento contínuo | 5 = relatório mensal de inadimplência | 10 = dashboard em tempo real com alertas de deterioração e análise de concentração" },
        { id: "cr_04", text: "Qual o nível de uso de modelos preditivos para identificar clientes com risco de inadimplência?", hint: "0 = sem modelos preditivos | 5 = regras simples baseadas em atraso | 10 = modelo de propensão à inadimplência com intervenção proativa antes do vencimento" },
        { id: "cr_05", text: "Como você segmenta e prioriza a régua de cobrança?", hint: "0 = cobrança genérica para todos | 5 = segmentação por dias de atraso | 10 = régua personalizada por perfil de risco, comportamento e propensão de pagamento" },
        { id: "cr_06", text: "Qual o nível de análise de fraude nos processos de crédito e pagamento?", hint: "0 = sem análise de fraude | 5 = regras básicas de detecção | 10 = modelos de detecção de fraude em tempo real com análise comportamental" },
        { id: "cr_07", text: "Como você calcula e monitora as provisões para devedores duvidosos (PDD)?", hint: "0 = provisão fixa por percentual | 5 = provisão por faixa de atraso | 10 = provisão dinâmica baseada em modelos de perda esperada (IFRS 9/ECL)" },
        { id: "cr_08", text: "Qual o nível de integração entre dados de crédito e dados operacionais do cliente?", hint: "0 = dados completamente separados | 5 = integração manual periódica | 10 = visão 360° do cliente com dados financeiros, operacionais e comportamentais integrados" },
        { id: "cr_09", text: "Como você analisa e otimiza o limite de crédito por cliente?", hint: "0 = limite fixo sem revisão | 5 = revisão anual manual | 10 = limite dinâmico com revisão automática baseada em comportamento e capacidade de pagamento" },
        { id: "cr_10", text: "Qual o nível de análise de concentração de risco na carteira?", hint: "0 = sem análise de concentração | 5 = análise por setor/cliente | 10 = análise de correlação e stress test com limites de concentração automatizados" },
        { id: "cr_11", text: "Como você mede a eficiência e o custo do processo de cobrança?", hint: "0 = sem medição de eficiência | 5 = taxa de recuperação calculada | 10 = análise de custo-benefício por canal de cobrança com otimização de mix" },
        { id: "cr_12", text: "Qual o nível de uso de dados alternativos na análise de crédito?", hint: "0 = apenas dados tradicionais | 5 = alguns dados alternativos manualmente | 10 = integração de múltiplas fontes de dados alternativos em modelos de crédito" },
        { id: "cr_13", text: "Como você gerencia o risco de contraparte em operações B2B?", hint: "0 = sem gestão formal | 5 = análise financeira básica | 10 = monitoramento contínuo com alertas de deterioração e análise de cadeia de fornecimento" },
        { id: "cr_14", text: "Qual o nível de automação nos processos de recuperação de crédito?", hint: "0 = recuperação 100% manual | 5 = automação parcial de comunicações | 10 = estratégia de recuperação totalmente automatizada com IA e múltiplos canais" },
        { id: "cr_15", text: "Como você analisa o impacto das políticas de crédito nos resultados financeiros?", hint: "0 = sem análise de impacto | 5 = análise de inadimplência vs. receita | 10 = simulação de cenários com análise de trade-off entre crescimento e risco" },
        { id: "cr_16", text: "Qual o nível de conformidade e auditabilidade dos processos de crédito?", hint: "0 = sem trilha de auditoria | 5 = registro manual de decisões | 10 = auditoria completa automatizada com explicabilidade dos modelos (XAI)" },
        { id: "cr_17", text: "Como você monitora e gerencia o risco operacional nos processos financeiros?", hint: "0 = sem gestão de risco operacional | 5 = controles básicos documentados | 10 = framework de risco operacional com KRIs automatizados e planos de contingência" },
        { id: "cr_18", text: "Qual o nível de análise de vintage e safra da carteira de crédito?", hint: "0 = sem análise de vintage | 5 = análise básica por período de concessão | 10 = análise de safra completa com identificação de padrões e ajuste de políticas" },
        { id: "cr_19", text: "Como você utiliza dados para precificar o risco de crédito (spread/taxa)?", hint: "0 = taxa única para todos | 5 = faixas de taxa por perfil | 10 = precificação baseada em risco (risk-based pricing) com modelos de perda esperada" },
        { id: "cr_20", text: "Qual o nível de monitoramento de variáveis macroeconômicas no risco da carteira?", hint: "0 = sem monitoramento macro | 5 = acompanhamento manual de indicadores | 10 = stress test automatizado com cenários macroeconômicos e impacto na carteira" },
        { id: "cr_21", text: "Como você gerencia o risco de liquidez e o fluxo de caixa projetado?", hint: "0 = sem projeção de fluxo de caixa | 5 = projeção mensal manual | 10 = projeção dinâmica com análise de cenários e alertas de liquidez" }
      ]
    },

    // ── ÁREA 4: Dados & Machine Learning ────────────────────────────────────
    {
      id: "dados_ml",
      title: "Dados & Machine Learning",
      icon: "fa-solid fa-brain",
      color: "indigo",
      colorHex: "#6366f1",
      description: "Infraestrutura de dados, governança, modelos de ML/IA e cultura data-driven",
      questions: [
        { id: "ml_01", text: "Como você avalia a qualidade e confiabilidade dos dados da sua empresa?", hint: "0 = dados inconsistentes, sem confiança | 5 = qualidade razoável com validações manuais | 10 = pipeline de qualidade automatizado com SLAs de dados definidos" },
        { id: "ml_02", text: "Qual o nível de centralização e integração das fontes de dados?", hint: "0 = dados em silos, sem integração | 5 = integração parcial com ETL manual | 10 = data warehouse/lakehouse centralizado com ingestão automatizada de todas as fontes" },
        { id: "ml_03", text: "Como você gerencia a governança e o catálogo de dados?", hint: "0 = sem governança formal | 5 = documentação básica de algumas fontes | 10 = data catalog completo com linhagem, glossário e políticas de acesso automatizadas" },
        { id: "ml_04", text: "Qual o nível de uso de modelos de Machine Learning em produção?", hint: "0 = sem uso de ML | 5 = 1-2 modelos em produção | 10 = múltiplos modelos em produção com MLOps, monitoramento e retreinamento automático" },
        { id: "ml_05", text: "Como você gerencia o ciclo de vida dos modelos de ML (MLOps)?", hint: "0 = sem processo de MLOps | 5 = versionamento básico de modelos | 10 = pipeline completo de MLOps com CI/CD, monitoramento de drift e retreinamento automático" },
        { id: "ml_06", text: "Qual o nível de maturidade da infraestrutura de dados (cloud, on-premise)?", hint: "0 = infraestrutura legada, sem escalabilidade | 5 = migração parcial para cloud | 10 = arquitetura moderna de dados (data mesh/lakehouse) totalmente escalável" },
        { id: "ml_07", text: "Como você garante a privacidade e segurança dos dados (LGPD/GDPR)?", hint: "0 = sem controles de privacidade | 5 = políticas básicas documentadas | 10 = framework completo de privacidade com anonimização, consentimento e auditoria automática" },
        { id: "ml_08", text: "Qual o nível de democratização do acesso a dados na empresa?", hint: "0 = dados acessíveis apenas para TI | 5 = alguns relatórios para gestores | 10 = self-service analytics para todos os usuários com governança adequada" },
        { id: "ml_09", text: "Como você mede e monitora a performance dos modelos de ML em produção?", hint: "0 = sem monitoramento de modelos | 5 = verificação manual periódica | 10 = monitoramento automático de drift, performance e alertas de degradação" },
        { id: "ml_10", text: "Qual o nível de uso de IA generativa e LLMs nos processos de negócio?", hint: "0 = sem uso de IA generativa | 5 = experimentação pontual | 10 = IA generativa integrada em processos críticos com governança e avaliação de ROI" },
        { id: "ml_11", text: "Como você gerencia e documenta os experimentos de ciência de dados?", hint: "0 = sem documentação de experimentos | 5 = documentação manual em planilhas | 10 = plataforma de experiment tracking (MLflow/W&B) com reprodutibilidade garantida" },
        { id: "ml_12", text: "Qual o nível de capacitação da equipe em dados e analytics?", hint: "0 = sem equipe de dados | 5 = 1-2 analistas com habilidades básicas | 10 = equipe multidisciplinar com cientistas de dados, engenheiros e analistas especializados" },
        { id: "ml_13", text: "Como você garante a explicabilidade e interpretabilidade dos modelos de ML?", hint: "0 = modelos caixa-preta sem explicação | 5 = explicações básicas para stakeholders | 10 = XAI implementado com SHAP/LIME e documentação de decisões automatizadas" },
        { id: "ml_14", text: "Qual o nível de automação dos pipelines de dados (ETL/ELT)?", hint: "0 = ETL manual e frágil | 5 = pipelines básicos com agendamento | 10 = pipelines modernos com orquestração (Airflow/Prefect), testes e monitoramento" },
        { id: "ml_15", text: "Como você mede o ROI e o impacto de negócio dos projetos de dados e ML?", hint: "0 = sem medição de ROI | 5 = estimativa qualitativa | 10 = framework de medição de impacto com KPIs de negócio vinculados a cada iniciativa de dados" },
        { id: "ml_16", text: "Qual o nível de uso de dados em tempo real (streaming) nos processos?", hint: "0 = apenas dados batch/históricos | 5 = alguns casos de uso em near real-time | 10 = arquitetura de streaming (Kafka/Flink) para casos de uso críticos" },
        { id: "ml_17", text: "Como você gerencia a estratégia de dados e o roadmap analítico?", hint: "0 = sem estratégia formal de dados | 5 = roadmap básico definido | 10 = estratégia de dados alinhada ao negócio com OKRs, priorização e revisão trimestral" },
        { id: "ml_18", text: "Qual o nível de uso de feature stores e reutilização de features de ML?", hint: "0 = sem reutilização de features | 5 = algumas features compartilhadas | 10 = feature store centralizado com catálogo, versionamento e reutilização entre modelos" },
        { id: "ml_19", text: "Como você testa e valida modelos antes de colocá-los em produção?", hint: "0 = sem processo de validação | 5 = validação manual básica | 10 = framework completo de testes (A/B, shadow mode, champion-challenger) com critérios de aprovação" },
        { id: "ml_20", text: "Qual o nível de integração entre dados e sistemas de decisão operacional?", hint: "0 = dados e operações completamente separados | 5 = relatórios para suporte à decisão | 10 = decisões automatizadas em tempo real com dados integrados nos sistemas operacionais" },
        { id: "ml_21", text: "Como você gerencia a cultura data-driven na organização?", hint: "0 = cultura baseada em intuição | 5 = alguns líderes usam dados | 10 = cultura data-driven consolidada com treinamentos, incentivos e decisões baseadas em dados em todos os níveis" }
      ]
    },

    // ── ÁREA 5: Automação, RPA & Alertas ────────────────────────────────────
    {
      id: "automacao",
      title: "Automação, RPA & Alertas",
      icon: "fa-solid fa-robot",
      color: "green",
      colorHex: "#22c55e",
      description: "Automação de processos, RPA, integrações e sistemas de alertas inteligentes",
      questions: [
        { id: "aut_01", text: "Qual o percentual de processos repetitivos que já foram automatizados?", hint: "0 = 0%, tudo manual | 5 = 20-40% automatizados | 10 = >80% dos processos repetitivos automatizados com RPA/scripts" },
        { id: "aut_02", text: "Como você identifica e prioriza oportunidades de automação?", hint: "0 = sem processo de identificação | 5 = levantamento ad-hoc | 10 = processo sistemático de mapeamento com análise de ROI e priorização por impacto" },
        { id: "aut_03", text: "Qual o nível de automação nos processos de geração e distribuição de relatórios?", hint: "0 = relatórios 100% manuais | 5 = alguns relatórios agendados | 10 = todos os relatórios gerados e distribuídos automaticamente com personalização por perfil" },
        { id: "aut_04", text: "Como você gerencia e monitora os robôs e automações em produção?", hint: "0 = sem monitoramento | 5 = verificação manual periódica | 10 = orquestração centralizada com monitoramento em tempo real, alertas e recuperação automática" },
        { id: "aut_05", text: "Qual o nível de automação nos processos de integração entre sistemas (APIs/ETL)?", hint: "0 = integrações manuais via planilhas | 5 = algumas integrações automatizadas | 10 = arquitetura de integração completa com APIs, webhooks e event-driven" },
        { id: "aut_06", text: "Como você utiliza alertas inteligentes para monitorar KPIs críticos do negócio?", hint: "0 = sem sistema de alertas | 5 = alertas básicos por e-mail | 10 = alertas inteligentes com detecção de anomalias, contexto e sugestão de ação" },
        { id: "aut_07", text: "Qual o nível de automação nos processos de cobrança e comunicação com clientes?", hint: "0 = comunicação 100% manual | 5 = e-mail marketing básico | 10 = jornadas automatizadas omnichannel com personalização e gatilhos comportamentais" },
        { id: "aut_08", text: "Como você automatiza o processo de coleta e consolidação de dados de múltiplas fontes?", hint: "0 = coleta manual de dados | 5 = alguns scripts de coleta | 10 = pipeline de ingestão automatizado com validação, transformação e carga em tempo real" },
        { id: "aut_09", text: "Qual o nível de uso de chatbots e assistentes virtuais nos processos?", hint: "0 = sem chatbots | 5 = chatbot básico de FAQ | 10 = assistentes virtuais com IA para atendimento, vendas e suporte com integração aos sistemas" },
        { id: "aut_10", text: "Como você automatiza o processo de precificação e atualização de preços?", hint: "0 = precificação manual | 5 = atualização periódica semi-automática | 10 = precificação dinâmica automatizada com regras de negócio e aprovação por alçada" },
        { id: "aut_11", text: "Qual o nível de automação nos processos de compras e aprovações?", hint: "0 = aprovações 100% manuais | 5 = workflow básico de aprovação | 10 = automação completa com alçadas dinâmicas, integração ERP e auditoria automática" },
        { id: "aut_12", text: "Como você monitora e alerta sobre anomalias nos dados e processos?", hint: "0 = sem detecção de anomalias | 5 = regras fixas de threshold | 10 = detecção de anomalias com ML, análise de causa raiz e alertas contextualizados" },
        { id: "aut_13", text: "Qual o nível de automação nos processos de RH (folha, ponto, recrutamento)?", hint: "0 = processos manuais | 5 = sistema básico de RH | 10 = automação completa com analytics de pessoas, predição de turnover e recrutamento assistido por IA" },
        { id: "aut_14", text: "Como você automatiza o monitoramento de concorrentes e mercado?", hint: "0 = monitoramento manual | 5 = algumas ferramentas de monitoramento | 10 = web scraping automatizado com análise de sentimento e alertas de mudanças relevantes" },
        { id: "aut_15", text: "Qual o nível de automação nos processos de faturamento e conciliação financeira?", hint: "0 = faturamento manual | 5 = emissão automatizada básica | 10 = faturamento, conciliação e fechamento financeiro totalmente automatizados" },
        { id: "aut_16", text: "Como você gerencia e documenta os processos automatizados (manutenção e evolução)?", hint: "0 = sem documentação | 5 = documentação básica | 10 = documentação completa com versionamento, testes automatizados e processo de change management" },
        { id: "aut_17", text: "Qual o nível de automação no processo de onboarding de clientes e parceiros?", hint: "0 = onboarding 100% manual | 5 = alguns formulários digitais | 10 = onboarding digital completo com validações automáticas, KYC e integração de sistemas" },
        { id: "aut_18", text: "Como você mede o ROI e os ganhos de produtividade das automações implementadas?", hint: "0 = sem medição de ROI | 5 = estimativa de horas economizadas | 10 = framework de medição com KPIs de produtividade, qualidade e custo por processo" },
        { id: "aut_19", text: "Qual o nível de automação nos processos de compliance e auditoria?", hint: "0 = compliance manual | 5 = checklist digital | 10 = monitoramento contínuo de compliance com alertas automáticos e relatórios regulatórios automatizados" },
        { id: "aut_20", text: "Como você utiliza automação para melhorar a experiência do cliente (CX)?", hint: "0 = sem automação de CX | 5 = automações básicas de comunicação | 10 = jornada do cliente totalmente orquestrada com personalização em tempo real" },
        { id: "aut_21", text: "Qual o nível de integração entre automações e sistemas de BI/Analytics?", hint: "0 = automações e analytics separados | 5 = alguns dados de automação no BI | 10 = feedback loop completo entre automações e analytics para melhoria contínua" }
      ]
    },

    // ── ÁREA 6: Dashboards & Analytics ──────────────────────────────────────
    {
      id: "dashboards",
      title: "Dashboards & Analytics",
      icon: "fa-solid fa-chart-pie",
      color: "cyan",
      colorHex: "#06b6d4",
      description: "Qualidade dos dashboards, self-service analytics, KPIs e cultura analítica",
      questions: [
        { id: "dash_01", text: "Como você avalia a qualidade e usabilidade dos dashboards atuais?", hint: "0 = sem dashboards | 5 = dashboards básicos em planilhas | 10 = dashboards interativos, responsivos e com UX otimizada para cada perfil de usuário" },
        { id: "dash_02", text: "Qual o nível de atualização e frequência dos dados nos dashboards?", hint: "0 = dados desatualizados (semanas/meses) | 5 = atualização diária | 10 = dados em tempo real ou near real-time com SLA de atualização monitorado" },
        { id: "dash_03", text: "Como você garante que os KPIs nos dashboards refletem as prioridades estratégicas?", hint: "0 = KPIs definidos sem alinhamento estratégico | 5 = revisão anual de KPIs | 10 = OKRs e KPIs alinhados à estratégia com revisão trimestral e cascata para times" },
        { id: "dash_04", text: "Qual o nível de self-service analytics na empresa?", hint: "0 = apenas TI cria relatórios | 5 = alguns usuários avançados | 10 = self-service analytics democratizado com treinamento, governança e suporte" },
        { id: "dash_05", text: "Como você mede a adoção e o uso efetivo dos dashboards pelos usuários?", hint: "0 = sem medição de adoção | 5 = feedback qualitativo | 10 = analytics de uso dos dashboards com identificação de usuários ativos e conteúdo mais acessado" },
        { id: "dash_06", text: "Qual o nível de análise exploratória e descoberta de insights nos dados?", hint: "0 = sem análise exploratória | 5 = análises ad-hoc ocasionais | 10 = processo estruturado de discovery com ferramentas de exploração e compartilhamento de insights" },
        { id: "dash_07", text: "Como você gerencia o ciclo de vida dos relatórios e dashboards?", hint: "0 = sem processo de gestão | 5 = processo informal | 10 = governance de conteúdo analítico com ownership, SLA de manutenção e processo de descontinuação" },
        { id: "dash_08", text: "Qual o nível de análise preditiva e prescritiva nos dashboards?", hint: "0 = apenas análise descritiva (o que aconteceu) | 5 = algumas análises de tendência | 10 = análise preditiva (o que vai acontecer) e prescritiva (o que fazer) integradas" },
        { id: "dash_09", text: "Como você garante a consistência e confiabilidade das métricas entre diferentes relatórios?", hint: "0 = métricas inconsistentes entre relatórios | 5 = algumas métricas padronizadas | 10 = single source of truth com definições únicas e certificação de métricas" },
        { id: "dash_10", text: "Qual o nível de personalização dos dashboards por perfil de usuário?", hint: "0 = dashboard único para todos | 5 = alguns dashboards por área | 10 = dashboards personalizados por papel, nível hierárquico e preferências individuais" },
        { id: "dash_11", text: "Como você utiliza storytelling com dados para comunicar insights aos stakeholders?", hint: "0 = dados brutos sem narrativa | 5 = apresentações com gráficos básicos | 10 = data storytelling estruturado com narrativa, contexto e recomendações de ação" },
        { id: "dash_12", text: "Qual o nível de análise de causa raiz (root cause analysis) nos processos?", hint: "0 = sem análise de causa raiz | 5 = análise manual quando há problema | 10 = análise de causa raiz automatizada com drill-down e identificação de fatores contribuintes" },
        { id: "dash_13", text: "Como você monitora e analisa a experiência do cliente (CX) com dados?", hint: "0 = sem analytics de CX | 5 = NPS e satisfação básicos | 10 = analytics completo de jornada do cliente com análise de sentimento e correlação com resultados" },
        { id: "dash_14", text: "Qual o nível de análise de benchmarking interno e externo?", hint: "0 = sem benchmarking | 5 = comparação com período anterior | 10 = benchmarking contínuo com dados de mercado, peers e melhores práticas do setor" },
        { id: "dash_15", text: "Como você utiliza análise de coorte e segmentação avançada?", hint: "0 = sem análise de coorte | 5 = segmentação básica | 10 = análise de coorte multidimensional com identificação de padrões e ações personalizadas" },
        { id: "dash_16", text: "Qual o nível de análise geoespacial e territorial nos dados?", hint: "0 = sem análise geográfica | 5 = mapas básicos de distribuição | 10 = análise geoespacial avançada com clustering, heatmaps e otimização territorial" },
        { id: "dash_17", text: "Como você gerencia e analisa dados não estruturados (textos, imagens, áudios)?", hint: "0 = sem análise de dados não estruturados | 5 = análise manual de textos | 10 = NLP/Computer Vision para extração automática de insights de dados não estruturados" },
        { id: "dash_18", text: "Qual o nível de análise de simulação e cenários (what-if analysis)?", hint: "0 = sem análise de cenários | 5 = simulações manuais em planilhas | 10 = ferramentas de simulação integradas com modelos de negócio e análise de sensibilidade" },
        { id: "dash_19", text: "Como você mede e analisa a produtividade e eficiência operacional com dados?", hint: "0 = sem analytics operacional | 5 = KPIs básicos de produtividade | 10 = analytics operacional em tempo real com benchmarking e identificação de oportunidades" },
        { id: "dash_20", text: "Qual o nível de integração entre analytics e processos de tomada de decisão?", hint: "0 = decisões tomadas sem dados | 5 = dados consultados ocasionalmente | 10 = dados integrados em todos os processos de decisão com frameworks de decision intelligence" },
        { id: "dash_21", text: "Como você garante a acessibilidade e disponibilidade dos dashboards (mobile, offline)?", hint: "0 = apenas desktop, sem mobile | 5 = acesso mobile básico | 10 = dashboards responsivos, com app mobile, modo offline e notificações push" },
        { id: "dash_22", text: "Qual o nível de análise de atribuição e impacto das iniciativas de negócio?", hint: "0 = sem análise de atribuição | 5 = análise básica de correlação | 10 = modelos de atribuição causal com análise de impacto incremental e experimentos controlados" }
      ]
    }
  ]
};
