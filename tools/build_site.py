#!/usr/bin/env python3
"""Build the Gravit Path website into site/ in every language, from the shared Gravit layout, the texts in
tools/texts_<lang>.py and the rule packs. English lives at /, the other languages at /<lang>/. The rules page
is generated from rules/*/*.yaml, so the site always shows exactly the rules the assistant uses; rule
statements stay in English, the language of their official sources."""
import html
import importlib
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
sys.path.insert(0, str(Path(__file__).resolve().parent))
LANGS = ["en", "de", "fr", "it", "es", "pt", "tr", "uk", "ru", "zh", "ja"]
HTML_LANG = {"zh": "zh-Hans"}
SHORT = {"en": "English", "de": "Deutsch", "fr": "Français", "it": "Italiano", "es": "Español", "pt": "Português", "tr": "Türkçe", "uk": "Українська", "ru": "Русский", "zh": "中文", "ja": "日本語"}
TAGCLS = {"verified": "t-ok", "secondary": "t-warn", "needs_review": "t-warn"}
GH = "https://github.com/gravit-open-network-foundation/gravit-path"
# Partners who agreed to be named; names exactly as on their own sites.
PARTNERS = [("Rapid Formations", "https://www.rapidformations.co.uk", "UK"),
            ("1stchoice Formations", "https://www.1stchoice-formations.co.uk", "UK"),
            ("Greater Zurich Area", "https://www.greaterzuricharea.com", "CH")]
E = html.escape
from plans_order import P as PO
from situations import S as SIT

