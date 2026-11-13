(function(){
  const state = { deferredPrompt: null, installed: false, env: null, adapt: {} };
  const $ = (s, r=document) => r.querySelector(s);
  const setText = (id, t) => { const el = document.getElementById(id); if (el) el.textContent = t; };
  const setHTML = (id, h) => { const el = document.getElementById(id); if (el) el.innerHTML = h; };

  function detectClientEnv(){
    const nav = navigator || {}; const scr = screen || {}; const loc = location || {};
    const conn = nav.connection || nav.mozConnection || nav.webkitConnection || {};
    const ua = nav.userAgent || '';
    const mobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua) || (nav.maxTouchPoints||0)>1;
    return {
      url: loc.href, origin: loc.origin, pathname: loc.pathname, protocol: loc.protocol, host: loc.host,
      userAgent: ua, platform: nav.platform, language: nav.language, languages: nav.languages,
      timezone: (Intl && Intl.DateTimeFormat) ? Intl.DateTimeFormat().resolvedOptions().timeZone : null,
      screen: { width: scr.width, height: scr.height, availWidth: scr.availWidth, availHeight: scr.availHeight, colorDepth: scr.colorDepth, pixelRatio: window.devicePixelRatio },
      viewport: { width: window.innerWidth, height: window.innerHeight },
      device: { mobile, touch: (nav.maxTouchPoints||0)>0, cores: nav.hardwareConcurrency || null, memory_gb: nav.deviceMemory || null },
      connection: { effectiveType: conn.effectiveType, downlink: conn.downlink, rtt: conn.rtt, saveData: conn.saveData },
      standalone: window.matchMedia('(display-mode: standalone)').matches || nav.standalone === true,
      referrer: document.referrer || null,
      time: new Date().toISOString()
    };
  }

  function autoAdapt(){
    const c = detectClientEnv();
    const w = c.viewport.width || c.screen.width || 1024;
    const cls = document.documentElement.classList;
    cls.toggle('device-mobile', !!c.device.mobile);
    cls.toggle('device-desktop', !c.device.mobile);
    cls.toggle('viewport-sm', w < 700);
    cls.toggle('viewport-md', w >= 700 && w < 1100);
    cls.toggle('viewport-lg', w >= 1100);
    cls.toggle('standalone-app', !!c.standalone);
    const orient = (w < (c.viewport.height||w)) ? 'portrait' : 'landscape';
    document.documentElement.dataset.orientation = orient;
    document.documentElement.dataset.device = c.device.mobile ? 'mobile' : 'desktop';
    state.adapt = { class: [...cls], orientation: orient, breakpoint: w<700?'sm':(w<1100?'md':'lg') };
    return c;
  }

  async function apiCall(path, body){
    try {
      const opts = body ? { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) } : { method:'GET' };
      const r = await fetch(path, opts);
      if(!r.ok) throw new Error('api '+r.status);
      return await r.json();
    } catch(e){ return null; }
  }

  async function syncEnv(client){
    const baseline = await fetch('./../environment.json', {cache:'no-store'}).then(r=>r.ok?r.json():null).catch(()=>null)
      || await fetch('./environment.json', {cache:'no-store'}).then(r=>r.ok?r.json():null).catch(()=>null);
    const payload = {
      client,
      paths: { pageout: location.pathname, href: location.href, origin: location.origin },
      data_paths: { local_env: 'build/web/data/env/environment.json', api_env: '/api/env', state_local: 'localStorage:spatial-avy-env' },
      fill: { auto_adapt: state.adapt, install_ready: !!state.deferredPrompt, service_worker: 'supported' in navigator },
      state: { last_visit: new Date().toISOString(), page: 'gta6' }
    };
    let apiRes = await apiCall('/api/env', payload);
    if(!apiRes){ apiRes = await apiCall('/api/env?save=1'); }
    const merged = apiRes && apiRes.env ? apiRes.env : (baseline ? { ...baseline, environment: { ...(baseline.environment||{}), client, runtime_fallback:true } } : { environment:{ client } });
    state.env = merged;
    try { localStorage.setItem('spatial-avy-env', JSON.stringify({ saved_at: new Date().toISOString(), env: merged })); } catch {}
    renderEnv(merged, !!apiRes);
    return merged;
  }

  function renderEnv(env, viaApi){
    const sum = {
      api: viaApi ? 'connected (/api/env)' : 'fallback (local/static)',
      saved_to: (env && env._state_path) || (viaApi ? 'api/runtime' : 'localStorage'),
      page: location.pathname,
      device: env && env.environment && env.environment.client && env.environment.client.device,
      viewport: env && env.environment && env.environment.client && env.environment.client.viewport,
      paths: env && env.environment && env.environment.paths,
      updated_at: env && (env.updated_at || env.generated_at)
    };
    setText('env-status', viaApi ? 'General API connected · env saved' : 'General API unavailable · env saved locally');
    setText('env-json', JSON.stringify(sum, null, 2));
    const full = document.getElementById('env-full'); if(full) full.textContent = JSON.stringify(env, null, 2);
  }

  function renderAds(){
    const slots = document.querySelectorAll('[data-ad-slot]');
    slots.forEach((el, i) => {
      const slot = el.getAttribute('data-ad-slot') || ('slot-'+i);
      const label = el.getAttribute('data-ad-label') || 'Sponsored / Partner';
      el.innerHTML = `
        <div class="ad-shell" data-slot="${slot}">
          <div class="ad-label">${label}</div>
          <div class="ad-loader"><span></span><span></span><span></span></div>
          <div class="ad-body">
            <div class="ad-creative">
              <strong>Leonida Network</strong>
              <div>Adaptive ad loader ready · slot <code>${slot}</code></div>
              <small>Auto-filled from environment/config · safe placeholder (no third-party secrets)</small>
            </div>
            <a class="ad-cta" href="https://www.rockstargames.com/VI" target="_blank" rel="noopener">Learn More</a>
          </div>
        </div>`;
      setTimeout(()=>{ el.classList.add('ad-loaded'); const loader = el.querySelector('.ad-loader'); if(loader) loader.style.display='none'; }, 900 + i*500);
    });
  }

  async function registerSW(){
    if(!('serviceWorker' in navigator)) return null;
    try { return await navigator.serviceWorker.register('./sw.js', { scope: './' }); } catch(e){ return null; }
  }

  function setupInstall(){
    const btn = document.getElementById('btn-install');
    const status = document.getElementById('install-status');
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault(); state.deferredPrompt = e;
      if(btn){ btn.disabled = false; btn.textContent = 'Install to Device'; }
      if(status) status.textContent = 'Install prompt ready. Tap to install this app to your device.';
    });
    window.addEventListener('appinstalled', () => {
      state.installed = true; state.deferredPrompt = null;
      if(btn){ btn.textContent = 'Installed'; btn.disabled = true; }
      if(status) status.textContent = 'Installed to device. Launch from your home screen/app list.';
    });
    if(btn){
      btn.addEventListener('click', async () => {
        if(state.deferredPrompt){
          state.deferredPrompt.prompt();
          try { await state.deferredPrompt.userChoice; } catch {}
          state.deferredPrompt = null;
        } else {
          if(status) status.textContent = 'Install prompt not available in this browser/context. Use browser menu: “Add to Home Screen” / “Install App”.';
        }
      });
    }
  }

  function setupDownload(){
    const status = document.getElementById('download-status');
    const btns = [document.getElementById('btn-download'), document.getElementById('btn-download-panel')].filter(Boolean);
    if(!btns.length) return;
    const staticHref = new URL('./install-package.json', location.href).href;

    function triggerDownload(blob, name){
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = name; a.rel = 'noopener';
      a.style.display = 'none';
      document.body.appendChild(a); a.click();
      setTimeout(()=>{ try{ URL.revokeObjectURL(url); }catch{} a.remove(); }, 2500);
    }

    async function doDownload(e){
      if(e){ e.preventDefault(); e.stopPropagation(); }
      try {
        if(status) status.textContent = 'Preparing install/download payload…';
        const client = detectClientEnv();
        const payload = {
          app: 'GTA VI Leonida — Spatial Avy Pageout',
          generated_at: new Date().toISOString(),
          env: state.env,
          client,
          adapt: state.adapt,
          assets: { page: location.href, manifest: new URL('./manifest.webmanifest', location.href).href, hero: new URL('./assets/hero.png', location.href).href },
          install: { pwa: true, service_worker: './sw.js', api_env: '/api/env' }
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], {type:'application/json'});
        triggerDownload(blob, 'gta6-leonida-install-package.json');
        if(status) status.textContent = 'Download started (install package JSON). For full device install use “Install to Device” (PWA).';
      } catch(err){
        try { window.location.href = staticHref; } catch {}
        if(status) status.textContent = 'Opened install package download. If blocked, use the direct download link.';
      }
    }

    btns.forEach(btn => {
      if(btn.tagName === 'A'){ btn.href = './install-package.json'; btn.setAttribute('download','gta6-leonida-install-package.json'); btn.target = '_blank'; }
      btn.addEventListener('click', doDownload);
    });
  }

  async function init(){
    const client = autoAdapt();
    renderAds();
    setupInstall();
    setupDownload();
    await registerSW();
    await syncEnv(client);
    window.addEventListener('resize', () => { autoAdapt(); if(state.env) syncEnv(detectClientEnv()); });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.GTA6Install = { state, detectClientEnv, syncEnv, autoAdapt };
})();
