#!/usr/bin/env python3
"""Делает index.html веб-версии для iPhone из HTML артефакта «2509».

    python3 tools/build_index.py путь/к/planer.html

Берёт тот же HTML, что идёт в Android (app/src/main/assets/index.html),
и добавляет в <head> только то, что нужно веб-приложению на экране «Домой»:
мета-теги iOS (непрозрачный статус-бар в цвет верхней панели), иконку, манифест
и офлайн-кэш (sw.js). Сам код приложения не меняется.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARK = '<!-- planernaroda: iPhone web app -->'
HEAD = MARK + r'''
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Планировщик">
<!-- статус-бар непрозрачный: с прозрачным («black-translucent») iOS 26 делает окно веб-приложения короче экрана
     на высоту статус-бара, и внизу остаётся пустая полоса, в которую страница не может рисовать
     (WebKit bug 301108). iOS читает этот тег только при добавлении на экран «Домой». -->
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#26282B">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="manifest" href="manifest.webmanifest">
<style>
  /* если страница всё же идёт под статус-бар — верхняя панель отступает на его высоту (при непрозрачном это 0) */
  #app .topbar{ padding-top:env(safe-area-inset-top, 0px); }
</style>
<script>
  /* цвет статус-бара (theme-color) — под цвет верхней панели текущей темы */
  (function(){
    function color(){
      try{
        var tb = document.querySelector('.topbar'), m = document.querySelector('meta[name="theme-color"]');
        if(!tb || !m) return;
        var cs = getComputedStyle(tb), bi = cs.backgroundImage, all = (bi && bi !== 'none' ? bi : '') + ' ' +
          cs.backgroundColor + ' ' + getComputedStyle(document.getElementById('app') || document.body).backgroundColor;
        var re = /rgba?\(([^)]+)\)/g, mm;
        while((mm = re.exec(all))){
          var v = mm[1].split(/[ ,\/]+/).map(parseFloat);
          if(v.length < 4 || v[3] >= .5){
            var c = 'rgb(' + Math.round(v[0]) + ',' + Math.round(v[1]) + ',' + Math.round(v[2]) + ')';
            if(m.content !== c) m.content = c;
            return;
          }
        }
      }catch(e){}
    }
    var t = 0; function soon(){ clearTimeout(t); t = setTimeout(color, 500); }
    addEventListener('load', function(){ setTimeout(color, 300); });
    document.addEventListener('click', soon, true);
    document.addEventListener('visibilitychange', soon);
    if(window.matchMedia) try{ matchMedia('(prefers-color-scheme: dark)').addEventListener('change', soon); }catch(e){}
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
