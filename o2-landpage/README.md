# O2 Data Solutions — Landing Page

Landing page B2B da **O2 Data Solutions** — Consultoria em Dados, IA e Machine Learning. Maringá, Paraná.

---

## Estrutura do Projeto

```
o2-landpage/
├── index.html                  ← Página principal (monta os partials)
├── assets/
│   ├── css/
│   │   └── styles.css          ← Estilos globais customizados
│   └── js/
│       ├── config.js           ← ⭐ FONTE ÚNICA DE VERDADE (textos, links, dados)
│       └── main.js             ← Comportamentos: dark mode, scroll, form
├── partials/
│   ├── navbar.html             ← Navbar sticky com glass effect
│   ├── hero.html               ← Hero: headline, CTAs, mockup visual
│   ├── logos.html              ← Faixa de logos de clientes
│   ├── services.html           ← Grid de 6 serviços/soluções
│   ├── methodology.html        ← Metodologia proprietária em 4 passos
│   ├── metrics.html            ← Big numbers + depoimento
│   ├── cta.html                ← CTA com formulário de contato
│   └── footer.html             ← Footer rico com colunas e redes sociais
└── README.md
```

---

## Como rodar localmente

O loader de partials usa `fetch()`, então precisa de um servidor HTTP local (não funciona abrindo o `index.html` direto no browser por restrição de CORS).

```bash
# Python (qualquer versão)
cd o2-landpage
python -m http.server 8080

# Node.js (npx)
cd o2-landpage
npx serve .
```

Acesse: `http://localhost:8080`

---

## Como editar conteúdo

### Textos, links e dados → `assets/js/config.js`

Toda a configuração de conteúdo está centralizada em `config.js`. Edite lá sem tocar no HTML:

```js
// Exemplo: mudar o headline do hero
hero: {
  headline1:    "Decisões mais inteligentes,",
  headlineGrad: "resultados mensuráveis.",
  ...
}

// Exemplo: adicionar um serviço
services: {
  items: [
    { icon: "fa-solid fa-...", color: "blue", title: "Novo Serviço", desc: "..." },
    ...
  ]
}
```

### Seções → `partials/*.html`

Cada seção é um arquivo HTML independente. Para editar o layout de uma seção específica, edite apenas o partial correspondente.

### Adicionar nova seção

1. Crie `partials/nova-secao.html`
2. Adicione um slot em `index.html`: `<div id="slot-nova-secao"></div>`
3. Adicione ao array `PARTIALS` no script loader do `index.html`

---

## Arquitetura Micro-Frontend

O projeto foi estruturado para facilitar a migração para micro-frontends:

| Abordagem         | Como migrar                                              |
|-------------------|----------------------------------------------------------|
| **SSI**           | Substitua os slots por `<!--#include file="partials/..."-->` |
| **Next.js / SSR** | Cada partial vira um componente React/Vue                |
| **Web Components**| Cada partial vira um `<custom-element>`                  |
| **Module Federation** | Cada partial vira um módulo remoto Webpack/Vite      |

---

## Seções da Página

| Seção         | ID âncora      | Partial                  |
|---------------|----------------|--------------------------|
| Navbar        | —              | `navbar.html`            |
| Hero          | —              | `hero.html`              |
| Clientes      | —              | `logos.html`             |
| Soluções      | `#solucoes`    | `services.html`          |
| Metodologia   | `#metodologia` | `methodology.html`       |
| Resultados    | `#resultados`  | `metrics.html`           |
| Contato       | `#contato`     | `cta.html`               |
| Footer        | —              | `footer.html`            |

---

## Stack

- **Tailwind CSS** (CDN) — utilitários de estilo
- **FontAwesome 6** — ícones
- **Plus Jakarta Sans** — tipografia
- **Vanilla JS** — sem dependências de framework
- **Python HTTP Server** — desenvolvimento local

---

## Próximos passos sugeridos

- [ ] Conectar formulário de contato a um backend / CRM (HubSpot, RD Station)
- [ ] Adicionar seção de Cases com logos reais de clientes
- [ ] Substituir logos placeholder pelos logos reais dos clientes
- [ ] Configurar domínio e deploy (Vercel, Netlify, ou servidor próprio)
- [ ] Adicionar Google Analytics / Meta Pixel
- [ ] Criar página `/blog` e `/cases`

---

*O2 Data Solutions · Maringá, Paraná · contato@o2datasolutions.com.br*