# Plan cards in the style of gravitverifier, and partner tiles (15.11.2026).
# Partner lines are short summaries of what each partner says about itself on its own site.
EXTRA = {
 "en": {"price_free": "CHF 0", "price_corp": "On request", "btn_free": "Start your path", "btn_corp": "Write to us", "planned": "PLANNED",
        "visit": "Visit site",
        "p": ["UK company formation agent: register a limited company online and start trading within 24 hours. Official ACSP agent.",
              "Authorised UK company formation agent: formation and registration of a company within one working day.",
              "Investment promotion agency of the Greater Zurich economic area: free support for companies settling in the region."]},
 "de": {"price_free": "CHF 0", "price_corp": "Auf Anfrage", "btn_free": "Ihren Weg beginnen", "btn_corp": "Schreiben Sie uns", "planned": "GEPLANT",
        "visit": "Zur Website",
        "p": ["Gründungsagentur im Vereinigten Königreich: eine Limited online registrieren und innerhalb von 24 Stunden starten. Offizieller ACSP-Agent.",
              "Zugelassene Gründungsagentur im Vereinigten Königreich: Gründung und Registrierung einer Gesellschaft innerhalb eines Arbeitstags.",
              "Standortmarketing des Wirtschaftsraums Zürich: kostenlose Unterstützung für Unternehmen, die sich in der Region ansiedeln."]},
 "fr": {"price_free": "CHF 0", "price_corp": "Sur demande", "btn_free": "Commencer votre parcours", "btn_corp": "Nous écrire", "planned": "PRÉVU",
        "visit": "Voir le site",
        "p": ["Agent de constitution de sociétés au Royaume-Uni : enregistrer une limited en ligne et commencer à exercer en 24 heures. Agent ACSP officiel.",
              "Agent agréé de constitution de sociétés au Royaume-Uni : constitution et enregistrement d’une société en un jour ouvrable.",
              "Agence de promotion économique de la région du Grand Zurich : soutien gratuit aux entreprises qui s’implantent dans la région."]},
 "it": {"price_free": "CHF 0", "price_corp": "Su richiesta", "btn_free": "Inizia il tuo percorso", "btn_corp": "Scrivici", "planned": "PREVISTO",
        "visit": "Visita il sito",
        "p": ["Agente per la costituzione di società nel Regno Unito: registrare una limited online e iniziare l’attività entro 24 ore. Agente ACSP ufficiale.",
              "Agente autorizzato per la costituzione di società nel Regno Unito: costituzione e registrazione di una società in un giorno lavorativo.",
              "Agenzia di promozione economica dell’area della Grande Zurigo: supporto gratuito alle aziende che si insediano nella regione."]},
 "es": {"price_free": "CHF 0", "price_corp": "Bajo consulta", "btn_free": "Empezar su camino", "btn_corp": "Escríbanos", "planned": "PREVISTO",
        "visit": "Ver sitio",
        "p": ["Agente de constitución de sociedades en el Reino Unido: registre una limited en línea y empiece a operar en 24 horas. Agente ACSP oficial.",
              "Agente autorizado de constitución de sociedades en el Reino Unido: constitución y registro de una sociedad en un día hábil.",
              "Agencia de promoción económica del área del Gran Zúrich: apoyo gratuito a las empresas que se establecen en la región."]},
 "pt": {"price_free": "CHF 0", "price_corp": "Sob consulta", "btn_free": "Começar o seu caminho", "btn_corp": "Escreva-nos", "planned": "PREVISTO",
        "visit": "Ver site",
        "p": ["Agente de constituição de empresas no Reino Unido: registe uma limited online e comece a operar em 24 horas. Agente ACSP oficial.",
              "Agente autorizado de constituição de empresas no Reino Unido: constituição e registo de uma empresa num dia útil.",
              "Agência de promoção económica da área da Grande Zurique: apoio gratuito às empresas que se instalam na região."]},
 "tr": {"price_free": "CHF 0", "price_corp": "Talep üzerine", "btn_free": "Yolunuza başlayın", "btn_corp": "Bize yazın", "planned": "PLANLANDI",
        "visit": "Siteye git",
        "p": ["Birleşik Krallık şirket kuruluş acentesi: bir limited şirketi çevrim içi kaydedin ve 24 saat içinde faaliyete başlayın. Resmî ACSP acentesi.",
              "Yetkili Birleşik Krallık şirket kuruluş acentesi: bir şirketin bir iş günü içinde kurulması ve tescili.",
              "Büyük Zürih ekonomik bölgesinin yatırım tanıtım ajansı: bölgeye yerleşen şirketlere ücretsiz destek."]},
 "uk": {"price_free": "CHF 0", "price_corp": "За запитом", "btn_free": "Почати свій шлях", "btn_corp": "Напишіть нам", "planned": "ЗАПЛАНОВАНО",
        "visit": "На сайт",
        "p": ["Агент із реєстрації компаній у Великій Британії: зареєструйте limited онлайн і почніть роботу протягом 24 годин. Офіційний агент ACSP.",
              "Уповноважений агент із реєстрації компаній у Великій Британії: створення та реєстрація компанії протягом одного робочого дня.",
              "Агенція з залучення інвестицій регіону Великого Цюриха: безкоштовна підтримка компаній, що оселяються в регіоні."]},
 "ru": {"price_free": "CHF 0", "price_corp": "По запросу", "btn_free": "Начать свой путь", "btn_corp": "Напишите нам", "planned": "ЗАПЛАНИРОВАНО",
        "visit": "На сайт",
        "p": ["Агент по регистрации компаний в Великобритании: зарегистрируйте limited онлайн и начните работу в течение 24 часов. Официальный агент ACSP.",
              "Уполномоченный агент по регистрации компаний в Великобритании: создание и регистрация компании за один рабочий день.",
              "Агентство по привлечению инвестиций региона Большого Цюриха: бесплатная поддержка компаний, которые размещаются в регионе."]},
 "zh": {"price_free": "CHF 0", "price_corp": "按需报价", "btn_free": "开始您的路径", "btn_corp": "联系我们", "planned": "计划中",
        "visit": "访问网站",
        "p": ["英国公司注册代理：在线注册有限公司，24 小时内即可开业。官方 ACSP 代理。",
              "经授权的英国公司注册代理：一个工作日内完成公司设立和注册。",
              "大苏黎世经济区投资促进机构：为在该地区落户的企业提供免费支持。"]},
 "ja": {"price_free": "CHF 0", "price_corp": "要相談", "btn_free": "あなたの道を始める", "btn_corp": "お問い合わせ", "planned": "予定",
        "visit": "サイトへ",
        "p": ["英国の会社設立代理店：リミテッド会社をオンラインで登記し、24 時間以内に事業を開始。公式 ACSP エージェント。",
              "認可を受けた英国の会社設立代理店：1 営業日以内に会社の設立と登記。",
              "グレーター・チューリッヒ地域の投資促進機関：地域に進出する企業を無料で支援。"]},
}

