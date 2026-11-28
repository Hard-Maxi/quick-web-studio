import re,os,sys,json
sys.path.insert(0,__import__('os').path.dirname(__file__))
from i18n import T,NOTION,TITLE,DESC
REPO=__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))); BASE='https://quickweb.studio/'
src=open(''+__import__('os').path.dirname(__file__)+'/master_ru.html').read()
URL={'es':BASE,'ru':BASE+'ru/','en':BASE+'en/'}
LOC={'es':'es_AR','ru':'ru_RU','en':'en_US'}
def og(lang):
    img=BASE+'og/'+lang+'.jpg?v=5'
    alt=[l for l in ('es','ru','en') if l!=lang]
    return (f'<meta property="og:type" content="website">'
            f'<meta property="og:title" content="{TITLE[lang]}"><meta property="og:description" content="{DESC[lang]}">'
            f'<meta property="og:url" content="{URL[lang]}"><meta property="og:locale" content="{LOC[lang]}">'
            + ''.join(f'<meta property="og:locale:alternate" content="{LOC[l]}">' for l in alt) +
            f'<meta property="og:image" content="{img}"><meta property="og:image:secure_url" content="{img}"><meta property="og:image:type" content="image/jpeg">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{TITLE[lang]}">'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{TITLE[lang]}"><meta name="twitter:description" content="{DESC[lang]}"><meta name="twitter:image" content="{img}">')
def switcher(lang,pre):
    href={'es':(pre+'?lang=es') if pre else './?lang=es','ru':pre+'ru/','en':pre+'en/'}
    out=[]
    for l in ('es','ru','en'):
        lab=l.upper()
        out.append(f'<b style="color: #0B0B0F">{lab}</b>' if l==lang else f'<a href="{href[l]}" style="color: #55565C; text-decoration: none">{lab}</a>')
    return '<span style="color: #55565C">'+' · '.join(out)+'</span>'
HEAD_JS='''<script>(function(){var L='%s';try{var q=new URLSearchParams(location.search).get('lang');var s=localStorage.getItem('qwLang');if(L==='es'){if(q==='es'){localStorage.setItem('qwLang','es');return;}if(s==='ru'||s==='en'){location.replace(s+'/');return;}if(!s){var n=(navigator.languages||[navigator.language||'']).map(function(x){return String(x).slice(0,2).toLowerCase()});for(var i=0;i<n.length;i++){if(n[i]==='es')break;if(n[i]==='ru'||n[i]==='en'){localStorage.setItem('qwLang',n[i]);location.replace(n[i]+'/');return;}}localStorage.setItem('qwLang','es');}}else{localStorage.setItem('qwLang',L);}}catch(e){}})();</script>'''
def build(lang):
    s=src
    pre='' if lang=='es' else '../'
    if lang!='ru':
        # mask SERP demo data
        i=s.find('const _gL = ['); j=s.find('];',i)+2; serp=s[i:j]; s=s[:i]+'\x00SERP\x00'+s[j:]
        k=0 if lang=='es' else 1
        items=sorted(T.items(),key=lambda kv:-len(kv[0]))
        x=s.find('<x-dc>'); head,body=s[:x],s[x:]
        sc=body.find('<script type="text/x-dc"'); mk,js=body[:sc],body[sc:]
        for ru,tr in items:
            t=tr[k]
            # markup text nodes
            mk=re.sub(r'>(\s*)'+re.escape(ru)+r'(\s*)<',lambda m:'>'+m.group(1)+t+m.group(2)+'<',mk)
            mk=re.sub(r'((?:alt|aria-label|placeholder|title)=")'+re.escape(ru)+'"',lambda m:m.group(1)+t+'"',mk)
            js=js.replace("'"+ru+"'","'"+t.replace("'","\\'")+"'").replace('"'+ru+'"','"'+t.replace('"','\\"')+'"')
        # Notion typing words
        nm=NOTION[lang]
        mk=mk.replace('style="visibility: hidden">не</span>','style="visibility: hidden">'+nm['не']+'</span>')
        a=js.find("[[1, 0], [2, 3200]].forEach"); b=js.find('});',a)
        seg=js[a:b].replace("'не'","'"+nm['не']+"'").replace("'н'","'"+nm['н']+"'")
        js=js[:a]+seg+js[b:]
        if lang=='en': js=js.replace("_dqP[0] + '».'","_dqP[0] + '”.'")
        js=js.replace('(this.state.gl || 0)','(this.state.gl ?? %d)'%(1 if lang=='es' else 2))
        s=head+mk+js
        from urllib.parse import quote, unquote
        WA={'Привет, хочу первый экран бесплатно':('Hola, quiero la portada gratis','Hi, I’d like the first screen for free'),
            'Привет, хочу пакет «Экспресс»':('Hola, quiero el paquete «Express»','Hi, I’d like the “Express” package'),
            'Привет, хочу пакет «Стандарт»':('Hola, quiero el paquete «Estándar»','Hi, I’d like the “Standard” package'),
            'Привет, хочу пакет «Премиум»':('Hola, quiero el paquete «Premium»','Hi, I’d like the “Premium” package')}
        def _wa(m):
            t=unquote(m.group(2)); assert t in WA, t
            return m.group(1)+quote(WA[t][k])
        s=re.sub(r'(wa\.me/5491126963676\?text=)([^"\'\s]+)',_wa,s)
        s=s.replace('\x00SERP\x00',serp)
        left=[m for m in re.findall(r'>([^<>]*[А-Яа-яЁё][^<>]*)<',s[s.find('<x-dc>'):s.find('<script type="text/x-dc"')])]
        print(lang,'untranslated markup:',left[:20])
    s=s.replace('<html lang="ru">','<html lang="%s">'%lang)
    s=re.sub(r'<title>[^<]*</title>','<title>%s</title>'%TITLE[lang],s,1)
    hl=''.join(f'<link rel="alternate" hreflang="{l}" href="{URL[l]}">' for l in ('es','ru','en'))+f'<link rel="alternate" hreflang="x-default" href="{URL["es"]}"><link rel="canonical" href="{URL[lang]}"><meta name="description" content="{DESC[lang]}"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta name="theme-color" content="#0B0B0F">'+og(lang)+'<script src="assets/ars.js" defer></script>'
    s=s.replace('<meta charset="utf-8">','<meta charset="utf-8">\n'+(HEAD_JS%lang)+'\n'+hl,1)
    old='<span style="color: #55565C">ES · <b style="color: #0B0B0F">RU</b> · EN</span>'
    assert s.count(old)==1; s=s.replace(old,switcher(lang,pre))
    if pre: s=re.sub(r'(?<=["\'(;])assets/','../assets/',s)
    out=REPO+('/index.html' if lang=='es' else f'/{lang}/index.html')
    os.makedirs(os.path.dirname(out),exist_ok=True); open(out,'w').write(s)
for l in ('es','ru','en'): build(l)
# runtime: resolve react paths relative to the runtime script
import glob
for f in glob.glob(REPO+'/assets/*.js'):
    c=open(f).read()
    if 'dc-runtime' in c[:300] and '__qwB' not in c:
        c=re.sub(r'(vn|xn)="assets/([0-9a-f]+\.js)"',lambda m:m.group(1)+'=new URL("'+m.group(2)+'",__qwB).href',c)
        c='var __qwB=(document.currentScript&&document.currentScript.src)||location.href;\n'+c
        open(f,'w').write(c); print('runtime patched')
