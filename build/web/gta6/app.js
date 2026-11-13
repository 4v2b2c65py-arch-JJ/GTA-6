const { createApp } = Vue;
createApp({
  data() {
    return {
      loading: true,
      fading: false,
      ready: false,
      progress: 0,
      statusText: 'Initializing State of Leonida…',
      lightbox: null,
      characters: [
        {id:'jason_lucia', name:'Jason & Lucia', role:'Protagonists', desc:'A criminal conspiracy across the state of Leonida forces them to rely on each other more than ever if they want to make it out alive.', img:'./assets/characters/jason_lucia.png'},
        {id:'jason', name:'Jason Duval', role:'Protagonist', desc:'Wants an easy life, but things just keep getting harder. Grew up around grifters and crooks; after the Army he worked for local drug runners in the Keys. Meeting Lucia could be the best or worst thing to happen to him.', img:'./assets/characters/jason.png'},
        {id:'lucia', name:'Lucia Caminos', role:'Protagonist', desc:"Lucia's father taught her to fight early. Fighting for her family landed her in the Leonida Penitentiary; luck got her out. Fresh out of prison and ready to change the odds — committed to her plan no matter what it takes.", img:'./assets/characters/lucia.png'},
        {id:'cal', name:'Cal Hampton', role:"Jason's Friend / Associate", desc:"At the low tide of America and happy there. Jason's friend and Brian's associate — Cal feels safest at home, snooping on Coast Guard comms with a few beers and private browser tabs open.", img:'./assets/characters/cal.png'},
        {id:'boobie', name:'Boobie Ike', role:'Vice City Legend', desc:"A local Vice City legend who transformed time in the streets into a legitimate empire spanning real estate, a strip club, and a recording studio — all smiles until it's time to talk business. Partnered with Dre'Quan for Only Raw Records.", img:'./assets/characters/boobie.png'},
        {id:'drequan', name:"Dre'Quan Priest", role:'Only Raw Records', desc:"Always more of a hustler than a gangster. Even while dealing on the streets, breaking into music was the goal. Now working with Boobie Ike to get a hit for Only Raw Records.", img:'./assets/characters/drequan.png'},
        {id:'realdimez', name:'Real Dimez (Bae-Luxe & Roxy)', role:'Viral Duo', desc:"Friends since high school — girls with the savvy to turn their time shaking down local dealers into cold, hard cash via spicy rap tracks and a relentless social media presence.", img:'./assets/characters/realdimez.png'},
        {id:'raul', name:'Raul Bautista', role:'Seasoned Bank Robber', desc:'Confidence, charm, and cunning — a seasoned bank robber always on the hunt for talent ready to take the risks that bring the biggest rewards.', img:'./assets/characters/raul.png'},
        {id:'brian', name:'Brian Heder', role:'Classic Drug Runner', desc:"A classic drug runner from the golden age of smuggling in the Keys. Still moving product through his boat yard with his third wife, Lori — been around long enough to let others do his dirty work.", img:'./assets/characters/brian.png'},
      ],
      locations: [
        {id:'vice_city', name:'Vice City', desc:"The sun and fun capital of America. Glamour, hustle, and greed in one city — from the pastel Art Deco hotels and bright white sands of Ocean Beach, to the bustling panaderías of Little Cuba and bootleg brands of the Tisha-Wocka flea market, out to the VC Port, cruise capital of the world.", img:'./assets/locations/vice_city.png'},
        {id:'leonida_keys', name:'Leonida Keys', desc:"Life in this tropical archipelago isn't flashy but it's easy — a gateway to paradise with some of the most beautiful and dangerous waters in all of America. Right off the doorstep of the Keys.", img:'./assets/locations/leonida_keys.png'},
        {id:'grassrivers', name:'Grassrivers', desc:"The untamable jewel of Leonida's crown. You never know what lies beneath the surface of this primordial expanse — the gators may be the most famous attraction, but there are far deadlier predators and weirder discoveries among the mangroves.", img:'./assets/locations/grassrivers.png'},
        {id:'port_gellhorn', name:'Port Gellhorn', desc:"Cheap motels, shuttered attractions, and empty strip malls won't bring the tourists back, but there's a new economy in this once-popular vacation spot — fueled by malt liquor, painkillers, and truck stop energy drinks. Sling your haul, or be hauled in.", img:'./assets/locations/port_gellhorn.png'},
        {id:'ambrosia', name:'Ambrosia', desc:"In the heart of Leonida, American industry and old school values still reign supreme — whatever the cost. The Allied Crystal sugar refinery provides the jobs, while the local biker gang provides almost everything else.", img:'./assets/locations/ambrosia.png'},
        {id:'mount_kalaga', name:'Mount Kalaga', desc:"A national landmark on the state's northern border offering prime hunting, fishing, and off-road trails. In the lush surrounding backwoods, hillbilly mystics and paranoid radicals make their home — far from the prying eyes of the government.", img:'./assets/locations/mount_kalaga.png'},
      ],
      editions: [
        {id:'standard', name:'Standard Edition', price:'$79.99', img:'./assets/editions/standard.png', featured:false, items:[
          'Base game: Jason & Lucia story across the State of Leonida & Vice City',
          'Full single-player experience (1 player, offline play, Remote Play supported)',
          'Pre-order bonus: Vintage Vice City Pack (all pre-orders/purchases before Nov 20, 2026)',
          'Digital pre-order bonus: 1 free month of GTA+',
          'PS5: DualSense haptics/adaptive triggers/speaker, Tempest 3D audio, fast SSD loading, PS5 Pro Enhanced'
        ]},
        {id:'ultimate', name:'Ultimate Edition', price:'$99.99', img:'./assets/editions/ultimate.png', featured:true, items:[
          "’95 Grotti Cheetah; Shitzu Squalo; ’67 Vapid Dominator Buggy & Paradise Garage",
          "Jason's safehouse vehicles: Dinka Enduro motorcycle & Crest Kayak",
          'Hawk & Little Morgan revolvers (Vercetti Estate stylings, engraved, high-performance scope)',
          "Personalized weapon variants: Jason's Girardi ES9 & Lucia's Klose K17 pistols",
          'Vice City Style & Goodtime Gear (exclusive outfits, hairstyles, tattoos)',
          'Ganado Retro Build & Classic Car Collection special commissions (Wyman)',
          "Rideout Customs, Sara's Unisex Salon, Stock 305, Electric Fang Tattoo, One-Eyed Willie's"
        ]},
        {id:'vintage_vc', name:'Vintage Vice City Pack', price:'Pre-order Bonus', img:'./assets/editions/vintage_vc.png', featured:false, items:[
          "’55 Vapid Stanier sedan (classic retro ride)",
          'Exclusive vintage looks & hairstyles for Jason and Lucia',
          'Vintage weapon pattern',
          'Retro Vice City vibes across Leonida',
          'Included with all pre-orders/purchases before Nov 20, 2026'
        ]},
      ],
      gallery: [
        {src:'./assets/hero.png', alt:'GTA VI Hero — State of Leonida'},
        {src:'./assets/loading_screen.png', alt:'GTA VI Loading — Enter Leonida'},
        {src:'./assets/keyart.jpg', alt:'GTA VI Key Art'},
        {src:'./assets/logo.png', alt:'GTA VI Logo'},
        {src:'./assets/characters/jason_lucia.png', alt:'Jason & Lucia'},
        {src:'./assets/characters/jason.png', alt:'Jason Duval'},
        {src:'./assets/characters/lucia.png', alt:'Lucia Caminos'},
        {src:'./assets/characters/cal.png', alt:'Cal Hampton'},
        {src:'./assets/characters/boobie.png', alt:'Boobie Ike'},
        {src:'./assets/characters/drequan.png', alt:"Dre'Quan Priest"},
        {src:'./assets/characters/realdimez.png', alt:'Real Dimez'},
        {src:'./assets/characters/raul.png', alt:'Raul Bautista'},
        {src:'./assets/characters/brian.png', alt:'Brian Heder'},
        {src:'./assets/locations/vice_city.png', alt:'Vice City'},
        {src:'./assets/locations/leonida_keys.png', alt:'Leonida Keys'},
        {src:'./assets/locations/grassrivers.png', alt:'Grassrivers'},
        {src:'./assets/locations/port_gellhorn.png', alt:'Port Gellhorn'},
        {src:'./assets/locations/ambrosia.png', alt:'Ambrosia'},
        {src:'./assets/locations/mount_kalaga.png', alt:'Mount Kalaga'},
        {src:'./assets/screenshots/s01_vice_skyline.png', alt:'Vice City Skyline'},
        {src:'./assets/screenshots/s02_keys_water.png', alt:'Leonida Keys Waters'},
        {src:'./assets/screenshots/s03_grassrivers.png', alt:'Grassrivers Mangroves'},
        {src:'./assets/screenshots/s04_port_gellhorn.png', alt:'Port Gellhorn Strip'},
        {src:'./assets/screenshots/s05_ambrosia.png', alt:'Ambrosia Refinery'},
        {src:'./assets/screenshots/s06_mount_kalaga.png', alt:'Mount Kalaga Trails'},
        {src:'./assets/screenshots/s07_jason_lucia.png', alt:'Jason & Lucia — Partners'},
        {src:'./assets/screenshots/s08_heist.png', alt:'The Score'},
        {src:'./assets/editions/standard.png', alt:'Standard Edition'},
        {src:'./assets/editions/ultimate.png', alt:'Ultimate Edition'},
        {src:'./assets/editions/vintage_vc.png', alt:'Vintage Vice City Pack'},
      ]
    };
  },
  methods: {
    bg(url){ return { backgroundImage: `url(${url})` }; },
    enter(){
      if(!this.ready) return;
      this.fading = true;
      setTimeout(()=>{ this.loading = false; window.scrollTo(0,0); }, 650);
    }
  },
  mounted(){
    const steps = [
      [12,'Loading Vice City skyline…'],[24,'Streaming Leonida Keys waters…'],[36,'Mounting Grassrivers & Port Gellhorn…'],
      [48,'Loading characters: Jason & Lucia…'],[60,'Syncing Cal, Boobie, Dre’Quan, Real Dimez, Raul, Brian…'],
      [72,'Preparing editions, vehicles & bonuses…'],[84,'Injecting world, audio & runtime data…'],[96,'Finalizing assets & package state…'],[100,'Welcome to Leonida.']
    ];
    let i=0;
    const tick=()=>{
      if(i>=steps.length){ this.progress=100; this.statusText='Welcome to Leonida.'; this.ready=true; return; }
      this.progress = steps[i][0]; this.statusText = steps[i][1]; i++;
      setTimeout(tick, 260 + Math.random()*220);
    };
    setTimeout(tick, 300);
    // preload key images
    ['./assets/hero.png','./assets/loading_screen.png','./assets/characters/jason_lucia.png'].forEach(s=>{ const im=new Image(); im.src=s; });
  }
}).mount('#app');