# Sends a first-time visitor to the language of their browser, if we have it. No cookies, no tracking:
# the choice made with the language links is remembered in this browser only.
AUTO = """<script>(function(){try{if(localStorage.getItem('gp-lang'))return}catch(e){}
var have=%s,ls=navigator.languages||[navigator.language||''];
for(var i=0;i<ls.length;i++){var c=(ls[i]||'').toLowerCase().slice(0,2);if(c==='en')return;
if(have.indexOf(c)>-1){location.replace('/'+c+location.pathname+location.hash);return}}})();</script>"""


def texts(lang):
    return importlib.import_module(f"texts_{lang}").T


def packs():
    return {f.parent.name: yaml.safe_load(f.read_text()) for f in sorted((ROOT / "rules").glob("*/*.yaml"))}


def prefix(lang):
    return "" if lang == "en" else f"{lang}/"


def page(lang, sub, title, desc, nav, body):
    depth = (0 if lang == "en" else 1) + (1 if sub else 0)
    root = "../" * depth
    head = (SITE / "_head.html").read_text().replace("{{TITLE}}", E(title)).replace("{{DESC}}", E(desc)).replace("{{ROOT}}", root)
    head = head.replace('<html lang="en">', f'<html lang="{HTML_LANG.get(lang, lang)}">')
    alt = "".join(f'<link rel="alternate" hreflang="{HTML_LANG.get(l, l)}" href="https://gravitpath.world/{prefix(l)}{sub}">' for l in LANGS)
    alt += f'<link rel="alternate" hreflang="x-default" href="https://gravitpath.world/{sub}">'
    head = head.replace("</head>", alt + (AUTO % json.dumps(LANGS[1:]) if lang == "en" else "") + "\n</head>", 1)
    foot = (SITE / "_foot.html").read_text().replace("{{ROOT}}", root or "./")
    home = root + prefix(lang)
    items = "".join(f'<li><a href="{h}">{t}</a></li>' for t, h in nav)
    opts = "".join(f'<option value="{root}{prefix(l)}{sub}" data-l="{l}"{" selected" if l == lang else ""}>{SHORT[l]}</option>' for l in LANGS)
    langs = ('<select aria-label="Language" onchange="try{localStorage.setItem(\'gp-lang\',this.options[this.selectedIndex].dataset.l)}catch(e){};'
             f'location.href=this.value">{opts}</select>')
    items += f'<li class="langs">{langs}</li>'
    header = f'''<div class="page">
  <header>
    <a class="logo" href="{home or './'}" aria-label="Gravit Path">
    <img class="astra" src="{root}img/logo-gon-162.webp" srcset="{root}img/logo-gon-162.webp 1x, {root}img/logo-gon-324.webp 2x, {root}img/logo-gon-486.webp 3x" width="108" height="162" alt="" decoding="async" fetchpriority="high" />
    
    </a>
    <nav aria-label="Main"><ul>{items}</ul></nav>
  </header>
  <style>nav li.langs{{margin-left:8px;padding-left:14px;border-left:1px solid rgba(100,180,255,.25)}}
  nav li.langs select{{background:transparent;color:inherit;border:1px solid rgba(100,180,255,.3);border-radius:8px;padding:4px 6px;font:inherit;cursor:pointer}}
  nav li.langs option{{background:#0b1a33;color:#fff}}</style>
  <main><div class="gv">
'''
    return head + header + body + "\n  </div></main>\n\n" + foot


