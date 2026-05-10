/**
 * O2 Data Solutions — calculator.js v2
 * Calculadora de ROI Rica por Setor e Problema
 */
(function(){
  var _sector = null;
  var _prob   = null;

  // ── Helpers de formatação ──────────────────────────────────
  function _fmt(v) {
    if (v >= 1000000) return 'R$ ' + (v/1000000).toFixed(1).replace('.',',') + 'M';
    if (v >= 1000)    return 'R$ ' + Math.round(v/1000).toLocaleString('pt-BR') + 'k';
    return 'R$ ' + Math.round(v).toLocaleString('pt-BR');
  }
  function _fmtFull(v) { return 'R$ ' + Math.round(v).toLocaleString('pt-BR'); }
  function _pct(v)     { return v.toFixed(1).replace('.',',') + '%'; }
  function _num(v)     { return Math.round(v).toLocaleString('pt-BR'); }

  // ── Definição de problemas por setor ───────────────────────
  var SECTOR_PROBLEMS = {
    varejo:      ['abandono','estoque','churn','automacao','ticket'],
    industria:   ['producao','estoque_parado','automacao','compras','qualidade'],
    distribuicao:['estoque','estoque_parado','compras','churn','automacao'],
    servicos:    ['churn','automacao','inadimplencia','ticket','funil'],
    importacao:  ['compras','estoque_parado','lead_time','cambio','automacao'],
    agro:        ['estoque_parado','compras','producao','automacao','churn'],
    saude:       ['estoque','automacao','inadimplencia','churn','qualidade'],
    financeiro:  ['inadimplencia','churn','automacao','funil','ticket'],
  };

  var PROBLEM_META = {
    abandono:      { icon:'fa-cart-arrow-down',   color:'#8b5cf6', label:'Abandono de Carrinho',    sub:'Vendas não convertidas' },
    estoque:       { icon:'fa-boxes-stacked',      color:'#3b82f6', label:'Ruptura de Estoque',      sub:'Perdas por falta de produto' },
    churn:         { icon:'fa-user-minus',         color:'#ef4444', label:'Churn de Clientes',       sub:'Perda de receita recorrente' },
    automacao:     { icon:'fa-gears',              color:'#f59e0b', label:'Processos Manuais',       sub:'Custo de retrabalho' },
    ticket:        { icon:'fa-arrow-trend-up',     color:'#22c55e', label:'Ticket Médio Baixo',      sub:'Oportunidade de upsell/cross-sell' },
    producao:      { icon:'fa-industry',           color:'#f97316', label:'Ineficiência na Produção',sub:'Horas paradas e retrabalho' },
    estoque_parado:{ icon:'fa-warehouse',          color:'#eab308', label:'Estoque Parado',          sub:'Capital imobilizado' },
    compras:       { icon:'fa-cart-shopping',      color:'#06b6d4', label:'Compras Ineficientes',    sub:'Custo de aquisição elevado' },
    qualidade:     { icon:'fa-circle-xmark',       color:'#ec4899', label:'Falhas de Qualidade',     sub:'Devoluções e retrabalho' },
    inadimplencia: { icon:'fa-file-invoice-dollar',color:'#ef4444', label:'Inadimplência',           sub:'Perdas na carteira' },
    funil:         { icon:'fa-filter',             color:'#a855f7', label:'Funil Comercial Lento',   sub:'Oportunidades perdidas' },
    lead_time:     { icon:'fa-clock-rotate-left',  color:'#64748b', label:'Lead Time de Importação', sub:'Atrasos e custos extras' },
    cambio:        { icon:'fa-dollar-sign',        color:'#10b981', label:'Exposição Cambial',       sub:'Perdas por variação do câmbio' },
  };

  // ── Definição de campos e cálculos por problema ───────────
  var PROBLEMS = {

    // ── ABANDONO DE CARRINHO ──────────────────────────────────
    abandono: {
      benchmark: 'Benchmark: taxa média de abandono no e-commerce brasileiro é 68-72%. Recuperação com automação e personalização pode reduzir em 20-25%.',
      fields: [
        { id:'fat_mes',     label:'Faturamento médio mensal (R$)',    placeholder:'Ex: 350000',  hint:'Receita bruta de vendas online/mês. PME e-commerce BR: R$ 50k–R$ 500k/mês' },
        { id:'pedidos_mes', label:'Pedidos faturados por mês',        placeholder:'Ex: 1200',    hint:'Pedidos efetivamente pagos. Exclua carrinhos abandonados deste número' },
        { id:'tx_abandono', label:'Taxa de abandono atual (%)',       placeholder:'Ex: 70',      hint:'Média BR: 68-72%. Acima de 75% = crítico. Abaixo de 60% = bom' },
        { id:'margem',      label:'Margem bruta média (%)',           placeholder:'Ex: 40',      hint:'Varejo online: 25-45% | Moda: 50-65% | Eletrônicos: 15-25%' },
        { id:'ticket',      label:'Ticket médio atual (R$)',          placeholder:'Ex: 290',     hint:'Faturamento ÷ pedidos faturados. Média e-commerce BR: R$ 180–R$ 350' },
      ],
      calc: function(v) {
        var fat=v.fat_mes, ped=v.pedidos_mes, tx=v.tx_abandono/100, mg=v.margem/100, tk=v.ticket;
        var carrinhos_total = ped / (1 - tx);
        var carrinhos_perdidos = carrinhos_total * tx;
        var perda_mes = carrinhos_perdidos * tk;
        var perda_ano = perda_mes * 12;
        var margem_perdida_ano = perda_ano * mg;
        var ticket_medio_dia = fat / 30;
        // Ganhos O2: -20% abandono, +10% ticket médio (cross-sell/upsell)
        var tx_alvo = tx * 0.80;
        var ganho_abandono_ano = (tx - tx_alvo) * carrinhos_total * tk * 12 * mg;
        var ganho_ticket_ano   = ped * 12 * tk * 0.10 * mg;
        var ganho_total        = ganho_abandono_ano + ganho_ticket_ano;
        return {
          loss: [
            { label:'Carrinhos perdidos/mês',  value:_num(carrinhos_perdidos),  color:'#8b5cf6', icon:'fa-cart-arrow-down', sub:'sem conversão' },
            { label:'Receita perdida/mês',     value:_fmt(perda_mes),           color:'#ef4444', icon:'fa-money-bill-wave', sub:'em vendas não realizadas' },
            { label:'Margem perdida/ano',      value:_fmt(margem_perdida_ano),  color:'#ef4444', icon:'fa-chart-line-down', sub:'impacto direto no lucro' },
          ],
          gain: [
            { label:'Recuperação de abandono/ano', value:_fmt(ganho_abandono_ano), color:'#22c55e', icon:'fa-cart-plus',        sub:'com -20% de abandono' },
            { label:'Ganho de ticket médio/ano',   value:_fmt(ganho_ticket_ano),   color:'#22c55e', icon:'fa-arrow-trend-up',   sub:'com cross-sell e upsell (+10%)' },
            { label:'Ganho total estimado/ano',    value:_fmt(ganho_total),        color:'#22c55e', icon:'fa-rocket',           sub:'em margem adicional' },
          ],
          timeline: [
            { period:'Dia',  value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',  value:_fmt(ganho_total/12) },
            { period:'Ano',  value:_fmt(ganho_total) },
          ],
          roi: 'Com recuperação de carrinho automatizada, personalização por comportamento e régua de remarketing inteligente, a O2 reduz o abandono em até 20% e aumenta o ticket médio em 10% via cross-sell e upsell. Potencial de ganho: <strong>' + _fmt(ganho_total) + '/ano</strong> em margem adicional.'
        };
      }
    },

    // ── RUPTURA DE ESTOQUE ────────────────────────────────────
    estoque: {
      benchmark: 'Benchmark: ruptura média no varejo BR é 8-12%. A O2 garante até 2% de ruptura em itens-chave com estratégia JIT, giro entre filiais e previsão de demanda com IA.',
      fields: [
        { id:'fat_mes',    label:'Faturamento médio mensal (R$)', placeholder:'Ex: 800000', hint:'Receita bruta mensal. PME distribuidora/varejo: R$ 300k–R$ 5M/mês' },
        { id:'num_sku',    label:'Número de SKUs ativos',         placeholder:'Ex: 3000',   hint:'Produtos com pelo menos 1 venda nos últimos 90 dias. Média PME: 500–8.000 SKUs' },
        { id:'num_dep',    label:'Número de depósitos/filiais',   placeholder:'Ex: 3',      hint:'Pontos físicos de estoque. Mais depósitos = maior potencial de giro entre filiais' },
        { id:'tx_ruptura', label:'Taxa de ruptura atual (%)',     placeholder:'Ex: 9',      hint:'% de pedidos com pelo menos 1 item indisponível. Média BR: 8-12%. Meta O2: ≤2%' },
        { id:'margem',     label:'Margem bruta média (%)',        placeholder:'Ex: 35',     hint:'Varejo: 25-45% | Distribuição: 15-30% | Indústria: 30-50%' },
      ],
      calc: function(v) {
        var fat=v.fat_mes, sku=v.num_sku, dep=v.num_dep, tx=v.tx_ruptura/100, mg=v.margem/100;
        var perda_mes = fat * tx;
        var perda_ano = perda_mes * 12;
        var margem_perdida = perda_ano * mg;
        var tx_alvo = 0.02;
        var ganho_ruptura = fat * (tx - tx_alvo) * 12 * mg;
        var ganho_giro    = fat * 0.05 * 12 * mg; // +5% vendas por melhor disponibilidade
        var ganho_total   = ganho_ruptura + ganho_giro;
        return {
          loss: [
            { label:'Vendas perdidas/mês',    value:_fmt(perda_mes),      color:'#3b82f6', icon:'fa-boxes-stacked',    sub:'por ruptura de estoque' },
            { label:'Perda anual estimada',   value:_fmt(perda_ano),      color:'#ef4444', icon:'fa-triangle-exclamation', sub:'em receita não realizada' },
            { label:'Margem perdida/ano',     value:_fmt(margem_perdida), color:'#ef4444', icon:'fa-money-bill-trend-up',  sub:'impacto direto no lucro' },
          ],
          gain: [
            { label:'Recuperação por -ruptura/ano', value:_fmt(ganho_ruptura), color:'#22c55e', icon:'fa-check-circle',     sub:'de ' + _pct(tx*100) + ' para 2% de ruptura' },
            { label:'Ganho de disponibilidade/ano', value:_fmt(ganho_giro),    color:'#22c55e', icon:'fa-arrow-trend-up',   sub:'+5% vendas por melhor fill rate' },
            { label:'Ganho total estimado/ano',     value:_fmt(ganho_total),   color:'#22c55e', icon:'fa-rocket',           sub:'em margem adicional' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Reduzindo a ruptura de ' + _pct(tx*100) + ' para até 2% com reposição automática, estoque de segurança dinâmico e giro entre os ' + Math.round(dep) + ' depósitos, sua empresa pode recuperar <strong>' + _fmt(ganho_total) + '/ano</strong> em margem. Benchmark O2: 98% de disponibilidade em itens-chave.'
        };
      }
    },

    // ── CHURN DE CLIENTES ─────────────────────────────────────
    churn: {
      benchmark: 'Benchmark: churn médio B2B é 2-5%/mês. A O2 reduz em 20% com modelos preditivos e aumenta ticket médio em 10% com cross-sell/upsell inteligente.',
      fields: [
        { id:'clientes',     label:'Base de clientes ativos',        placeholder:'Ex: 800',   hint:'Clientes com compra nos últimos 12 meses. PME B2B: 100–2.000 clientes ativos' },
        { id:'ticket_medio', label:'Ticket médio mensal (R$)',        placeholder:'Ex: 1500',  hint:'Receita média por cliente/mês. B2B serviços: R$ 500–R$ 5.000 | SaaS: R$ 300–R$ 2.000' },
        { id:'tx_churn',     label:'Taxa de churn mensal (%)',        placeholder:'Ex: 3',     hint:'% de clientes perdidos por mês. Saudável: <2% | Atenção: 2-5% | Crítico: >5%' },
        { id:'ltv_meses',    label:'LTV médio (meses)',               placeholder:'Ex: 18',    hint:'Tempo médio que um cliente fica ativo. B2B: 12-36 meses | SaaS: 18-48 meses' },
        { id:'cac',          label:'CAC médio por cliente (R$)',      placeholder:'Ex: 800',   hint:'Custo total de marketing+vendas ÷ novos clientes. B2B: R$ 500–R$ 5.000' },
      ],
      calc: function(v) {
        var cli=v.clientes, tk=v.ticket_medio, tx=v.tx_churn/100, ltv=v.ltv_meses, cac=v.cac;
        var perdidos_mes = cli * tx;
        var mrr_perdido  = perdidos_mes * tk;
        // LTV destruído: cada cliente perdido leva consigo tk * ltv_meses de receita futura
        // Anualizado = clientes perdidos/mês × LTV por cliente × 12 meses de fluxo
        var ltv_por_cliente   = tk * ltv;
        var ltv_destruido_ano = perdidos_mes * ltv_por_cliente * 12;
        // O2: -20% churn → retém 20% dos clientes que seriam perdidos
        var clientes_retidos_mes = perdidos_mes * 0.20;
        var ganho_retencao = clientes_retidos_mes * ltv_por_cliente * 12;
        // O2: +10% ticket na base ativa (cross-sell/upsell)
        var ganho_upsell   = cli * tk * 0.10 * 12;
        var ganho_total    = ganho_retencao + ganho_upsell;
        return {
          loss: [
            { label:'Clientes perdidos/mês',  value:_num(perdidos_mes),       color:'#ef4444', icon:'fa-user-minus',       sub:'em média por mês' },
            { label:'MRR perdido/mês',        value:_fmt(mrr_perdido),        color:'#ef4444', icon:'fa-money-bill-wave',  sub:'receita recorrente perdida' },
            { label:'LTV destruído/ano',      value:_fmt(ltv_destruido_ano),  color:'#ef4444', icon:'fa-chart-line-down',  sub:'valor de vida perdido' },
          ],
          gain: [
            { label:'Ganho de retenção/ano',  value:_fmt(ganho_retencao), color:'#22c55e', icon:'fa-user-check',      sub:'-20% churn com modelos preditivos' },
            { label:'Ganho de upsell/ano',    value:_fmt(ganho_upsell),   color:'#22c55e', icon:'fa-arrow-trend-up',  sub:'+10% ticket médio com cross-sell' },
            { label:'Ganho total/ano',        value:_fmt(ganho_total),    color:'#22c55e', icon:'fa-rocket',          sub:'retenção + expansão de receita' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com modelos preditivos de churn e intervenção proativa, a O2 reduz a perda de clientes em 20%. Somado ao aumento de 10% no ticket médio via cross-sell e upsell, o potencial de ganho é <strong>' + _fmt(ganho_total) + '/ano</strong>. Cada cliente retido economiza também R$ ' + _num(cac) + ' em CAC.'
        };
      }
    },

    // ── PROCESSOS MANUAIS / AUTOMAÇÃO ─────────────────────────
    automacao: {
      benchmark: 'Benchmark: empresas com processos manuais gastam 30-40% do tempo em tarefas repetitivas. A O2 automatiza 70% dessas tarefas em 4-8 semanas.',
      fields: [
        { id:'func',       label:'Funcionários no processo',          placeholder:'Ex: 5',     hint:'Pessoas que executam as tarefas manuais. Inclua todos os envolvidos no fluxo' },
        { id:'salario',    label:'Salário médio mensal (R$)',          placeholder:'Ex: 3500',  hint:'Salário bruto. O custo real CLT é ~1,7x (FGTS, INSS, férias, 13º). Média BR: R$ 2.500–R$ 6.000' },
        { id:'horas_sem',  label:'Horas/semana em tarefas manuais',   placeholder:'Ex: 20',    hint:'Horas por funcionário em tarefas repetitivas. Média: 15-25h/sem (37-62% da jornada)' },
        { id:'erros_mes',  label:'Custo de erros/retrabalho/mês (R$)',placeholder:'Ex: 5000',  hint:'Inclua: devoluções, reprocessamento, multas, horas extras para corrigir. Média: R$ 2k–R$ 20k/mês' },
        { id:'processos',  label:'Número de processos manuais',       placeholder:'Ex: 8',     hint:'Fluxos repetitivos distintos (ex: emissão NF, conciliação, relatório, cadastro). Média PME: 5-15' },
      ],
      calc: function(v) {
        var func=v.func, sal=v.salario*1.7, hrs=v.horas_sem, erros=v.erros_mes, proc=v.processos;
        var custo_hora     = sal / 176;
        var custo_manual   = func * custo_hora * hrs * 4.3;
        var custo_anual    = (custo_manual + erros) * 12;
        var horas_mes      = func * hrs * 4.3;
        var auto_pct       = 0.70;
        var ganho_custo    = custo_manual * auto_pct * 12;
        var ganho_erros    = erros * 0.85 * 12;
        var ganho_total    = ganho_custo + ganho_erros;
        var horas_liberadas = horas_mes * auto_pct;
        return {
          loss: [
            { label:'Custo mensal de processos manuais', value:_fmt(custo_manual),  color:'#f59e0b', icon:'fa-clock',              sub:'em horas improdutivas' },
            { label:'Custo anual total',                 value:_fmt(custo_anual),   color:'#ef4444', icon:'fa-money-bill-trend-up', sub:'incluindo erros e retrabalho' },
            { label:'Horas perdidas/mês',                value:_num(horas_mes)+'h', color:'#f59e0b', icon:'fa-hourglass-half',      sub:'em tarefas repetitivas' },
          ],
          gain: [
            { label:'Economia de mão de obra/ano',  value:_fmt(ganho_custo),        color:'#22c55e', icon:'fa-coins',          sub:'com automação de 70% das tarefas' },
            { label:'Redução de erros/ano',         value:_fmt(ganho_erros),        color:'#22c55e', icon:'fa-shield-check',   sub:'-85% em erros e retrabalho' },
            { label:'Horas liberadas/mês',          value:_num(horas_liberadas)+'h',color:'#22c55e', icon:'fa-hourglass-end',  sub:'para atividades estratégicas' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Automatizando 70% das ' + Math.round(proc) + ' tarefas repetitivas, sua equipe recupera <strong>' + _num(horas_liberadas) + ' horas/mês</strong> para atividades estratégicas. Economia estimada: <strong>' + _fmt(ganho_total) + '/ano</strong> em custo de mão de obra e erros eliminados.'
        };
      }
    },

    // ── ESTOQUE PARADO ────────────────────────────────────────
    estoque_parado: {
      benchmark: 'Benchmark: 20-35% do estoque médio das empresas tem giro < 1x/ano. A O2 reduz em 35% com análise ABC-XYZ, giro entre filiais e reposição inteligente.',
      fields: [
        { id:'valor_estoque', label:'Valor total do estoque (R$)',       placeholder:'Ex: 2000000', hint:'Custo de aquisição de todo o estoque atual. PME: R$ 500k–R$ 10M' },
        { id:'pct_parado',    label:'% estimado de estoque parado',      placeholder:'Ex: 28',      hint:'Itens sem venda há >90 dias. Média BR: 20-35%. Acima de 40% = crítico' },
        { id:'num_sku',       label:'Total de SKUs no portfólio',        placeholder:'Ex: 4000',    hint:'Todos os produtos cadastrados, incluindo inativos. Ajuda a dimensionar o problema' },
        { id:'num_dep',       label:'Número de depósitos/filiais',       placeholder:'Ex: 3',       hint:'Mais depósitos = maior potencial de giro entre unidades para liberar capital' },
        { id:'custo_capital', label:'Custo de capital mensal (%)',       placeholder:'Ex: 1.5',     hint:'Taxa do crédito ou custo de oportunidade. CDI atual ~1,0%/mês | Capital próprio: 1,2-2,0%/mês' },
        { id:'custo_armaz',   label:'Custo de armazenagem mensal (R$)', placeholder:'Ex: 12000',   hint:'Aluguel + energia + mão de obra do depósito. Média: R$ 5k–R$ 50k/mês por galpão' },
      ],
      calc: function(v) {
        var est=v.valor_estoque, pct=v.pct_parado/100, cc=v.custo_capital/100, arm=v.custo_armaz;
        var est_parado       = est * pct;
        var custo_capital_ano = est_parado * cc * 12;
        var custo_armaz_ano  = arm * 12 * pct;
        var custo_total_ano  = custo_capital_ano + custo_armaz_ano;
        var reducao          = 0.35;
        var ganho_capital    = est_parado * reducao * cc * 12;
        var ganho_armaz      = custo_armaz_ano * reducao;
        var capital_liberado = est_parado * reducao;
        var ganho_total      = ganho_capital + ganho_armaz;
        return {
          loss: [
            { label:'Capital imobilizado parado', value:_fmt(est_parado),       color:'#eab308', icon:'fa-warehouse',          sub:'em itens de baixo giro' },
            { label:'Custo de capital/ano',       value:_fmt(custo_capital_ano),color:'#ef4444', icon:'fa-percent',            sub:'oportunidade perdida' },
            { label:'Custo total do estoque parado/ano', value:_fmt(custo_total_ano), color:'#ef4444', icon:'fa-money-bill-trend-up', sub:'capital + armazenagem' },
          ],
          gain: [
            { label:'Capital liberado',          value:_fmt(capital_liberado), color:'#22c55e', icon:'fa-coins',          sub:'-35% de estoque parado' },
            { label:'Economia de capital/ano',   value:_fmt(ganho_capital),    color:'#22c55e', icon:'fa-piggy-bank',     sub:'custo de oportunidade recuperado' },
            { label:'Ganho total estimado/ano',  value:_fmt(ganho_total),      color:'#22c55e', icon:'fa-rocket',         sub:'capital + armazenagem' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com análise ABC-XYZ, reposição inteligente e giro entre os ' + Math.round(v.num_dep) + ' depósitos, a O2 reduz o estoque parado em 35%. Liberação de capital estimada: <strong>' + _fmt(capital_liberado) + '</strong>, com economia de <strong>' + _fmt(ganho_total) + '/ano</strong> em custo de capital e armazenagem.'
        };
      }
    },

    // ── INADIMPLÊNCIA ─────────────────────────────────────────
    inadimplencia: {
      benchmark: 'Benchmark: inadimplência média no B2B brasileiro é 4-8%. A O2 reduz em 28% com scorecard de crédito e régua de cobrança inteligente.',
      fields: [
        { id:'carteira',   label:'Carteira de crédito ativa (R$)',  placeholder:'Ex: 3000000', hint:'Saldo total de crédito concedido a clientes. Inclua prazo, parcelado e boleto em aberto' },
        { id:'tx_inad',    label:'Taxa de inadimplência atual (%)', placeholder:'Ex: 6',       hint:'% da carteira em atraso >30 dias. Média B2B BR: 4-8%. Acima de 10% = crítico' },
        { id:'fat_mes',    label:'Faturamento médio mensal (R$)',   placeholder:'Ex: 1000000', hint:'Receita bruta mensal. Ajuda a dimensionar a carteira em relação ao faturamento' },
        { id:'custo_cobr', label:'Custo mensal de cobrança (R$)',   placeholder:'Ex: 20000',   hint:'Equipe de cobrança + sistema + ações (SMS, carta, advogado). Média: R$ 5k–R$ 50k/mês' },
        { id:'prazo_medio',label:'Prazo médio de recebimento (dias)',placeholder:'Ex: 45',     hint:'Dias médios entre a venda e o recebimento. Média BR: 30-60 dias' },
      ],
      calc: function(v) {
        var cart=v.carteira, tx=v.tx_inad/100, fat=v.fat_mes, cobr=v.custo_cobr, prazo=v.prazo_medio;
        var perda_carteira = cart * tx;
        var pdd            = cart * tx * 0.5;
        var custo_cobr_ano = cobr * 12;
        var custo_total    = perda_carteira + custo_cobr_ano;
        var tx_alvo        = tx * 0.72;
        var ganho_inad     = cart * (tx - tx_alvo);
        var ganho_cobr     = custo_cobr_ano * 0.40;
        var ganho_total    = ganho_inad + ganho_cobr;
        return {
          loss: [
            { label:'Exposição à inadimplência', value:_fmt(perda_carteira), color:'#ef4444', icon:'fa-file-invoice-dollar', sub:'saldo em risco na carteira' },
            { label:'PDD estimado',              value:_fmt(pdd),            color:'#f59e0b', icon:'fa-shield-halved',       sub:'provisão para devedores duvidosos' },
            { label:'Custo de cobrança/ano',     value:_fmt(custo_cobr_ano), color:'#f59e0b', icon:'fa-phone-volume',        sub:'operação de recuperação' },
          ],
          gain: [
            { label:'Recuperação de carteira',      value:_fmt(ganho_inad),  color:'#22c55e', icon:'fa-hand-holding-dollar', sub:'-28% inadimplência com scorecard' },
            { label:'Redução de custo de cobrança', value:_fmt(ganho_cobr),  color:'#22c55e', icon:'fa-robot',               sub:'-40% com cobrança automatizada' },
            { label:'Ganho total estimado',         value:_fmt(ganho_total), color:'#22c55e', icon:'fa-rocket',              sub:'carteira + operação' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com scorecard de crédito e régua de cobrança inteligente, a O2 reduz a inadimplência em 28%. Potencial de recuperação: <strong>' + _fmt(ganho_inad) + '</strong> na carteira, além de reduzir o custo operacional de cobrança em 40% — totalizando <strong>' + _fmt(ganho_total) + '</strong>.'
        };
      }
    },

    // ── TICKET MÉDIO BAIXO ────────────────────────────────────
    ticket: {
      benchmark: 'Benchmark: cross-sell e upsell bem implementados aumentam o ticket médio em 10-20%. A O2 projeta +10% com recomendação inteligente e segmentação de clientes.',
      fields: [
        { id:'fat_mes',     label:'Faturamento médio mensal (R$)', placeholder:'Ex: 500000', hint:'Receita bruta mensal. Use a média dos últimos 6 meses para maior precisão' },
        { id:'pedidos_mes', label:'Pedidos/transações por mês',    placeholder:'Ex: 2000',   hint:'Total de pedidos ou transações. Ticket = Faturamento ÷ Pedidos' },
        { id:'ticket',      label:'Ticket médio atual (R$)',       placeholder:'Ex: 250',    hint:'Valor médio por pedido. Varejo: R$ 100–R$ 500 | B2B: R$ 500–R$ 10.000' },
        { id:'margem',      label:'Margem bruta média (%)',        placeholder:'Ex: 38',     hint:'Varejo: 25-45% | Serviços: 50-70% | Indústria: 30-50% | Distribuição: 15-30%' },
        { id:'clientes',    label:'Base de clientes ativos',       placeholder:'Ex: 1500',   hint:'Clientes com compra nos últimos 12 meses. Usado para calcular impacto de retenção' },
      ],
      calc: function(v) {
        var fat=v.fat_mes, ped=v.pedidos_mes, tk=v.ticket, mg=v.margem/100, cli=v.clientes;
        var fat_ano        = fat * 12;
        var margem_atual   = fat_ano * mg;
        var ticket_novo    = tk * 1.10;
        // +10% ticket médio em todos os pedidos existentes
        var ganho_ticket   = ped * 12 * tk * 0.10 * mg;
        // +20% retenção: reduz churn, mantém ~4% a mais do faturamento anual
        var ganho_retencao = fat_ano * 0.04 * mg;
        var ganho_total    = ganho_ticket + ganho_retencao;
        return {
          loss: [
            { label:'Faturamento anual atual',    value:_fmt(fat_ano),      color:'#64748b', icon:'fa-chart-bar',       sub:'baseline atual' },
            { label:'Margem anual atual',         value:_fmt(margem_atual), color:'#64748b', icon:'fa-percent',         sub:'com ticket médio de ' + _fmtFull(tk) },
            { label:'Potencial não capturado/ano',value:_fmt(ganho_total),  color:'#f59e0b', icon:'fa-magnifying-glass-dollar', sub:'em receita adicional acessível' },
          ],
          gain: [
            { label:'Ganho de ticket médio/ano',  value:_fmt(ganho_ticket),   color:'#22c55e', icon:'fa-arrow-trend-up',  sub:'+10% ticket com cross-sell/upsell' },
            { label:'Ganho de retenção/ano',      value:_fmt(ganho_retencao), color:'#22c55e', icon:'fa-user-check',      sub:'+20% retenção com segmentação' },
            { label:'Ticket médio projetado',     value:_fmtFull(ticket_novo),color:'#22c55e', icon:'fa-rocket',          sub:'vs ' + _fmtFull(tk) + ' atual' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com recomendação inteligente de produtos, segmentação de clientes e campanhas de upsell automatizadas, a O2 projeta +10% no ticket médio (de ' + _fmtFull(tk) + ' para ' + _fmtFull(ticket_novo) + ') e +20% de retenção. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong> em margem adicional.'
        };
      }
    },

    // ── INEFICIÊNCIA NA PRODUÇÃO ──────────────────────────────
    producao: {
      benchmark: 'Benchmark: empresas industriais perdem 15-25% da capacidade produtiva com paradas não planejadas e retrabalho. A O2 reduz em 30% com manutenção preditiva e controle de processo.',
      fields: [
        { id:'fat_mes',      label:'Faturamento médio mensal (R$)',      placeholder:'Ex: 1500000', hint:'Receita bruta mensal da indústria. Use média dos últimos 6 meses' },
        { id:'func_prod',    label:'Funcionários na produção',           placeholder:'Ex: 50',      hint:'Pessoas diretamente na linha de produção (operadores, técnicos)' },
        { id:'salario_med',  label:'Salário médio produção (R$)',        placeholder:'Ex: 2800',    hint:'Salário bruto do operador. Média indústria BR: R$ 2.000–R$ 4.500. Custo real CLT ~1,7x' },
        { id:'horas_parada', label:'Horas de parada não planejada/mês',  placeholder:'Ex: 40',      hint:'Horas de máquina parada por falha/manutenção corretiva. Média: 20-80h/mês. Acima de 5% do tempo = crítico' },
        { id:'pct_retrabalho',label:'% de produção com retrabalho/defeito',placeholder:'Ex: 5',    hint:'% de itens que precisam reprocessamento ou descarte. Meta classe mundial: <1%. Média BR: 3-8%' },
        { id:'custo_hora',   label:'Custo da hora de máquina parada (R$)',placeholder:'Ex: 800',   hint:'Energia + mão de obra + overhead por hora parada. Calcule: custo fixo mensal ÷ horas produtivas. Média: R$ 300–R$ 2.000/h' },
      ],
      calc: function(v) {
        var fat=v.fat_mes, func=v.func_prod, sal=v.salario_med*1.7, hp=v.horas_parada, pct=v.pct_retrabalho/100, ch=v.custo_hora;
        var custo_parada_mes  = hp * ch;
        var custo_retrabalho  = fat * pct * 0.15; // 15% do faturamento afetado vira custo
        var custo_total_mes   = custo_parada_mes + custo_retrabalho;
        var custo_total_ano   = custo_total_mes * 12;
        var ganho_parada      = custo_parada_mes * 0.60 * 12; // -60% paradas com manutencao preditiva
        var ganho_retrabalho  = custo_retrabalho * 0.70 * 12; // -70% retrabalho com controle de processo
        var ganho_total       = ganho_parada + ganho_retrabalho;
        return {
          loss: [
            { label:'Custo de paradas/mês',    value:_fmt(custo_parada_mes), color:'#f97316', icon:'fa-industry',         sub:hp + 'h de linha parada' },
            { label:'Custo de retrabalho/mês', value:_fmt(custo_retrabalho), color:'#ef4444', icon:'fa-rotate-left',      sub:_pct(pct*100) + ' de produção com defeito' },
            { label:'Custo total anual',       value:_fmt(custo_total_ano),  color:'#ef4444', icon:'fa-money-bill-trend-up',sub:'paradas + retrabalho' },
          ],
          gain: [
            { label:'Redução de paradas/ano',    value:_fmt(ganho_parada),     color:'#22c55e', icon:'fa-wrench',         sub:'-60% com manutenção preditiva' },
            { label:'Redução de retrabalho/ano', value:_fmt(ganho_retrabalho), color:'#22c55e', icon:'fa-shield-check',   sub:'-70% com controle estatístico de processo' },
            { label:'Ganho total estimado/ano',  value:_fmt(ganho_total),      color:'#22c55e', icon:'fa-rocket',         sub:'produtividade + qualidade' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com manutenção preditiva e controle estatístico de processo (CEP), a O2 reduz paradas não planejadas em 60% e retrabalho em 70%. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong> em produtividade e qualidade.'
        };
      }
    },

    // ── COMPRAS INEFICIENTES ──────────────────────────────────
    compras: {
      benchmark: 'Benchmark: empresas sem inteligência de compras pagam 8-15% acima do preço de mercado. A O2 reduz o custo de aquisição em 10% com análise de mercado e negociação baseada em dados.',
      fields: [
        { id:'volume_compras', label:'Volume de compras mensal (R$)',    placeholder:'Ex: 600000', hint:'Total pago a fornecedores por mês (mercadorias, matéria-prima, insumos). Média PME: R$ 200k–R$ 3M/mês' },
        { id:'num_fornec',     label:'Número de fornecedores ativos',    placeholder:'Ex: 80',     hint:'Fornecedores com pelo menos 1 pedido nos últimos 12 meses. Muitos fornecedores = menor poder de negociação' },
        { id:'num_sku',        label:'SKUs comprados regularmente',      placeholder:'Ex: 2000',   hint:'Itens comprados com frequência (pelo menos 1x/trimestre). Ajuda a dimensionar o esforço de negociação' },
        { id:'lead_time',      label:'Tempo médio de entrega (dias)',    placeholder:'Ex: 15',     hint:'Dias entre o pedido e o recebimento. Média BR: 7-30 dias. Lead time alto = mais compras urgentes' },
        { id:'pct_urgencia',   label:'% de compras em caráter urgente',  placeholder:'Ex: 20',     hint:'Compras fora do planejamento (falta de estoque, urgência). Média: 10-30%. Acima de 25% = problema de planejamento' },
      ],
      calc: function(v) {
        var vol=v.volume_compras, forn=v.num_fornec, sku=v.num_sku, lt=v.lead_time, urg=v.pct_urgencia/100;
        // Compras urgentes custam ~18% a mais (frete expresso, fornecedor spot, sem negociação)
        var custo_urgencia_mes = vol * urg * 0.18;
        var custo_urgencia_ano = custo_urgencia_mes * 12;
        // Sem dados de mercado, paga-se ~8% acima do preço ótimo
        var custo_ineficiencia = vol * 0.08 * 12;
        var custo_total_ano    = custo_urgencia_ano + custo_ineficiencia;
        // O2: recupera 70% da ineficiência via benchmarking e negociação baseada em dados
        var ganho_negociacao   = custo_ineficiencia * 0.70;
        // O2: elimina 70% das compras urgentes com planejamento de demanda
        var ganho_urgencia     = custo_urgencia_ano * 0.70;
        var ganho_total        = ganho_negociacao + ganho_urgencia;
        return {
          loss: [
            { label:'Custo de compras urgentes/ano', value:_fmt(custo_urgencia_ano),  color:'#06b6d4', icon:'fa-bolt',              sub:_pct(urg*100) + ' das compras sem planejamento' },
            { label:'Custo de ineficiência/ano',     value:_fmt(custo_ineficiencia),  color:'#ef4444', icon:'fa-magnifying-glass-dollar', sub:'8% acima do mercado sem dados' },
            { label:'Custo total evitável/ano',      value:_fmt(custo_total_ano),     color:'#ef4444', icon:'fa-money-bill-trend-up', sub:'urgência + ineficiência' },
          ],
          gain: [
            { label:'Ganho de negociação/ano',    value:_fmt(ganho_negociacao), color:'#22c55e', icon:'fa-handshake',      sub:'-10% custo com dados de mercado' },
            { label:'Redução de urgências/ano',   value:_fmt(ganho_urgencia),   color:'#22c55e', icon:'fa-calendar-check', sub:'-70% compras urgentes com planejamento' },
            { label:'Ganho total estimado/ano',   value:_fmt(ganho_total),      color:'#22c55e', icon:'fa-rocket',         sub:'negociação + planejamento' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com inteligência de compras, benchmarking de preços e planejamento de demanda, a O2 reduz o custo de aquisição em 10% e elimina 70% das compras urgentes. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong> em economia de compras.'
        };
      }
    },

    // ── FUNIL COMERCIAL LENTO ─────────────────────────────────
    funil: {
      benchmark: 'Benchmark: empresas B2B perdem 40-60% das oportunidades por follow-up tardio. A O2 aumenta a conversão em 25% com automação de CRM e lead scoring.',
      fields: [
        { id:'leads_mes',    label:'Leads gerados por mês',             placeholder:'Ex: 200',    hint:'Oportunidades que entram no funil (MQL + SQL). Inclua todos os canais: inbound, outbound, indicação' },
        { id:'tx_conv',      label:'Taxa de conversão atual (%)',       placeholder:'Ex: 8',      hint:'% de leads que viram clientes. Média B2B: 5-15%. Abaixo de 5% = funil com problema' },
        { id:'ticket_medio', label:'Ticket médio por contrato (R$)',    placeholder:'Ex: 15000',  hint:'Valor médio de um novo contrato. B2B serviços: R$ 5k–R$ 100k | SaaS: R$ 500–R$ 10k/mês' },
        { id:'ciclo_venda',  label:'Ciclo de venda médio (dias)',       placeholder:'Ex: 45',     hint:'Dias do primeiro contato ao fechamento. B2B: 30-120 dias. Ciclo longo = mais custo de vendas' },
        { id:'margem',       label:'Margem bruta média (%)',            placeholder:'Ex: 45',     hint:'Serviços: 50-70% | SaaS: 60-80% | Consultoria: 40-60% | Produtos: 25-45%' },
      ],
      calc: function(v) {
        var leads=v.leads_mes, tx=v.tx_conv/100, tk=v.ticket_medio, ciclo=v.ciclo_venda, mg=v.margem/100;
        var contratos_mes    = leads * tx;
        var receita_mes      = contratos_mes * tk;
        var oport_perdidas   = leads * (1 - tx);
        var receita_perdida  = oport_perdidas * tk * 0.15; // 15% das perdidas eram recuperáveis
        var tx_alvo          = tx * 1.25; // +25% conversão
        var ganho_conversao  = leads * (tx_alvo - tx) * tk * 12 * mg;
        var ganho_ciclo      = receita_mes * 12 * mg * 0.10; // 10% mais receita por ciclo menor
        var ganho_total      = ganho_conversao + ganho_ciclo;
        return {
          loss: [
            { label:'Oportunidades perdidas/mês', value:_num(oport_perdidas),   color:'#a855f7', icon:'fa-filter',          sub:'leads não convertidos' },
            { label:'Receita recuperável/mês',    value:_fmt(receita_perdida),  color:'#ef4444', icon:'fa-money-bill-wave', sub:'15% das perdas eram evitáveis' },
            { label:'Ciclo de venda atual',       value:ciclo + ' dias',        color:'#f59e0b', icon:'fa-clock',           sub:'tempo até o fechamento' },
          ],
          gain: [
            { label:'Ganho de conversão/ano',   value:_fmt(ganho_conversao), color:'#22c55e', icon:'fa-chart-line',     sub:'+25% conversão com lead scoring' },
            { label:'Ganho de velocidade/ano',  value:_fmt(ganho_ciclo),     color:'#22c55e', icon:'fa-bolt',           sub:'+10% receita com ciclo mais curto' },
            { label:'Ganho total estimado/ano', value:_fmt(ganho_total),     color:'#22c55e', icon:'fa-rocket',         sub:'conversão + velocidade' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com automação de CRM, lead scoring e follow-up inteligente, a O2 aumenta a conversão em 25% e reduz o ciclo de venda. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong> em receita adicional.'
        };
      }
    },

    // ── LEAD TIME DE IMPORTAÇÃO ───────────────────────────────
    lead_time: {
      benchmark: 'Benchmark: atrasos de importação custam em média 2-5% do valor da mercadoria em custos extras. A O2 reduz em 40% os atrasos com visibilidade em tempo real e planejamento preditivo.',
      fields: [
        { id:'volume_import', label:'Volume de importação mensal (R$)',  placeholder:'Ex: 800000', hint:'Valor CIF das mercadorias importadas por mês (produto + frete + seguro). Média PME importadora: R$ 200k–R$ 5M/mês' },
        { id:'num_pedidos',   label:'Pedidos de importação por mês',     placeholder:'Ex: 15',     hint:'Número de ordens de importação (POs) mensais. Cada pedido atrasado gera custo direto' },
        { id:'lead_time',     label:'Lead time médio atual (dias)',       placeholder:'Ex: 60',     hint:'Dias do pedido ao recebimento no Brasil. China: 45-75 dias | EUA: 20-40 dias | Europa: 30-60 dias' },
        { id:'pct_atraso',    label:'% de pedidos com atraso',           placeholder:'Ex: 35',     hint:'% de importações que chegam fora do prazo acordado. Média: 25-45%. Acima de 40% = crítico' },
        { id:'custo_atraso',  label:'Custo médio por atraso (R$)',       placeholder:'Ex: 5000',   hint:'Multas de contrato + armazenagem extra no porto + frete urgente. Média: R$ 2k–R$ 15k por pedido atrasado' },
      ],
      calc: function(v) {
        var vol=v.volume_import, ped=v.num_pedidos, lt=v.lead_time, pct=v.pct_atraso/100, ca=v.custo_atraso;
        var pedidos_atrasados = ped * pct;
        var custo_atraso_mes  = pedidos_atrasados * ca;
        var custo_atraso_ano  = custo_atraso_mes * 12;
        var custo_capital_ano = vol * 0.015 * (lt/30) * 12; // custo de capital do estoque em trânsito
        var custo_total_ano   = custo_atraso_ano + custo_capital_ano;
        var ganho_atraso      = custo_atraso_ano * 0.40;
        var ganho_capital     = custo_capital_ano * 0.25;
        var ganho_total       = ganho_atraso + ganho_capital;
        return {
          loss: [
            { label:'Pedidos atrasados/mês',    value:_num(pedidos_atrasados),  color:'#64748b', icon:'fa-clock-rotate-left', sub:_pct(pct*100) + ' das importações' },
            { label:'Custo de atrasos/ano',     value:_fmt(custo_atraso_ano),   color:'#ef4444', icon:'fa-triangle-exclamation', sub:'multas, armazenagem e frete urgente' },
            { label:'Custo de capital em trânsito/ano', value:_fmt(custo_capital_ano), color:'#f59e0b', icon:'fa-ship', sub:'capital imobilizado no lead time' },
          ],
          gain: [
            { label:'Redução de atrasos/ano',    value:_fmt(ganho_atraso),  color:'#22c55e', icon:'fa-calendar-check', sub:'-40% atrasos com visibilidade em tempo real' },
            { label:'Redução de capital/ano',    value:_fmt(ganho_capital), color:'#22c55e', icon:'fa-coins',          sub:'-25% capital em trânsito com planejamento' },
            { label:'Ganho total estimado/ano',  value:_fmt(ganho_total),   color:'#22c55e', icon:'fa-rocket',         sub:'atrasos + capital' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com visibilidade em tempo real da cadeia de importação e planejamento preditivo, a O2 reduz atrasos em 40% e o capital imobilizado em trânsito em 25%. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong>.'
        };
      }
    },

    // ── QUALIDADE / DEVOLUÇÕES ────────────────────────────────
    qualidade: {
      benchmark: 'Benchmark: devoluções e retrabalho custam 2-5% do faturamento. A O2 reduz em 60% com controle estatístico de processo e rastreabilidade.',
      fields: [
        { id:'fat_mes',      label:'Faturamento médio mensal (R$)',    placeholder:'Ex: 1200000', hint:'Receita bruta mensal. Use média dos últimos 6 meses para maior precisão' },
        { id:'pct_devolucao',label:'Taxa de devolução/defeito (%)',    placeholder:'Ex: 3',       hint:'% de produtos devolvidos ou com defeito. Indústria: 1-5% | Varejo: 2-8%. Acima de 5% = crítico' },
        { id:'custo_retrabalho',label:'Custo de retrabalho/mês (R$)', placeholder:'Ex: 15000',   hint:'Mão de obra + material para corrigir defeitos. Inclua descarte. Média: 1-3% do faturamento' },
        { id:'margem',       label:'Margem bruta média (%)',           placeholder:'Ex: 35',      hint:'Varejo: 25-45% | Indústria: 30-50% | Distribuição: 15-30%' },
        { id:'num_fornec',   label:'Número de fornecedores',           placeholder:'Ex: 40',      hint:'Fornecedores que fornecem insumos/componentes. Mais fornecedores = maior variabilidade de qualidade' },
      ],
      calc: function(v) {
        var fat=v.fat_mes, pct=v.pct_devolucao/100, retr=v.custo_retrabalho, mg=v.margem/100, forn=v.num_fornec;
        var perda_devolucao  = fat * pct;
        var custo_total_mes  = perda_devolucao + retr;
        var custo_total_ano  = custo_total_mes * 12;
        var ganho_qualidade  = perda_devolucao * 0.60 * 12;
        var ganho_retrabalho = retr * 0.70 * 12;
        var ganho_total      = ganho_qualidade + ganho_retrabalho;
        return {
          loss: [
            { label:'Perda por devoluções/mês',  value:_fmt(perda_devolucao), color:'#ec4899', icon:'fa-circle-xmark',       sub:_pct(pct*100) + ' do faturamento' },
            { label:'Custo de retrabalho/mês',   value:_fmt(retr),            color:'#ef4444', icon:'fa-rotate-left',        sub:'correção de defeitos' },
            { label:'Custo total de qualidade/ano', value:_fmt(custo_total_ano), color:'#ef4444', icon:'fa-money-bill-trend-up', sub:'devoluções + retrabalho' },
          ],
          gain: [
            { label:'Redução de devoluções/ano',  value:_fmt(ganho_qualidade),  color:'#22c55e', icon:'fa-shield-check',   sub:'-60% com controle estatístico (CEP)' },
            { label:'Redução de retrabalho/ano',  value:_fmt(ganho_retrabalho), color:'#22c55e', icon:'fa-wrench',         sub:'-70% com rastreabilidade e alertas' },
            { label:'Ganho total estimado/ano',   value:_fmt(ganho_total),      color:'#22c55e', icon:'fa-rocket',         sub:'qualidade + produtividade' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com controle estatístico de processo (CEP) e rastreabilidade end-to-end, a O2 reduz devoluções em 60% e retrabalho em 70%. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong> em qualidade e produtividade.'
        };
      }
    },

    // ── EXPOSIÇÃO CAMBIAL ─────────────────────────────────────
    cambio: {
      benchmark: 'Benchmark: empresas importadoras sem hedge cambial perdem 3-8% do volume em anos de alta volatilidade. A O2 implementa estratégias de proteção e planejamento cambial.',
      fields: [
        { id:'volume_import', label:'Volume de importação anual (R$)',   placeholder:'Ex: 5000000', hint:'Total importado por ano em reais (câmbio atual). PME importadora: R$ 1M–R$ 30M/ano' },
        { id:'pct_dolar',     label:'% das compras em dólar/euro',       placeholder:'Ex: 80',      hint:'Parcela das importações em moeda estrangeira. Quanto maior, maior a exposição cambial' },
        { id:'variacao_cambio',label:'Variação cambial sofrida (%)',     placeholder:'Ex: 8',       hint:'% de alta do câmbio no período analisado. Dólar variou +15% em 2024. Use o pior cenário recente' },
        { id:'margem',        label:'Margem bruta média (%)',            placeholder:'Ex: 30',      hint:'Importadores: 20-40%. Cada 1% de alta cambial sem hedge corrói ~1-3% da margem' },
      ],
      calc: function(v) {
        var vol=v.volume_import, pct=v.pct_dolar/100, var_cambio=v.variacao_cambio/100, mg=v.margem/100;
        var exposicao        = vol * pct;
        var perda_cambio     = exposicao * var_cambio;
        var impacto_margem   = perda_cambio / (vol * mg) * 100;
        var ganho_hedge      = perda_cambio * 0.70; // 70% da perda evitável com hedge
        var ganho_planejamento = vol * 0.02; // 2% de economia com planejamento de compras
        var ganho_total      = ganho_hedge + ganho_planejamento;
        return {
          loss: [
            { label:'Exposição cambial',         value:_fmt(exposicao),     color:'#10b981', icon:'fa-dollar-sign',        sub:_pct(pct*100) + ' das compras em moeda estrangeira' },
            { label:'Perda cambial estimada',    value:_fmt(perda_cambio),  color:'#ef4444', icon:'fa-chart-line-down',    sub:'com ' + _pct(var_cambio*100) + ' de alta do câmbio' },
            { label:'Impacto na margem',         value:_pct(impacto_margem),color:'#f59e0b', icon:'fa-percent',            sub:'pontos percentuais de margem perdidos' },
          ],
          gain: [
            { label:'Proteção com hedge/ano',       value:_fmt(ganho_hedge),        color:'#22c55e', icon:'fa-shield-halved',  sub:'70% da perda cambial evitável' },
            { label:'Economia de planejamento/ano', value:_fmt(ganho_planejamento), color:'#22c55e', icon:'fa-calendar-check', sub:'+2% com timing de compras otimizado' },
            { label:'Ganho total estimado/ano',     value:_fmt(ganho_total),        color:'#22c55e', icon:'fa-rocket',         sub:'hedge + planejamento' },
          ],
          timeline: [
            { period:'Dia',    value:_fmt(ganho_total/365) },
            { period:'Semana', value:_fmt(ganho_total/52) },
            { period:'Mês',    value:_fmt(ganho_total/12) },
            { period:'Ano',    value:_fmt(ganho_total) },
          ],
          roi: 'Com estratégia de hedge cambial e planejamento de compras baseado em dados, a O2 protege 70% da exposição cambial e otimiza o timing de compras. Ganho estimado: <strong>' + _fmt(ganho_total) + '/ano</strong>.'
        };
      }
    },

  }; // end PROBLEMS


  // ── UI: Selecionar Setor ───────────────────────────────────
  window.calcSelectSector = function(s) {
    _sector = s;
    _prob   = null;

    // Highlight setor
    document.querySelectorAll('.calc-sector-btn').forEach(function(b) {
      b.classList.remove('bg-white/15','border-blue-400/60','border-orange-400/60','border-teal-400/60','border-purple-400/60','border-yellow-400/60','border-green-400/60','border-red-400/60','border-cyan-400/60');
      b.classList.add('border-white/10','bg-white/5');
    });
    var btn = document.querySelector('[data-s="'+s+'"]');
    if (btn) { btn.classList.remove('border-white/10','bg-white/5'); btn.classList.add('bg-white/15','border-blue-400/60'); }

    // Montar grid de problemas
    var probs = SECTOR_PROBLEMS[s] || [];
    var html  = probs.map(function(p) {
      var m = PROBLEM_META[p];
      if (!m) return '';
      return '<button onclick="calcSelectProblem(\''+p+'\')" data-p="'+p+'"'
        + ' class="calc-prob-btn flex flex-col items-center gap-2 p-4 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all text-center group">'
        + '<i class="fa-solid '+m.icon+' text-xl group-hover:scale-110 transition-transform" style="color:'+m.color+'"></i>'
        + '<span class="text-white text-xs font-bold">'+m.label+'</span>'
        + '<span class="text-blue-300/50 text-[10px]">'+m.sub+'</span>'
        + '</button>';
    }).join('');

    document.getElementById('calc-problem-grid').innerHTML = html;
    document.getElementById('calc-problem-wrap').classList.remove('hidden');
    document.getElementById('calc-inputs').classList.add('hidden');
    document.getElementById('calc-result').classList.add('hidden');
  };

  // ── UI: Selecionar Problema ────────────────────────────────
  window.calcSelectProblem = function(p) {
    _prob = p;
    var prob = PROBLEMS[p];
    if (!prob) return;

    // Highlight problema
    document.querySelectorAll('.calc-prob-btn').forEach(function(b) {
      b.classList.remove('bg-white/15','border-blue-400/60');
      b.classList.add('border-white/10','bg-white/5');
    });
    var btn = document.querySelector('[data-p="'+p+'"]');
    if (btn) { btn.classList.remove('border-white/10','bg-white/5'); btn.classList.add('bg-white/15','border-blue-400/60'); }

    // Montar campos
    var fieldsHtml = prob.fields.map(function(f) {
      return '<div>'
        + '<label class="block text-blue-200/70 text-[10px] font-bold mb-1.5 uppercase tracking-widest">'+f.label+'</label>'
        + '<input type="number" id="calc-f-'+f.id+'" placeholder="'+f.placeholder+'"'
        + ' class="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white text-sm placeholder-blue-300/30 focus:outline-none focus:border-blue-400/60 focus:bg-white/10 transition-all"'
        + ' oninput="calcCompute()">'
        + '<p class="text-blue-300/40 text-[10px] mt-1">'+f.hint+'</p>'
        + '</div>';
    }).join('');

    document.getElementById('calc-fields').innerHTML = fieldsHtml;
    document.getElementById('calc-benchmark-note').textContent = prob.benchmark || '';
    document.getElementById('calc-inputs').classList.remove('hidden');
    document.getElementById('calc-result').classList.add('hidden');
  };

  // ── UI: Calcular ───────────────────────────────────────────
  window.calcCompute = function() {
    if (!_prob) return;
    var prob = PROBLEMS[_prob];
    if (!prob) return;
    var vals = {};
    var allFilled = true;
    prob.fields.forEach(function(f) {
      var el = document.getElementById('calc-f-'+f.id);
      var v  = el ? parseFloat(el.value) : NaN;
      if (!v || isNaN(v) || v <= 0) allFilled = false;
      vals[f.id] = v || 0;
    });
    if (!allFilled) { document.getElementById('calc-result').classList.add('hidden'); return; }

    var res = prob.calc(vals);

    // Render loss cards
    document.getElementById('calc-loss-cards').innerHTML = _renderCards(res.loss);
    // Render gain cards
    document.getElementById('calc-gain-cards').innerHTML = _renderCards(res.gain);
    // Render ROI text
    document.getElementById('calc-roi-text').innerHTML = res.roi;
    // Render timeline
    document.getElementById('calc-timeline').innerHTML = res.timeline.map(function(t) {
      return '<div class="text-center p-4 rounded-2xl" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08)">'
        + '<p class="text-blue-300/50 text-[10px] font-bold uppercase tracking-widest mb-2">'+t.period+'</p>'
        + '<p class="text-white font-black text-lg">'+t.value+'</p>'
        + '</div>';
    }).join('');

    document.getElementById('calc-result').classList.remove('hidden');
  };

  function _renderCards(cards) {
    return cards.map(function(c) {
      return '<div class="rounded-2xl p-5 text-center" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08)">'
        + '<div class="w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center" style="background:'+c.color+'20">'
        + '<i class="fa-solid '+c.icon+' text-sm" style="color:'+c.color+'"></i>'
        + '</div>'
        + '<p class="text-2xl font-black text-white mb-1">'+c.value+'</p>'
        + '<p class="text-blue-200/80 text-xs font-bold">'+c.label+'</p>'
        + '<p class="text-blue-300/40 text-[10px] mt-1">'+c.sub+'</p>'
        + '</div>';
    }).join('');
  }

})();
