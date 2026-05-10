// ============================================================
//  O2 Data Solutions — main.js v3
//  Dark mode (cookie), scroll, form real, WhatsApp, reveal
// ============================================================

const COOKIE_NAME = 'o2_theme';
const COOKIE_DAYS = 365;
const WA_NUMBER   = '5511913353137';

// ── Cookie helpers ───────────────────────────────────────────
function setCookie(n, v, d) {
  const e = new Date(); e.setTime(e.getTime() + d * 864e5);
  document.cookie = n + '=' + v + ';expires=' + e.toUTCString() + ';path=/;SameSite=Lax';
}
function getCookie(n) {
  const m = document.cookie.match('(^| )' + n + '=([^;]+)');
  return m ? m[2] : null;
}

// ── Theme ────────────────────────────────────────────────────
function applyTheme(t) {
  const html = document.documentElement;
  const icons = [document.getElementById('theme-icon'), document.getElementById('theme-icon-mobile')];
  if (t === 'dark') {
    html.classList.add('dark');
    icons.forEach(i => { if (i) { i.classList.remove('fa-moon'); i.classList.add('fa-sun'); } });
  } else {
    html.classList.remove('dark');
    icons.forEach(i => { if (i) { i.classList.remove('fa-sun'); i.classList.add('fa-moon'); } });
  }
}
function toggleTheme() {
  const next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
  applyTheme(next);
  setCookie(COOKIE_NAME, next, COOKIE_DAYS);
}
// Init theme: cookie > system > dark
(function() {
  const saved = getCookie(COOKIE_NAME);
  const sys   = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  applyTheme(saved || sys);
  if (!saved) setCookie(COOKIE_NAME, sys, COOKIE_DAYS);
})();

// ── Navbar scroll ────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const nav = document.getElementById('main-nav');
  if (nav) nav.classList.toggle('shadow-xl', window.scrollY > 30);
}, { passive: true });

// ── Mobile menu ──────────────────────────────────────────────
function toggleMobileMenu() {
  const m = document.getElementById('mobile-menu');
  if (m) m.classList.toggle('hidden');
}

// ── Smooth scroll ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', function(e) {
      const t = document.querySelector(this.getAttribute('href'));
      if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
      const m = document.getElementById('mobile-menu');
      if (m) m.classList.add('hidden');
    });
  });

  // Reveal on scroll
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));
});

// ── Contact Form ─────────────────────────────────────────────
async function handleFormSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const btn  = document.getElementById('submit-btn') || form.querySelector('button[type="submit"]');
  const data = Object.fromEntries(new FormData(form));

  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Enviando...';
  btn.disabled  = true;

  try {
    const res  = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (res.ok) {
      btn.innerHTML = '<i class="fa-solid fa-check mr-2"></i>Enviado! Entraremos em contato em breve.';
      btn.classList.add('bg-green-500', 'text-white');
      btn.classList.remove('bg-white', 'text-brand-600');
      form.reset();
    } else {
      throw new Error(json.detail || 'Erro');
    }
  } catch (err) {
    btn.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-2"></i>Erro. Tente pelo WhatsApp.';
    btn.classList.add('bg-red-500', 'text-white');
    btn.classList.remove('bg-white', 'text-brand-600');
  } finally {
    setTimeout(() => {
      btn.innerHTML = '<i class="fa-solid fa-calendar-check mr-2"></i>Agendar Reunião de Diagnóstico';
      btn.disabled  = false;
      btn.classList.remove('bg-green-500', 'bg-red-500', 'text-white');
      btn.classList.add('bg-white', 'text-brand-600');
    }, 5000);
  }
}

// ── WhatsApp tracker ──────────────────────────────────────────
function trackWhatsApp(source) {
  const msg = encodeURIComponent('Olá! Vim pelo site da O2 Data Solutions e gostaria de agendar uma reunião de diagnóstico gratuita.');
  window.open('https://wa.me/' + WA_NUMBER + '?text=' + msg, '_blank');
}