def index(p, T, lang):
    n = sum(len(v) for v in p.values())
    v = sum(1 for rs in p.values() for r in rs if r["status"] == "verified")
    f = lambda s: s.format(n=n, v=v)  # noqa: E731
    labels = "".join(f'<div class="state"><b>{E(a)}</b><span class="tag {c}">{E(b)}</span></div>'
                     for (a, b), c in zip(T["labels"], ["t-bad", "t-plan", "t-ok"]))
    steps = "".join(f'<div class="card"><span class="rule">{E(a)}</span><h3>{E(b)}</h3><p>{E(c)}</p></div>' for a, b, c in T["steps"])
    tag = {"rules": f' <span class="tag t-plan">{E(T["tag_rules"])}</span>', "planned": f' <span class="tag t-warn">{E(T["tag_planned"])}</span>', "": ""}
    paths = "".join(f'<div class="card"><span class="rule">{E(a)}</span><h3>{E(b)}</h3><p>{E(c)}{tag[s]}</p></div>' for a, b, c, s in T["paths"])
    countries = "".join(
        f'<div class="card"><span class="rule">{k.upper()}</span><h3>{E(T["country_names"][k])}</h3><p>'
        f'{E(T["country_card"].format(n=len(rs), v=sum(1 for r in rs if r["status"] == "verified")))} '
        f'<a href="rules/#{k}">{E(T["see_them"])}</a></p></div>' for k, rs in p.items())
    sample = [r for rs in p.values() for r in rs if r["status"] == "verified"][:3]
    rules = "".join(f'<div class="card"><span class="rule">{E(r["id"])}</span><p>{E(r["statement"])} '
                    f'<a href="{E(r["source"])}">{E(T["official_source"])}</a></p></div>' for r in sample)
    princ = "".join(f'<div class="card"><h3>{E(a)}</h3><p>{E(b)}</p></div>' for a, b in T["principles"])
    links = ["https://gravitverifier.space", "https://github.com/gravit-open-network-foundation/capability-gate",
             "https://github.com/gravit-open-network-foundation/history-keeper"]
    trust = "".join(f'<div class="card"><h3>{E(a)}</h3><p>{E(b)} <a href="{u}">{E(c)}</a></p></div>' for (a, b, c), u in zip(T["trust"], links))
    ul = lambda xs: "".join(f"<li>{E(x)}</li>" for x in xs)  # noqa: E731
    pp, pr = T["plan_people"], T["plan_pro"]
    X = EXTRA.get(lang, EXTRA["en"])
    Q = PO[lang]
    Z = SIT[lang]
    mail = '<a href="/contact/">gravitpath.world/contact</a>'
    canon = f'<a href="{GH}/blob/main/CANON.md">CANON.md</a>'
    tcls = {"ok": "t-ok", "warn": "t-warn", "bad": "t-bad", "plan": "t-plan"}
    status = "".join(f'<tr><td>{E(a)}</td><td><span class="tag {tcls[c]}">{E(t)}</span> '
                     f'{E(f(d)).replace("{canon}", canon) if d != "{canon}" else canon}</td></tr>' for a, c, t, d in [(r[0], "ok", PO[lang]["avail"], PO[lang]["avail_txt"]) if r[1] == "plan" else r for r in T["status"]])
    return f'''
<div class="hero">
  <div>
    <p class="kicker">{E(Z["kicker"])}</p>
    <h1>{E(Z["h1"])}</h1>
    <p class="lead">{E(Z["lead"])}</p>
    <div class="btns"><a class="btn btn1" href="/contact/">{E(Z["btn_tell"])}</a><a class="btn btn2" href="#how">{E(Z["btn_steps"])}</a></div>
  </div>
  <div class="states">{labels}<p>{E(T["labels_note"])}</p></div>
</div>
<section id="situations"><h2>{E(Z["sit_h"])}</h2><p class="muted">{E(Z["sit_lead"])}</p>
  <div class="ptiles sit">{"".join(f'<a class="ptile" href="/contact/"><h3>{E(a)}</h3><p>{E(b)}</p><span class="pgo">{E(Z["tile_btn"])} →</span></a>' for a, b in Z["sits"])}</div></section>
<section id="how"><h2>{E(T["how_h"])}</h2><div class="grid">{steps}</div></section>
<section id="paths"><h2>{E(T["paths_h"])}</h2><p class="muted">{E(T["paths_lead"])}</p><div class="grid">{paths}</div></section>
<section id="countries"><h2>{E(T["countries_h"])}</h2><p class="muted">{E(T["countries_lead"])}</p><div class="grid">{countries}</div></section>
<section id="rules"><h2>{E(T["rules_h"])}</h2><p class="muted">{E(f(T["rules_lead"]))}</p><div class="grid">{rules}</div>
  <p style="margin-top:16px"><a class="btn btn2" href="rules/">{E(f(T["all_rules"]))}</a></p></section>
<section id="plans"><h2>{E(T["plans_h"])}</h2>
  <p class="muted">{E(Q["intro"])}</p>
  <div class="plans">
    <div class="plan"><h3>Free</h3><div class="price">CHF 0</div>
      <p class="muted" style="margin:4px 0 0;font-size:14px">{E(pp[0])}</p><span class="tag t-plan">{E(T["preview"])}</span>
      <ul>{ul(pp[2] + [Q["free_plus"]])}</ul><a class="btn btn2" href="#how" style="margin-top:14px">{E(Q["btn_free"])}</a></div>
    <div class="plan" style="border-color:var(--glow)"><h3>Business</h3><div class="price">CHF 7 <small>{E(Q["per30"])}</small></div>
      <p class="muted" style="margin:4px 0 0;font-size:14px">{E(Q["for_companies"])}</p><span class="tag t-ok">{E(Q["new"])}</span>
      <ul>{ul(Q["biz"])}</ul><a class="btn btn1" href="order/?plan=business" style="margin-top:14px">{E(Q["btn_biz"])}</a></div>
    <div class="plan"><h3>Enterprise</h3><div class="price">CHF 150 <small>{E(Q["per30"])}</small></div>
      <span class="tag t-ok">{E(Q["new"])}</span>
      <ul>{ul(pr[2][1:] + [Q["ent_plus"]])}</ul><a class="btn btn1" href="order/?plan=enterprise" style="margin-top:14px">{E(Q["btn_ent"])}</a></div>
  </div></section>
<section id="partners"><h2>{E(T["partners_h"])}</h2><p class="muted">{E(T["partners_text"]).replace("{mail}", mail)}</p>
  <div class="ptiles">{"".join(f'<a class="ptile" href="{u}" rel="noopener" target="_blank"><span class="rule">{c}</span><h3>{E(n)}</h3><p>{E(d)}</p><span class="pgo">{E(X["visit"])} →</span></a>' for (n, u, c), d in zip(PARTNERS, X["p"]))}</div></section>
<section id="status"><h2>{E(T["status_h"])}</h2>
  <div class="tablewrap"><table><tr><th>{E(T["status_item"])}</th><th>{E(T["status_today"])}</th></tr>{status}</table></div>
  <div class="notice">{E(T["notice"])}</div></section>
<section id="reviewers"><h2>{E(Z["rev_h"])}</h2><p class="muted">{E(Z["rev_lead"])}</p></section>
<section id="principles"><h3 style="font-size:22px;margin-top:28px">{E(T["principles_h"])}</h3><div class="grid">{princ}</div></section>
<section id="trust"><h3 style="font-size:22px;margin-top:28px">{E(T["trust_h"])}</h3><p class="muted">{E(T["trust_lead"])}</p><div class="grid">{trust}</div></section>
<section id="security"><h3 style="font-size:22px;margin-top:28px">{E(T["sec_h"])}</h3><p>{E(T["sec_p"])} <a href="https://gravitverifier.space/#standards">{E(T["sec_link"])}</a></p></section>

'''


