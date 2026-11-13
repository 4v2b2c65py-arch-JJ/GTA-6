async function loadJSON(path){ try{ const r=await fetch(path,{cache:'no-store'}); if(!r.ok) throw 0; return await r.json(); }catch(e){ return null; } }
function esc(s){ return String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
function show(id,data){ const el=document.getElementById(id); if(el) el.textContent = data?JSON.stringify(data,null,2):'unavailable'; }
function makeCard(c){ return `<div class="card"><h3>${esc(c.title||c.card_id||c.name||c.id)}</h3><p>${esc(c.type||c.class||c.mode_id||'item')} · ${c.enabled===false?'disabled':'active'}</p></div>`; }
function addThumb(container, src, cap){
  const d=document.createElement('div'); d.className='thumb';
  const img=document.createElement('img'); img.src=src; img.loading='lazy'; img.alt=cap;
  img.onerror=()=>{img.style.display='none'};
  const c=document.createElement('div'); c.className='cap'; c.textContent=cap;
  d.appendChild(img); d.appendChild(c); container.appendChild(d);
}
function renderBars(containerId, bandsObj){
  const el=document.getElementById(containerId); if(!el||!bandsObj) return;
  el.innerHTML = Object.entries(bandsObj).map(([k,v])=>{
    const pct=Math.max(0,Math.min(100, (Number(v)||0)*100));
    return `<div class="eq-band"><div class="label">${esc(k)}</div><div class="meter"><div class="fill" style="height:${pct}%"></div></div><div class="val">${Number(v).toFixed ? Number(v).toFixed(2):v}</div></div>`;
  }).join('');
}
function renderEQ(eq){
  if(!eq) return;
  show('eq-data', eq);
  const q=document.getElementById('eq-quality');
  if(q){ const orig=eq.original_sound_quality && (eq.original_sound_quality.enabled!==false); q.textContent = orig ? 'Original sound quality: ON' : 'Original sound quality: configurable'; }
  const sel=document.getElementById('eq-preset'); const bandsEl=document.getElementById('eq-bands');
  if(sel){
    sel.innerHTML=(eq.presets||[]).map(p=>`<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
    sel.value = eq.active_preset || (eq.presets&&eq.presets[0]&&eq.presets[0].id) || '';
    const draw=(id)=>{
      const p=(eq.presets||[]).find(x=>x.id===id) || (eq.presets||[])[0];
      if(!p||!bandsEl) return;
      bandsEl.innerHTML=Object.entries(p.gains||{}).map(([k,db])=>{
        const pct=Math.max(0,Math.min(100, ((Number(db)+12)/24)*100));
        return `<div class="eq-band"><div class="label">${esc(k)}</div><div class="meter"><div class="fill" style="height:${pct}%"></div></div><div class="val">${Number(db)>0?'+':''}${db} dB</div></div>`;
      }).join('');
    };
    draw(sel.value); sel.addEventListener('change',()=>draw(sel.value));
  }
}
function renderSoundboard(sb){
  show('soundboard-data', sb);
  const el=document.getElementById('soundboard'); if(!el||!sb||!sb.pads) return;
  el.innerHTML=sb.pads.map(p=>`<button class="pad" style="border-color:${esc(p.color||'#2a3648')}" title="${esc(p.ref||'')}"><div>${esc(p.label)}</div><small>${esc(p.type)} · ${esc(p.source)} ${p.gain_db!=null?('· '+p.gain_db+'dB'):''}</small></button>`).join('');
}
async function boot(){
  document.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); document.getElementById('tab-'+b.dataset.tab).classList.add('active');
  }));

  const deck = await loadJSON('./data/systems/character_hub/deck/deck.json');
  const loadout = await loadJSON('./data/narrative/characters/default_loadout.json');
  const runtime = await loadJSON('./data/systems/runtime/game_world_runtime.json');
  const build = await loadJSON('./data/build/game/build.json');
  const world = await loadJSON('./data/home_world/home_world_index.json');
  const timeline = await loadJSON('./data/systems/grid_store/timeline_pockets.json');
  const audioState = await loadJSON('./data/systems/audio/install_state.json');
  const soundtrack = await loadJSON('./data/systems/audio/soundtrack/soundtrack.json');
  const vocals = await loadJSON('./data/assets/audio/voice/vocals/vocals_index.json');
  const musicState = await loadJSON('./data/systems/audio/music/music_state.json') || await loadJSON('./data/assets/audio/music/music_manifest.json');
  const spotifyPeers = await loadJSON('./data/systems/audio/music/spotify_track_peers.json');
  const musicPlaylist = await loadJSON('./data/systems/audio/music/playlist_sorted.json') || await loadJSON('./data/assets/audio/music/music_playlist_sorted.json');
  const eqPresets = await loadJSON('./data/systems/audio/music/eq_presets.json') || await loadJSON('./data/assets/audio/music/eq_presets.json');
  const soundboard = await loadJSON('./data/systems/audio/music/soundboard.json') || await loadJSON('./data/assets/audio/music/soundboard.json');
  const frequencyState = await loadJSON('./data/systems/audio/music/frequency_state.json') || await loadJSON('./data/assets/audio/music/frequency_state.json');
  const speakerLevels = await loadJSON('./data/systems/audio/music/speaker_output_levels.json') || await loadJSON('./data/assets/audio/music/speaker_output_levels.json');
  const dlc = await loadJSON('./data/assets/game_assets/dlc/dlc_install_manifest.json');
  const images = await loadJSON('./data/assets/images/images_manifest.json');
  const icons = await loadJSON('./data/assets/images/icons_manifest.json');
  const identity = await loadJSON('./data/assets/identity/identity_manifest.json') || await loadJSON('./assets/identity_manifest.json');
  const transportInjection = await loadJSON('./data/injection/transport_geo_injection.json') || await loadJSON('./assets/transport_geo_injection.json');
  const vehicles = await loadJSON('./data/systems/world/transportation/vehicles.json') || await loadJSON('./data/assets/game_assets/transportation/vehicles.json');
  const transportation = await loadJSON('./data/systems/world/transportation/transportation.json') || await loadJSON('./data/assets/game_assets/transportation/transportation.json');
  const geo = await loadJSON('./data/systems/world/geo/geo_injection.json') || await loadJSON('./data/assets/game_assets/geo/geo_injection.json');

  if(deck && deck.cards){ document.getElementById('deck-cards').innerHTML = deck.cards.map(makeCard).join(''); }
  show('loadout', loadout); show('runtime', runtime); show('build', build);
  show('world', world); show('timeline', timeline);
  show('audio-state', audioState); show('soundtrack', soundtrack); show('vocals', vocals);
  show('music-state', musicState); show('spotify-peers', spotifyPeers); show('music-playlist', musicPlaylist);
  renderEQ(eqPresets); renderSoundboard(soundboard);
  show('frequency-state', frequencyState || speakerLevels);
  const spk = (frequencyState && frequencyState.speaker_output && frequencyState.speaker_output.speaker_levels && frequencyState.speaker_output.speaker_levels.bands) ? frequencyState.speaker_output.speaker_levels.bands : (speakerLevels && speakerLevels.speaker_levels && speakerLevels.speaker_levels.bands ? speakerLevels.speaker_levels.bands : null);
  renderBars('freq-bars', spk);
  show('dlc', dlc); show('images', images); show('icons', icons); show('identity', identity);
  show('transport-injection', transportInjection); show('vehicles', vehicles); show('transportation', transportation); show('geo', geo);

  const pc=document.getElementById('playlist-cards');
  if(pc && musicPlaylist && musicPlaylist.tracks){ pc.innerHTML = musicPlaylist.tracks.slice(0,30).map(t=>`<div class="card"><h3>#${t.sort_rank||''} ${esc(t.title)}</h3><p>${esc(t.artist||'')} · ${esc((t.mood||[]).join(', '))}</p><p>${esc(t.zone||'')} ${esc(t.beat||'')} · score ${t._sort_score??''} · ${esc(t.source||'')}</p></div>`).join(''); }
  const vc=document.getElementById('vehicle-cards');
  if(vc && vehicles && vehicles.vehicles){ vc.innerHTML = vehicles.vehicles.map(v=>`<div class="card"><h3>${esc(v.name)}</h3><p>${esc(v.class)} · ${esc(v.base_game)} · ${esc(v.source||'base')}</p><p>${esc((v.tags||[]).join(', '))}</p></div>`).join(''); }
  const gc=document.getElementById('geo-cards');
  if(gc && geo){
    const regs=(geo.regions||[]).map(r=>`<div class="card"><h3>${esc(r.name)}</h3><p>${esc(r.region_id)} · ${r.center?`lat ${r.center.lat}, lon ${r.center.lon}`:''}</p><p>${esc(r.real_world_ref||'')}</p></div>`).join('');
    const hubs=(geo.transport_hubs||[]).map(h=>`<div class="card"><h3>${esc(h.hub_id)}</h3><p>${esc(h.type)} · ${esc(h.region_id)}</p><p>${esc((h.services||[]).join(', '))}</p></div>`).join('');
    gc.innerHTML = regs + hubs;
  }

  const story = { story_novel_data: identity?.story_novel_data, ai_integrated_data: identity?.ai_integrated_data };
  show('story-identity', story);
  const refs = (world && world.narrative_refs) ? world.narrative_refs : {};
  const ul=document.getElementById('narrative-refs');
  if(ul){ Object.entries(refs).forEach(([k,v])=>{ const li=document.createElement('li'); li.innerHTML=`<strong>${esc(k)}</strong>: <code>${esc(v)}</code>`; ul.appendChild(li); }); }

  const ig=document.getElementById('image-gallery');
  if(ig && images && images.installed){ images.installed.slice(0,80).forEach(it=>{ if(it.installed_to) addThumb(ig, './data/'+it.installed_to, it.installed_to.split('/').pop()); }); }
  const ic=document.getElementById('icon-gallery');
  if(ic && icons && icons.icons){ icons.icons.forEach(it=>addThumb(ic, './data/'+it.file, it.name||it.id)); }
  ['assets/identity_manifest.json','./assets/insignia/og_image.png','./assets/icons/icon-512.png'].forEach((src,i)=>{ if(i>0 && ic) addThumb(ic, src, src.split('/').pop()); });
}
boot();
