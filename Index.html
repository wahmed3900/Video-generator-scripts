<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Building Reel — Product Résumé</title>
<meta name="description" content="Building Reel turns any topic into a scripted, voiced, ready-to-post short video. Free 3 per month, then $40/month Pro.">
<style>
  /* ---------- tokens ---------- */
  :root{
    --bg:#0a0b10;
    --panel:rgba(255,255,255,.035);
    --line:rgba(255,255,255,.09);
    --line-strong:rgba(255,255,255,.16);
    --ink:#eef1f7;
    --muted:#9aa3b2;
    --dim:#6b7385;
    --a1:#7c5cff;
    --a2:#22d3ee;
    --a3:#ff5c8a;
    --radius:16px;
    --maxw:1080px;
    --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Inter,Roboto,"Helvetica Neue",Arial,sans-serif;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  }

  *,*::before,*::after{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{
    margin:0;
    font-family:var(--font);
    color:var(--ink);
    background:var(--bg);
    line-height:1.6;
    letter-spacing:.005em;
    -webkit-font-smoothing:antialiased;
    overflow-x:hidden;
  }
  a{color:inherit}
  h1,h2,h3,h4{margin:0;line-height:1.15;letter-spacing:-.02em;font-weight:650}
  p{margin:0}
  ul{margin:0;padding:0;list-style:none}

  .wrap{width:100%;max-width:var(--maxw);margin-inline:auto;padding-inline:24px}

  .grad{
    background:linear-gradient(100deg,var(--a1),var(--a2) 55%,var(--a3));
    -webkit-background-clip:text;background-clip:text;color:transparent;
  }

  /* ---------- ambient background ---------- */
  .glow{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}
  .glow span{position:absolute;border-radius:50%;filter:blur(90px);opacity:.5}
  .glow .g1{width:620px;height:620px;top:-260px;left:-160px;background:radial-gradient(circle,#7c5cff55,transparent 70%)}
  .glow .g2{width:520px;height:520px;top:-120px;right:-180px;background:radial-gradient(circle,#22d3ee3d,transparent 70%)}
  .glow .g3{width:640px;height:640px;bottom:-340px;left:35%;background:radial-gradient(circle,#ff5c8a2e,transparent 70%)}
  .grid-lines{
    position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.35;
    background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);
    background-size:64px 64px;
    mask-image:radial-gradient(ellipse 90% 60% at 50% 0%,#000 20%,transparent 80%);
    -webkit-mask-image:radial-gradient(ellipse 90% 60% at 50% 0%,#000 20%,transparent 80%);
  }

  .page{position:relative;z-index:1}

  /* ---------- hero ---------- */
  .hero{padding:56px 0 40px}
  .topbar{
    display:flex;align-items:center;justify-content:space-between;
    gap:16px;flex-wrap:wrap;margin-bottom:44px;
  }
  .brand{display:flex;align-items:center;gap:12px;font-weight:640;letter-spacing:-.01em}
  .mark{
    width:36px;height:36px;flex:none;border-radius:11px;
    display:grid;place-items:center;font-size:13px;color:#fff;
    background:linear-gradient(135deg,var(--a1),var(--a2));
    box-shadow:0 8px 24px -8px #7c5cffaa, inset 0 1px 0 #ffffff44;
  }
  .brand small{display:block;font-weight:450;font-size:11.5px;color:var(--dim);letter-spacing:.06em;text-transform:uppercase}

  .badge{
    display:inline-flex;align-items:center;gap:9px;
    font-size:12.5px;font-weight:550;letter-spacing:.01em;
    padding:8px 14px;border-radius:999px;
    color:#d9dced;
    background:rgba(255,255,255,.05);
    border:1px solid var(--line-strong);
    backdrop-filter:blur(8px);
    transition:all .2s ease;
  }
  .badge.pro{
    background:linear-gradient(100deg,rgba(124,92,255,.25),rgba(34,211,238,.15));
    border-color:rgba(124,92,255,.5);
    color:#fff;
  }
  .dot{
    width:7px;height:7px;border-radius:50%;background:#3ee98a;flex:none;
    box-shadow:0 0 0 0 #3ee98a88;animation:pulse 2.4s infinite;
  }
  @keyframes pulse{
    0%{box-shadow:0 0 0 0 #3ee98a88}
    70%{box-shadow:0 0 0 9px #3ee98a00}
    100%{box-shadow:0 0 0 0 #3ee98a00}
  }

  h1{
    font-size:clamp(2.05rem,5.4vw,3.5rem);
    font-weight:700;
    max-width:19ch;
    margin-bottom:20px;
  }
  .lede{
    max-width:58ch;color:var(--muted);font-size:clamp(1rem,1.6vw,1.1rem);
  }
  .lede b{color:var(--ink);font-weight:600}

  .cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}
  .btn{
    display:inline-flex;align-items:center;gap:9px;
    padding:13px 22px;border-radius:12px;border:1px solid transparent;
    font:inherit;font-weight:600;font-size:14.5px;
    text-decoration:none;cursor:pointer;
    transition:transform .18s ease, box-shadow .18s ease, background .18s ease, border-color .18s ease;
  }
  .btn-primary{
    color:#0a0b10;
    background:linear-gradient(100deg,#b7a6ff,#7c5cff 35%,#22d3ee);
    box-shadow:0 14px 34px -14px #7c5cffcc;
  }
  .btn-primary:hover{transform:translateY(-2px);box-shadow:0 20px 42px -16px #7c5cff}
  .btn-ghost{
    color:var(--ink);background:rgba(255,255,255,.04);border-color:var(--line-strong);
  }
  .btn-ghost:hover{background:rgba(255,255,255,.08);transform:translateY(-2px)}
  .btn:focus-visible{outline:2px solid var(--a2);outline-offset:3px}
  .btn:disabled{opacity:.5;cursor:not-allowed;transform:none}

  /* ---------- metrics strip ---------- */
  .metrics{
    display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
    margin-top:46px;
    background:var(--line);border:1px solid var(--line);
    border-radius:var(--radius);overflow:hidden;
  }
  .metric{background:#0c0e15;padding:20px 20px 18px}
  .metric .n{
    font-family:var(--mono);font-size:1.5rem;font-weight:600;letter-spacing:-.03em;
    background:linear-gradient(120deg,#fff,#b9c2d6);-webkit-background-clip:text;background-clip:text;color:transparent;
  }
  .metric .l{font-size:12px;color:var(--dim);letter-spacing:.09em;text-transform:uppercase;margin-top:4px}

  /* ---------- layout ---------- */
  .body-grid{
    display:grid;grid-template-columns:300px 1fr;gap:44px;
    padding:24px 0 80px;
  }
  aside{display:flex;flex-direction:column;gap:26px}
  @media (min-width:961px){
    aside{position:sticky;top:28px;align-self:start}
  }

  .sec{margin-bottom:44px}
  .sec:last-child{margin-bottom:0}
  .sec-title{
    display:flex;align-items:center;gap:12px;
    font-size:11.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
    color:var(--dim);margin-bottom:18px;
  }
  .sec-title::after{content:"";flex:1;height:1px;background:var(--line)}

  .card{
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:var(--radius);
    padding:22px;
  }
  .card + .card{margin-top:14px}

  /* ---------- contact list ---------- */
  .contact li{display:flex;gap:11px;align-items:baseline;padding:9px 0;border-bottom:1px dashed var(--line);font-size:14px}
  .contact li:last-child{border-bottom:0}
  .contact .k{color:var(--dim);font-size:11px;letter-spacing:.1em;text-transform:uppercase;width:74px;flex:none;padding-top:2px}
  .contact a{text-decoration:none;border-bottom:1px solid transparent}
  .contact a:hover{border-bottom-color:var(--a2);color:#fff}

  /* ---------- chips ---------- */
  .chips{display:flex;flex-wrap:wrap;gap:8px}
  .chip{
    font-size:12.5px;font-weight:520;padding:7px 12px;border-radius:9px;
    background:rgba(255,255,255,.045);
    border:1px solid var(--line);
    color:#c9d0dd;
  }
  .chip:hover{border-color:var(--line-strong);color:#fff}

  /* ---------- pipeline ---------- */
  .step{
    display:grid;grid-template-columns:40px 1fr;gap:18px;
    padding:20px 0;border-bottom:1px solid var(--line);
  }
  .step:last-child{border-bottom:0;padding-bottom:0}
  .step:first-child{padding-top:4px}
  .num{
    width:36px;height:36px;border-radius:11px;display:grid;place-items:center;
    font-family:var(--mono);font-size:13px;font-weight:600;color:#cbbdff;
    background:linear-gradient(150deg,rgba(124,92,255,.22),rgba(34,211,238,.14));
    border:1px solid rgba(124,92,255,.35);
  }
  .step h3{font-size:1.02rem;margin-bottom:6px}
  .step p{color:var(--muted);font-size:14.5px}
  .step .tag{
    display:inline-block;margin-top:9px;font-family:var(--mono);font-size:11px;
    color:var(--dim);letter-spacing:.05em;
  }

  /* ---------- features ---------- */
  .features{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
  .feature{
    padding:18px;border-radius:14px;background:var(--panel);
    border:1px solid var(--line);transition:border-color .18s ease,transform .18s ease;
  }
  .feature:hover{border-color:var(--line-strong);transform:translateY(-2px)}
  .feature h4{font-size:14.5px;margin-bottom:6px;display:flex;align-items:center;gap:8px}
  .feature h4 i{
    font-style:normal;font-size:12px;width:22px;height:22px;flex:none;border-radius:7px;
    display:grid;place-items:center;background:rgba(124,92,255,.16);
    border:1px solid rgba(124,92,255,.3);
  }
  .feature p{font-size:13.5px;color:var(--muted);line-height:1.55}

  /* ---------- pricing ---------- */
  .price{
    border:1px solid var(--line);border-radius:var(--radius);padding:18px;
    background:var(--panel);
    position:relative;
    transition:all .2s ease;
  }
  .price + .price{margin-top:12px}
  .price.hot{
    border-color:rgba(124,92,255,.45);
    background:linear-gradient(160deg,rgba(124,92,255,.14),rgba(34,211,238,.06));
    box-shadow:0 18px 40px -26px #7c5cff;
  }
  .price .row{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
  .price .name{font-size:13px;font-weight:600;letter-spacing:.02em}
  .price .amt{font-family:var(--mono);font-size:1.25rem;font-weight:600;letter-spacing:-.02em}
  .price .amt span{font-size:11.5px;color:var(--dim);font-weight:400}
  .price ul{margin-top:12px;display:flex;flex-direction:column;gap:7px}
  .price li{font-size:13px;color:var(--muted);display:flex;gap:9px;align-items:flex-start}
  .price li::before{content:"✓";color:var(--a2);font-size:11px;flex:none;margin-top:4px}
  .price .upgrade-btn{
    display:block;width:100%;margin-top:14px;text-align:center;
    padding:10px 14px;border-radius:10px;font-size:13px;font-weight:600;
    text-decoration:none;cursor:pointer;border:1px solid transparent;
    color:#0a0b10;
    background:linear-gradient(100deg,#b7a6ff,#7c5cff 40%,#22d3ee);
    transition:transform .18s ease, box-shadow .18s ease;
  }
  .price .upgrade-btn:hover{transform:translateY(-2px);box-shadow:0 14px 30px -12px #7c5cff}

  /* ---------- usage tracker ---------- */
  .usage-card{
    background:linear-gradient(160deg,rgba(124,92,255,.10),rgba(34,211,238,.04));
    border:1px solid rgba(124,92,255,.28);
    border-radius:var(--radius);
    padding:18px;
    margin-bottom:22px;
  }
  .usage-head{
    display:flex;justify-content:space-between;align-items:center;gap:12px;
    margin-bottom:12px;
  }
  .usage-head .label{
    font-size:11.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--dim);
  }
  .usage-head .count{
    font-family:var(--mono);font-size:14px;font-weight:600;color:#fff;
  }
  .usage-bar{
    height:8px;border-radius:999px;background:rgba(255,255,255,.07);
    overflow:hidden;
  }
  .usage-bar .fill{
    height:100%;border-radius:999px;width:0%;
    background:linear-gradient(90deg,var(--a1),var(--a2));
    transition:width .5s cubic-bezier(.4,0,.2,1), background .3s ease;
  }
  .usage-bar .fill.warn{
    background:linear-gradient(90deg,#ffb020,#ff5c8a);
  }
  .usage-bar .fill.full{
    background:linear-gradient(90deg,#ff5c8a,#ff2d55);
  }
  .usage-note{
    font-size:12px;color:var(--dim);margin-top:10px;
  }
  .usage-note strong{color:var(--ink)}

  /* ---------- generator demo ---------- */
  .generator{
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:var(--radius);
    padding:22px;
  }
  .generator label{
    display:block;font-size:11.5px;font-weight:600;letter-spacing:.12em;
    text-transform:uppercase;color:var(--dim);margin-bottom:10px;
  }
  .generator input{
    width:100%;padding:13px 15px;border-radius:11px;
    background:rgba(0,0,0,.28);
    border:1px solid var(--line-strong);
    color:var(--ink);font:inherit;font-size:14.5px;
    outline:none;transition:border-color .18s ease, box-shadow .18s ease;
  }
  .generator input:focus{
    border-color:rgba(124,92,255,.7);
    box-shadow:0 0 0 3px rgba(124,92,255,.18);
  }
  .generator input:disabled{opacity:.5;cursor:not-allowed}
  .generator .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
  .generator .actions .btn{flex:1;justify-content:center;min-width:160px}
  .generator .output{
    margin-top:18px;padding:16px;border-radius:12px;
    background:rgba(0,0,0,.25);
    border:1px dashed var(--line-strong);
    font-size:13.5px;color:var(--muted);min-height:72px;
    display:flex;align-items:center;gap:12px;
  }
  .generator .output.working{
    color:#cbbdff;
  }
  .spinner{
    width:16px;height:16px;flex:none;border-radius:50%;
    border:2px solid rgba(124,92,255,.3);
    border-top-color:var(--a2);
    animation:spin .8s linear infinite;
  }
  @keyframes spin{to{transform:rotate(360deg)}}

  /* ---------- modal ---------- */
  .modal-overlay{
    position:fixed;inset:0;z-index:100;
    background:rgba(6,7,12,.75);
    backdrop-filter:blur(8px);
    display:none;
    align-items:center;justify-content:center;
    padding:20px;
    animation:fadeIn .22s ease;
  }
  .modal-overlay.open{display:flex}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  .modal{
    position:relative;width:100%;max-width:460px;
    background:linear-gradient(160deg,#14161f,#0c0e15);
    border:1px solid rgba(124,92,255,.4);
    border-radius:20px;
    padding:32px 28px 26px;
    box-shadow:0 40px 80px -30px #000, 0 0 60px -30px #7c5cff;
    animation:popIn .28s cubic-bezier(.34,1.56,.64,1);
  }
  @keyframes popIn{
    from{opacity:0;transform:scale(.92) translateY(12px)}
    to{opacity:1;transform:scale(1) translateY(0)}
  }
  .modal .close-x{
    position:absolute;top:14px;right:16px;
    width:30px;height:30px;border-radius:9px;
    display:grid;place-items:center;
    background:rgba(255,255,255,.05);border:1px solid var(--line);
    color:var(--muted);cursor:pointer;font-size:15px;line-height:1;
    transition:all .18s ease;
  }
  .modal .close-x:hover{background:rgba(255,255,255,.1);color:#fff}
  .modal .modal-icon{
    width:52px;height:52px;border-radius:15px;
    display:grid;place-items:center;font-size:22px;
    background:linear-gradient(140deg,rgba(255,92,138,.22),rgba(124,92,255,.18));
    border:1px solid rgba(255,92,138,.4);
    margin-bottom:18px;
  }
  .modal h2{font-size:1.35rem;margin-bottom:10px;line-height:1.25}
  .modal p.sub{color:var(--muted);font-size:14.5px;margin-bottom:22px}
  .modal .modal-price{
    display:flex;align-items:baseline;gap:8px;
    margin-bottom:20px;padding:16px;border-radius:12px;
    background:rgba(124,92,255,.08);border:1px solid rgba(124,92,255,.28);
  }
  .modal .modal-price .big{
    font-family:var(--mono);font-size:1.9rem;font-weight:700;
    letter-spacing:-.03em;color:#fff;
  }
  .modal .modal-price .per{font-size:13px;color:var(--dim)}
  .modal .modal-price .save{
    margin-left:auto;font-size:11.5px;font-weight:600;
    padding:5px 10px;border-radius:999px;
    color:#cbbdff;background:rgba(124,92,255,.18);
    border:1px solid rgba(124,92,255,.35);
    letter-spacing:.03em;
  }
  .modal ul.perks{
    display:flex;flex-direction:column;gap:10px;margin-bottom:24px;
  }
  .modal ul.perks li{
    display:flex;gap:10px;align-items:flex-start;
    font-size:13.5px;color:#c9d0dd;
  }
  .modal ul.perks li::before{
    content:"✓";color:var(--a2);font-size:11px;flex:none;margin-top:4px;
  }
  .modal .modal-actions{display:flex;flex-direction:column;gap:10px}
  .modal .modal-actions .btn{width:100%;justify-content:center}
  .modal .fine{font-size:11.5px;color:var(--dim);text-align:center;margin-top:14px}

  /* ---------- footer ---------- */
  footer{
    border-top:1px solid var(--line);
    padding:28px 0 56px;
    display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
    color:var(--dim);font-size:12.5px;
  }
  footer a{text-decoration:none;color:var(--muted)}
  footer a:hover{color:#fff}

  /* ---------- responsive ---------- */
  @media (max-width:960px){
    .body-grid{grid-template-columns:1fr;gap:8px}
    aside{position:static}
    .metrics{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:560px){
    .wrap{padding-inline:18px}
    .hero{padding-top:34px}
    .features{grid-template-columns:1fr}
    .step{grid-template-columns:32px 1fr;gap:14px}
    .num{width:30px;height:30px;border-radius:9px}
    footer{padding-bottom:40px}
    .modal{padding:26px 22px 22px}
  }

  @media (prefers-reduced-motion:reduce){
    *,*::before,*::after{animation:none!important;transition:none!important}
  }

  /* ---------- print / PDF ---------- */
  @media print{
    :root{--ink:#111;--muted:#444;--dim:#666;--line:#dcdcdc;--line-strong:#bbb}
    body{background:#fff;color:#111}
    .glow,.grid-lines,.cta,.modal-overlay,.generator,.usage-card{display:none!important}
    .hero{padding-top:0}
    .body-grid{grid-template-columns:1fr;gap:0;padding-bottom:0}
    aside{position:static}
    .card,.feature,.price,.metric{background:#fff!important;box-shadow:none!important}
    .metric .n{color:#111;-webkit-text-fill-color:#111;background:none}
    .grad{-webkit-text-fill-color:initial;color:#5b3df5;background:none}
    h1{font-size:1.9rem}
    .sec{margin-bottom:24px;break-inside:avoid}
    .step,.feature,.price{break-inside:avoid}
  }
</style>
</head>
<body>

<div class="glow" aria-hidden="true">
  <span class="g1"></span><span class="g2"></span><span class="g3"></span>
</div>
<div class="grid-lines" aria-hidden="true"></div>

<div class="page">

  <!-- ================= HERO ================= -->
  <header class="hero">
    <div class="wrap">
      <div class="topbar">
        <div class="brand">
          <span class="mark" aria-hidden="true">▶</span>
          <span>
            Building Reel
            <small>Product Résumé · 2026</small>
          </span>
        </div>
        <span class="badge" id="plan-badge"><span class="dot" aria-hidden="true"></span> <span id="plan-badge-text">Free — 3 videos / month</span></span>
      </div>

      <h1>Turn any topic into a <span class="grad">scripted, voiced, ready-to-post</span> short video.</h1>

      <p class="lede">
        Building Reel is a one-person production studio in a text box. Drop in a topic —
        <b>no script, no mic, no editing timeline</b> — and get back a vertical short with a hook,
        a paced voiceover, burned-in captions, and a cover frame. Built for founders, educators,
        and anyone who has to post before lunch.
      </p>

      <div class="cta">
        <a class="btn btn-primary" href="#start">Start free — 3 videos/month</a>
        <a class="btn btn-ghost" href="#how">See how it works</a>
      </div>

      <div class="metrics" role="list">
        <div class="metric" role="listitem"><div class="n" id="metric-free">3 / mo</div><div class="l" id="metric-free-label">Free forever</div></div>
        <div class="metric" role="listitem"><div class="n">9:16</div><div class="l">Native vertical</div></div>
        <div class="metric" role="listitem"><div class="n">&lt;60s</div><div class="l">Idea → export</div></div>
        <div class="metric" role="listitem"><div class="n" id="metric-pro">$40</div><div class="l" id="metric-pro-label">Pro / month</div></div>
      </div>
    </div>
  </header>

  <!-- ================= BODY ================= -->
  <div class="wrap">
    <div class="body-grid">

      <!-- ---------- SIDEBAR ---------- -->
      <aside>

        <section class="card">
          <div class="sec-title">Contact</div>
          <ul class="contact">
            <li><span class="k">Web</span><a href="#start">buildingreel.app</a></li>
            <li><span class="k">Email</span><a href="mailto:hello@buildingreel.app">hello@buildingreel.app</a></li>
            <li><span class="k">Social</span><a href="#start">@buildingreel</a></li>
            <li><span class="k">Status</span><span style="color:#3ee98a">● Open — accepting new users</span></li>
          </ul>
        </section>

        <section class="card">
          <div class="sec-title">Core Skills</div>
          <div class="chips">
            <span class="chip">Script writing</span>
            <span class="chip">Hook generation</span>
            <span class="chip">AI voiceover</span>
            <span class="chip">Auto-captions</span>
            <span class="chip">Vertical 9:16</span>
            <span class="chip">B-roll assembly</span>
            <span class="chip">Brand kits</span>
            <span class="chip">Batch rendering</span>
            <span class="chip">Cover frames</span>
            <span class="chip">Multi-voice</span>
          </div>
        </section>

        <section>
          <div class="sec-title">Pricing</div>

          <!-- ===== FRONTEND ADDITION #1: $40/month Pro price ===== -->
          <div class="price hot" id="free-plan-card">
            <div class="row">
              <span class="name">Free</span>
              <span class="amt">$0 <span>/ month</span></span>
            </div>
            <ul>
              <li>3 finished videos per month</li>
              <li>Full script + voiceover engine</li>
              <li>Captions and cover frame included</li>
              <li>No watermark, no card required</li>
            </ul>
            <p class="usage-note" style="margin-top:12px">After 3 videos, upgrade to Pro to continue.</p>
          </div>

          <div class="price" id="pro-plan-card">
            <div class="row">
              <span class="name">Pro</span>
              <span class="amt">$40 <span>/ month</span></span>
            </div>
            <ul>
              <li>Unlimited videos</li>
              <li>Premium voice library</li>
              <li>Brand kit + saved templates</li>
              <li>Priority rendering</li>
            </ul>
            <button class="upgrade-btn" id="sidebar-upgrade-btn" type="button">Upgrade to Pro →</button>
          </div>
        </section>

      </aside>

      <!-- ---------- MAIN ---------- -->
      <main>

        <section class="sec">
          <div class="sec-title">Summary</div>
          <div class="card">
            <p style="color:var(--muted)">
              Most short-form tools assume you already have a script, a voice, and an editing
              workflow. Building Reel removes all three assumptions. Give it a topic, a link, or a
              rough thought, and it returns a finished vertical video with the pacing, the
              narration, and the on-screen text already handled.
            </p>
            <p style="color:var(--muted);margin-top:14px">
              The product is deliberately narrow: <strong style="color:var(--ink)">one topic in, one postable short out.</strong>
              The free tier covers <strong style="color:var(--ink)">3 videos per month</strong>. Once you hit the
              limit, upgrade to <strong style="color:var(--ink)">Pro at $40/month</strong> for unlimited generation.
            </p>
          </div>
        </section>

        <section class="sec" id="how">
          <div class="sec-title">How It Works</div>

          <div class="step">
            <div class="num">01</div>
            <div>
              <h3>Drop in a topic</h3>
              <p>A sentence, a headline, a URL, or a half-formed idea. No prompt engineering, no
                 template picking, no blank-page paralysis.</p>
              <span class="tag">input → any text</span>
            </div>
          </div>

          <div class="step">
            <div class="num">02</div>
            <div>
              <h3>Get a script built to hold attention</h3>
              <p>Reel writes a hook, a tight body, and a closing beat — timed to the second so
                 nothing drags and nothing gets cut off mid-sentence.</p>
              <span class="tag">output → timed script</span>
            </div>
          </div>

          <div class="step">
            <div class="num">03</div>
            <div>
              <h3>Pick a voice — or keep your own</h3>
              <p>Choose from a library of natural narrators, set the energy, and let it read.
                 Prefer your own voice? Use the script as a teleprompter instead.</p>
              <span class="tag">output → voiceover track</span>
            </div>
          </div>

          <div class="step">
            <div class="num">04</div>
            <div>
              <h3>Export ready-to-post</h3>
              <p>Captions burned in, cover frame generated, framed 9:16 for Reels, Shorts, and
                 TikTok. Download and upload — that's the whole remaining job.</p>
              <span class="tag">output → .mp4 · 9:16</span>
            </div>
          </div>
        </section>

        <!-- ================= GENERATOR DEMO ================= -->
        <section class="sec" id="start">
          <div class="sec-title">Try It — Usage Demo</div>

          <!-- Usage tracker (driven by BACKEND SIMULATION below) -->
          <div class="usage-card">
            <div class="usage-head">
              <span class="label" id="usage-label">Free plan usage</span>
              <span class="count" id="usage-count">0 / 3 videos</span>
            </div>
            <div class="usage-bar"><div class="fill" id="usage-fill"></div></div>
            <p class="usage-note" id="usage-note">
              You have <strong id="usage-remaining">3</strong> free videos left this month.
            </p>
          </div>

          <!-- Generator -->
          <div class="generator">
            <label for="topic-input">Your topic</label>
            <input id="topic-input" type="text" placeholder="e.g. Why most SaaS onboarding loses users by day 3" />
            <div class="actions">
              <button class="btn btn-primary" id="generate-btn" type="button">Generate video</button>
              <button class="btn btn-ghost" id="reset-btn" type="button" title="Reset demo (test the paywall again)">Reset demo</button>
            </div>
            <div class="output" id="output">
              Enter a topic above and click <strong style="color:var(--ink)">Generate video</strong> to see the usage limit in action.
            </div>
          </div>
        </section>

        <section class="sec">
          <div class="sec-title">What It Handles</div>
          <div class="features">

            <div class="feature">
              <h4><i>✎</i> Script &amp; hook writing</h4>
              <p>Every video opens with a hook written for the scroll, not for an essay. Rewrite
                 any line and the timing re-flows automatically.</p>
            </div>

            <div class="feature">
              <h4><i>◍</i> Studio-grade voiceover</h4>
              <p>Multiple voices, adjustable pace and energy. No mic, no retakes, no "let me record
                 that one more time."</p>
            </div>

            <div class="feature">
              <h4><i>▤</i> Burned-in captions</h4>
              <p>Auto-generated, word-synced, and styled to stay legible on a phone at arm's
                 length. Most viewers watch muted — this is the part that matters.</p>
            </div>

            <div class="feature">
              <h4><i>◨</i> Native vertical output</h4>
              <p>Framed and paced for 9:16 from the start, with a cover frame that reads as a
                 thumbnail instead of a random still.</p>
            </div>

            <div class="feature">
              <h4><i>⚡</i> Fast enough to iterate</h4>
              <p>Under a minute from topic to export. Try three hooks in the time it used to take
                 to open an editor.</p>
            </div>

            <div class="feature">
              <h4><i>◆</i> Consistent by default</h4>
              <p>Save a brand kit once — colours, caption style, voice — and every future video
                 comes out looking like the same channel made it.</p>
            </div>

          </div>
        </section>

        <section class="sec">
          <div class="sec-title">Get Started</div>
          <div class="card" style="display:flex;flex-wrap:wrap;gap:20px;align-items:center;justify-content:space-between">
            <div style="min-width:240px;flex:1">
              <h3 style="font-size:1.15rem;margin-bottom:6px">3 free videos a month. Then Pro at $40/month.</h3>
              <p style="color:var(--muted);font-size:14px">
                Make your three. If it sounds like you, upgrade for unlimited generation.
              </p>
            </div>
            <button class="btn btn-primary" id="footer-upgrade-btn" type="button">Upgrade to Pro →</button>
          </div>
        </section>

      </main>
    </div>

    <!-- ================= FOOTER ================= -->
    <footer>
      <span>Building Reel — topic in, postable short out.</span>
      <span>
        <a href="#start">buildingreel.app</a> · <a href="mailto:hello@buildingreel.app">hello@buildingreel.app</a>
      </span>
    </footer>
  </div>

</div>

<!-- ================= UPGRADE MODAL ================= -->
<div class="modal-overlay" id="upgrade-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <button class="close-x" id="modal-close" type="button" aria-label="Close">✕</button>

    <div class="modal-icon" aria-hidden="true">🔒</div>

    <h2 id="modal-title">You've used all 3 free videos</h2>
    <p class="sub">
      Your monthly free limit is up. Upgrade to Pro to keep generating unlimited
      scripted, voiced shorts — and never hit this wall again.
    </p>

    <div class="modal-price">
      <span class="big">$40</span>
      <span class="per">/ month · cancel anytime</span>
      <span class="save">UNLIMITED</span>
    </div>

    <ul class="perks">
      <li>Unlimited videos every month</li>
      <li>Premium voice library &amp; energy controls</li>
      <li>Saved brand kits and templates</li>
      <li>Priority rendering queue</li>
    </ul>

    <div class="modal-actions">
      <!-- 🔻 REPLACE the href below with your real Stripe / PayPal checkout link -->
      <a class="btn btn-primary" id="checkout-btn" href="https://buy.stripe.com/REPLACE_WITH_YOUR_40_DOLLAR_LINK" target="_blank" rel="noopener">
        Upgrade now — $40/month
      </a>
      <button class="btn btn-ghost" id="modal-dismiss" type="button">Maybe later</button>
    </div>

    <p class="fine">Secure checkout · Cancel anytime · No hidden fees</p>
  </div>
</div>

<script>
/* =========================================================================
   Building Reel — 2 LAYERS
   ---------------------------------------------------------------------
   FRONTEND LAYER  (what the user sees — this file)
     • Displays $40/month Pro price
     • Shows usage counter + progress bar
     • Opens the paywall modal when blocked
     • Redirects to checkout on upgrade

   BACKEND LAYER   (simulated here with localStorage)
     • Counts videos per user
     • Blocks generation at 3 for Free users
     • Flips user to Pro after successful payment
     • Source of truth — frontend never decides billing

   In production, replace `Backend.*` calls with real fetch():
     GET  /api/me              → { tier, videosUsed }
     POST /api/generate-video  → 403 { error:"LIMIT_REACHED" } if over
     POST /api/checkout        → { url } Stripe Checkout session
   ========================================================================= */

/* =====================================================================
   BACKEND SIMULATION — localStorage acts as the database
   ===================================================================== */
const Backend = (() => {
  const KEY         = 'building_reel_demo_v1';
  const FREE_LIMIT  = 3;
  const PRO_PRICE   = 40;   // ← $40/month — also referenced in frontend copy

  function _read() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return { tier: 'free', videosUsed: 0 };
      const p = JSON.parse(raw);
      return {
        tier: p.tier === 'pro' ? 'pro' : 'free',
        videosUsed: Number(p.videosUsed) || 0
      };
    } catch { return { tier: 'free', videosUsed: 0 }; }
  }

  function _write(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch {}
  }

  return {
    FREE_LIMIT,
    PRO_PRICE,

    /* GET /api/me */
    getUser() {
      const s = _read();
      return {
        tier: s.tier,
        videosUsed: s.videosUsed,
        remaining: Math.max(FREE_LIMIT - s.videosUsed, 0),
        limit: FREE_LIMIT
      };
    },

    /* POST /api/generate-video */
    generate() {
      const s = _read();
      if (s.tier === 'pro') return { ok: true, state: this.getUser() };
      if (s.videosUsed >= FREE_LIMIT) {
        return { ok: false, error: 'LIMIT_REACHED', state: this.getUser() };
      }
      s.videosUsed += 1;
      _write(s);
      return { ok: true, state: this.getUser() };
    },

    /* POST /api/checkout — in prod, this returns a Stripe URL */
    upgradeToPro() {
      const s = _read();
      s.tier = 'pro';
      _write(s);
      return { ok: true, state: this.getUser() };
    },

    reset() {
      try { localStorage.removeItem(KEY); } catch {}
    }
  };
})();

/* =====================================================================
   FRONTEND LAYER — DOM refs
   ===================================================================== */
const els = {
  planBadge:      document.getElementById('plan-badge'),
  planBadgeText:  document.getElementById('plan-badge-text'),
  metricFree:     document.getElementById('metric-free'),
  metricFreeLbl:  document.getElementById('metric-free-label'),

  freeCard:       document.getElementById('free-plan-card'),
  proCard:        document.getElementById('pro-plan-card'),

  usageLabel:     document.getElementById('usage-label'),
  usageCount:     document.getElementById('usage-count'),
  usageFill:      document.getElementById('usage-fill'),
  usageNote:      document.getElementById('usage-note'),
  usageRemaining: document.getElementById('usage-remaining'),

  topicInput:     document.getElementById('topic-input'),
  generateBtn:    document.getElementById('generate-btn'),
  resetBtn:       document.getElementById('reset-btn'),
  output:         document.getElementById('output'),

  modal:          document.getElementById('upgrade-modal'),
  modalClose:     document.getElementById('modal-close'),
  modalDismiss:   document.getElementById('modal-dismiss'),

  sidebarUpgrade: document.getElementById('sidebar-upgrade-btn'),
  footerUpgrade:  document.getElementById('footer-upgrade-btn')
};

/* =====================================================================
   FRONTEND LAYER — render (pure display, no billing logic)
   ===================================================================== */
function render() {
  const { tier, videosUsed, remaining, limit } = Backend.getUser();
  const isPro = tier === 'pro';
  const used  = Math.min(videosUsed, limit);

  /* badge */
  els.planBadge.classList.toggle('pro', isPro);
  els.planBadgeText.textContent = isPro
    ? 'Pro — unlimited videos'
    : 'Free — 3 videos / month';

  /* metric strip */
  if (isPro) {
    els.metricFree.textContent = '∞';
    els.metricFreeLbl.textContent = 'Unlimited (Pro)';
  } else {
    els.metricFree.textContent = remaining + ' / mo';
    els.metricFreeLbl.textContent = remaining === 1 ? 'Free video left' : 'Free videos left';
  }

  /* usage card */
  els.usageLabel.textContent = isPro ? 'Pro plan usage' : 'Free plan usage';
  els.usageCount.textContent = isPro ? '∞ / ∞ videos' : used + ' / ' + limit + ' videos';

  let pct = isPro ? 100 : (videosUsed / limit) * 100;
  pct = Math.max(0, Math.min(pct, 100));
  els.usageFill.style.width = pct + '%';
  els.usageFill.classList.remove('warn', 'full');
  if (!isPro) {
    if (remaining === 0) els.usageFill.classList.add('full');
    else if (remaining === 1) els.usageFill.classList.add('warn');
  }

  if (isPro) {
    els.usageNote.innerHTML = 'You\u2019re on <strong>Pro</strong> — generate as many videos as you like.';
  } else if (remaining === 0) {
    els.usageNote.innerHTML = 'You\u2019ve used all 3 free videos this month. <strong>Upgrade to Pro for $40/month</strong> to continue.';
  } else {
    els.usageNote.innerHTML = 'You have <strong id="usage-remaining">' + remaining + '</strong> free ' +
      (remaining === 1 ? 'video' : 'videos') + ' left this month.';
    els.usageRemaining = document.getElementById('usage-remaining');
  }

  /* generator controls */
  if (isPro) {
    els.generateBtn.disabled = false;
    els.generateBtn.textContent = 'Generate video';
    els.topicInput.disabled = false;
  } else if (remaining === 0) {
    els.generateBtn.disabled = false;
    els.generateBtn.textContent = 'Upgrade to continue';
    els.topicInput.disabled = true;
  } else {
    els.generateBtn.disabled = false;
    els.generateBtn.textContent = 'Generate video';
    els.topicInput.disabled = false;
  }

  /* sidebar highlight */
  els.freeCard.classList.toggle('hot', !isPro);
  els.proCard.classList.toggle('hot', isPro);
}

/* =====================================================================
   FRONTEND LAYER — modal + upgrade handlers
   ===================================================================== */
function openModal() {
  els.modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  els.modal.classList.remove('open');
  document.body.style.overflow = '';
}

els.modalClose.addEventListener('click', closeModal);
els.modalDismiss.addEventListener('click', closeModal);
els.modal.addEventListener('click', (e) => {
  if (e.target === els.modal) closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && els.modal.classList.contains('open')) closeModal();
});

/* Upgrade button → in prod this calls POST /api/checkout and redirects */
function goToCheckout() {
  const proceed = confirm(
    'DEMO MODE\n\n' +
    'In production this would open Stripe Checkout for $40/month.\n\n' +
    'Click OK to simulate a successful payment and unlock Pro.'
  );
  if (!proceed) return;

  const result = Backend.upgradeToPro();
  if (result.ok) {
    closeModal();
    render();
    els.output.innerHTML =
      '<strong style="color:#3ee98a">✓ Upgraded to Pro.</strong> Unlimited videos unlocked. ' +
      'You can now generate as many videos as you want.';
  }
}

els.sidebarUpgrade.addEventListener('click', goToCheckout);
els.footerUpgrade.addEventListener('click', goToCheckout);

/* =====================================================================
   FRONTEND LAYER — generate button → calls backend, reacts to result
   ===================================================================== */
els.generateBtn.addEventListener('click', () => {
  const { tier, remaining } = Backend.getUser();

  /* Paywall check (backend also enforces this) */
  if (tier !== 'pro' && remaining <= 0) {
    openModal();
    return;
  }

  const topic = (els.topicInput.value || '').trim();
  if (!topic) {
    els.output.textContent = '⚠️ Enter a topic first — e.g. "Why most SaaS onboarding loses users by day 3".';
    els.topicInput.focus();
    return;
  }

  /* Simulate the backend round-trip */
  els.generateBtn.disabled = true;
  els.output.classList.add('working');
  els.output.innerHTML = '<span class="spinner" aria-hidden="true"></span> Generating script, voiceover, and captions…';

  setTimeout(() => {
    const result = Backend.generate();
    const newRemaining = result.state ? result.state.remaining : 0;

    els.output.classList.remove('working');
    els.generateBtn.disabled = false;

    if (!result.ok) {
      /* Backend said LIMIT_REACHED */
      els.output.innerHTML =
        '<span style="color:#ff5c8a;font-size:18px">🔒</span>' +
        '<span><strong style="color:var(--ink)">Free limit reached.</strong> Upgrade to Pro to keep generating.</span>';
      render();
      openModal();
      return;
    }

    els.output.innerHTML =
      '<span style="color:#3ee98a;font-size:18px">▶</span>' +
      '<span>Your short on <strong style="color:var(--ink)">"' + escapeHtml(topic) + '"</strong> is ready. ' +
      '<span style="color:var(--dim)">(demo — no actual video generated)</span></span>';

    render();

    /* Just crossed the limit → auto-nudge with the modal */
    if (result.state.tier !== 'pro' && newRemaining === 0) {
      setTimeout(openModal, 600);
    }
  }, 1400);
});

/* =====================================================================
   FRONTEND LAYER — reset demo
   ===================================================================== */
els.resetBtn.addEventListener('click', () => {
  if (!confirm('Reset the demo? This clears your usage count and returns you to the Free plan.')) return;
  Backend.reset();
  els.topicInput.value = '';
  els.topicInput.disabled = false;
  els.output.classList.remove('working');
  els.output.textContent = 'Demo reset. Enter a topic and click Generate video to test the 3-video limit again.';
  render();
});

/* =====================================================================
   helper
   ===================================================================== */
function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}

/* init */
render();
</script>
</body>
</html>