def rules_page(p, T):
    blocks = []
    for k, rs in p.items():
        rows = "".join(
            f'<tr><td><code>{E(r["id"])}</code></td><td>{E(r["form"])}</td><td>{E(r["statement"])}'
            + (f'<br><span class="muted" style="font-size:14px">&ldquo;{E(r["quote"])}&rdquo;</span>' if r.get("quote") else "")
            + (f'<br><span class="muted" style="font-size:14px">{E(r["note"])}</span>' if r.get("note") else "")
            + f'</td><td><span class="tag {TAGCLS[r["status"]]}">{E(T["rp_status"][r["status"]])}</span><br>'
              f'<a href="{E(r["source"])}">{E(T["rp_source"])}</a></td></tr>'
            for r in rs)
        c = T["rp_cols"]
        blocks.append(f'<section id="{k}"><style>.gv td code{{white-space:nowrap}}</style><h2>{E(T["country_names"][k])}</h2>'
                      f'<div class="tablewrap"><table><tr><th>{E(c[0])}</th><th>{E(c[1])}</th><th>{E(c[2])}</th><th>{E(c[3])}</th></tr>'
                      f'{rows}</table></div></section>')
    manifest = json.loads((ROOT / "rules" / "MANIFEST.json").read_text())
    fp = "".join(f'<li><code>{E(f)}</code> sha256 <code>{m["sha256"][:16]}</code></li>' for f, m in manifest.items())
    gh = f'<a href="{GH}/tree/main/rules">GitHub</a>'
    note = f'<div class="notice">{E(T["rp_lang_note"])}</div>' if T["rp_lang_note"] else ""
    return f'''
<div class="hero" style="grid-template-columns:1fr">
  <div>
    <p class="kicker">{E(T["rp_kicker"])}</p>
    <h1>{E(T["rp_h1"])}<em>{E(T["rp_h1_em"])}</em></h1>
    <p class="lead">{E(T["rp_lead"])}</p>{note}
  </div>
</div>
{"".join(blocks)}
<section><h2>{E(T["rp_versions_h"])}</h2><p class="muted">{E(T["rp_versions"]).replace("{gh}", gh)}</p><ul>{fp}</ul></section>
'''


