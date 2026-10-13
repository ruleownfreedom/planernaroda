#!/usr/bin/env python3
"""Делает index.html веб-версии для iPhone из HTML артефакта «2509».

    python3 tools/build_index.py путь/к/planer.html

Берёт тот же HTML, что идёт в Android (app/src/main/assets/index.html),
и добавляет в <head> только то, что нужно веб-приложению на экране «Домой»:
мета-теги iOS, иконку, манифест, отступ верхней панели под статус-бар
и офлайн-кэш (sw.js). Сам код приложения не меняется.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARK = '<!-- planernaroda: iPhone web app -->'
HEAD = MARK + r'''
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Планировщик">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="manifest" href="manifest.webmanifest">
<style>
  /* на экране «Домой» страница идёт под статус-бар: верхняя панель отступает на его высоту */
  #app .topbar{ padding-top:env(safe-area-inset-top, 0px); }
  /* iOS на экране «Домой» с прозрачным статус-баром делает окно страницы ниже экрана на высоту статус-бара —
     внизу, у скруглений, оставалась пустая полоса. Тело страницы растягивается на эту разницу (её меряет скрипт ниже),
     и всё, что прижато к низу (панели, шторки, кнопка «+»), встаёт к настоящему низу экрана. */
  html.web-gap body{ position:fixed; top:0; left:0; right:0; height:calc(100% + var(--web-gap, 0px)); transform:translateZ(0); }
  html.web-gap #app{ height:100%; }
  html.web-gap .lockveil{ height:100% !important; }
</style>
<script>
  /* статус-бар iPhone: над тёмной верхней панелью — прозрачный со светлым текстом (панель уходит под него),
     над светлой — обычный с тёмным текстом. iOS читает это при запуске, поэтому цвет панели запоминается
     при уходе из приложения и применяется при следующем открытии. */
  (function(){
    var st = null;
    try{
      st = localStorage.getItem('planer_web_statusbar');
      if(st !== 'default' && st !== 'black-translucent'){
        var s = JSON.parse(localStorage.getItem('planner_settings_v1') || 'null'), sc = s && s.ui && s.ui.scheme;
        st = (sc === 'dark' || (sc !== 'light' && !(window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches))) ? 'black-translucent' : 'default';
      }
    }catch(e){ st = 'default'; }
    var m = document.createElement('meta'); m.name = 'apple-mobile-web-app-status-bar-style'; m.content = st;
    document.head.appendChild(m);
    /* разница между высотой экрана и окна страницы (см. «web-gap» выше); пока открыта клавиатура — как было,
       чтобы не сбить подъём форм над клавиатурой */
    function fitGap(){
      try{
        var d = document.documentElement, vv = window.visualViewport;
        if(vv && window.innerHeight - vv.height > 80) return;
        var standalone = navigator.standalone === true || (window.matchMedia && matchMedia('(display-mode: standalone)').matches);
        var land = window.innerWidth > window.innerHeight;
        var full = land ? Math.min(screen.width, screen.height) : Math.max(screen.width, screen.height);
        var gap = full - window.innerHeight;
        if(standalone && st === 'black-translucent' && gap > 0 && gap < 120){
          d.style.setProperty('--web-gap', gap + 'px'); d.classList.add('web-gap');
        } else { d.classList.remove('web-gap'); d.style.removeProperty('--web-gap'); }
      }catch(e){}
    }
    fitGap();
    addEventListener('resize', fitGap);
    addEventListener('orientationchange', function(){ setTimeout(fitGap, 300); });
    if(window.visualViewport) window.visualViewport.addEventListener('resize', function(){
      var vv = window.visualViewport, d = document.documentElement;
      if(window.innerHeight - vv.height > 80){ d.classList.remove('web-gap'); } else fitGap();
    });
    function remember(){
      try{
        var tb = document.querySelector('.topbar'); if(!tb) return;
        var cs = getComputedStyle(tb), bi = cs.backgroundImage, all = (bi && bi !== 'none' ? bi : '') + ' ' +
          cs.backgroundColor + ' ' + getComputedStyle(document.getElementById('app') || document.body).backgroundColor;
        var c = null, re = /rgba?\(([^)]+)\)/g, mm;
        while((mm = re.exec(all))){ var v = mm[1].split(/[ ,\/]+/).map(parseFloat); if(v.length < 4 || v[3] >= .5){ c = v; break; } }
        if(!c) return;
        var L = (.299 * c[0] + .587 * c[1] + .114 * c[2]) / 255;
        localStorage.setItem('planer_web_statusbar', L < .55 ? 'black-translucent' : 'default');
      }catch(e){}
    }
    addEventListener('load', function(){ setTimeout(remember, 1500); });
    document.addEventListener('visibilitychange', function(){ if(document.hidden) remember(); });
    addEventListener('pagehide', remember);
  })();
  if('serviceWorker' in navigator && location.protocol === 'https:'){
    addEventListener('load', function(){ navigator.serviceWorker.register('sw.js').catch(function(){}); });
  }
  try{ if(navigator.storage && navigator.storage.persist) navigator.storage.persist(); }catch(e){}
</script>
'''

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
    if MARK in src:
        sys.exit('Это уже веб-версия — дайте исходный HTML артефакта.')
    vp = src.find('<meta name="viewport"')
    if vp < 0:
        sys.exit('Не найден <meta name="viewport"> в <head>.')
    end = src.index('>', vp) + 1
    out = src[:end] + '\n' + HEAD + src[end:]
    out = out.replace('<title>2509</title>', '<title>Планировщик</title>', 1)
    (ROOT / 'index.html').write_text(out, encoding='utf-8')
    print('index.html:', len(out), 'символов')

if __name__ == '__main__':
    main()