def order_page(lang):
    Q = PO[lang]
    opts = "".join(f'<option value="{v}">{E(t)}</option>' for v, t in
                   [("business", "Business, CHF 7 " + Q["per30"]), ("enterprise", "Enterprise, CHF 150 " + Q["per30"])])
    pays = "".join(f'<label class="pay"><input type="radio" name="pay" value="{v}"{" checked" if v == "USDC" else ""}> {E(t)}</label>'
                   for v, t in [("USDC", "USDC"), ("USDT", "USDT"), ("Bitcoin", "Bitcoin")])
    return f'''<section style="max-width:720px"><h1>{E(Q["o_title"])}</h1><p class="muted">{E(Q["o_lead"])}</p>
<div class="notice" id="ok" hidden>{E(Q["o_thanks"])}</div><div class="notice" id="err" hidden>{E(Q["o_err"])}</div><div class="notice" id="rate" hidden>{E(Q["o_rate"])}</div>
<form class="order" method="post" action="send.php">
<input type="hidden" name="t0" value="0"><input type="text" name="website2" value="" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
<input type="hidden" name="lang" value="{lang}">
<label>{E(Q["o_plan"])}<select name="plan" id="plan">{opts}</select></label>
<label>{E(Q["o_name"])}<input name="name" required maxlength="120"></label>
<label>{E(Q["o_email"])}<input name="email" type="email" required maxlength="200"></label>
<label>{E(Q["o_org"])}<input name="org" maxlength="200"></label>
<label>{E(Q["o_addr"])}<textarea name="addr" rows="3" maxlength="1000"></textarea></label>
<fieldset><legend>{E(Q["o_pay"])}</legend>{pays}<label class="pay" style="opacity:.55"><input type="radio" disabled> {E(Q["o_paypal"])}</label></fieldset>
<label>{E(Q["o_note"])}<textarea name="note" rows="3" maxlength="2000"></textarea></label>
<label class="pay"><input type="checkbox" name="consent" value="1" required> {E(Q["o_consent"])}</label>
<button class="btn btn1" type="submit">{E(Q["o_send"])}</button>
<p class="muted" style="font-size:14px;margin-top:14px">{E(Q["o_vat"])}</p>
</form>
<style>.gv form.order label{{display:block;margin:12px 0}}.gv form.order input:not([type=radio]):not([type=checkbox]),.gv form.order select,.gv form.order textarea{{display:block;width:100%;margin-top:6px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--text);font:inherit}}
.gv form.order fieldset{{border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin:12px 0}}.gv form.order .pay{{display:block;margin:6px 0}}.gv form.order button{{border:0;cursor:pointer;margin-top:8px}}</style>
<script>(function(){{var f=document.querySelector("form.order");f.t0.value=Date.now();var q=new URLSearchParams(location.search);
var p=q.get("plan");if(p)document.getElementById("plan").value=p;
if(q.get("sent")){{document.getElementById("ok").hidden=false;f.hidden=true}}
if(q.get("error")==="rate"){{document.getElementById("rate").hidden=false}}else if(q.get("error")){{document.getElementById("err").hidden=false}}}})();</script>
</section>'''


SEND = """<?php
// Order form of Gravit Path: the fields are written into the message and handled like a contact message.
$f = fn($k, $n) => mb_substr(trim((string)($_POST[$k] ?? '')), 0, $n);
$_POST['message'] = "ORDER\nPlan: " . $f('plan', 20) . "\nPayment: " . $f('pay', 20) . "\nLanguage: " . $f('lang', 5)
    . "\nBilling address: " . $f('addr', 1000) . "\nNotes: " . $f('note', 2000);
$_POST['topic'] = 'sales';
require dirname(__DIR__, %d) . '/contact-forms/lib.php';
cf_handle('gravitpath.order');
"""


if __name__ == "__main__":
    p = packs()
    keys = set(texts("en"))
    for lang in LANGS:
        T = texts(lang)
        missing = keys - set(T)
        if missing:
            raise SystemExit(f"texts_{lang}.py lacks {sorted(missing)}")
        anchors = ["#how", "#paths", "#countries", "rules/", "#principles", "#plans", "#status"]
        nav = list(zip(T["nav"], anchors))
        out = SITE / prefix(lang)
        (out / "rules").mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(page(lang, "", T["title"], T["desc"], nav, index(p, T, lang)))
        nav2 = [(t, ("../" + h) if h.startswith("#") else "./") for t, h in nav]
        (out / "rules" / "index.html").write_text(page(lang, "rules/", T["rp_title"], T["rp_desc"], nav2, rules_page(p, T)))
        (out / "order").mkdir(parents=True, exist_ok=True)
        (out / "order" / "index.html").write_text(page(lang, "order/", PO[lang]["o_title"] + " · Gravit Path", PO[lang]["o_lead"], nav2, order_page(lang)))
        (out / "order" / "send.php").write_text(SEND % (2 if lang == "en" else 3))
    print("built", ", ".join(LANGS))
