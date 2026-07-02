"""
Deploy do jogo para GitHub Pages (pasta docs/).

  python deploy.py

1. Copia SO o codigo do jogo para uma pasta de staging (evita empacotar
   docs/, README, .git etc. dentro do game.apk - sem recursao).
2. Roda o pygbag --build no staging.
3. Recria docs/ com o build + manifest/icones do PWA.
4. Injeta as tags do PWA no index.html gerado.

Depois: git add -A && git commit && git push
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ  = os.path.dirname(os.path.abspath(__file__))
FONTE = ["main.py", "constants.py", "engine", "scenes", "characters"]
PWA_TAGS = """    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#2a7d2a">
    <link rel="apple-touch-icon" href="icon-192.png">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
"""

# Tela de abertura: cobre o loader feio do pygbag e some sozinha quando o
# jogo comeca (o SDL redimensiona o #canvas de 1px para o tamanho real).
# pointer-events:none deixa o toque "vazar" para o pygbag iniciar o jogo.
SPLASH = """<div id="splash">
  <div class="s-sun"></div>
  <div class="s-mid">
    <h1 class="s-title">Sítio<br>Chove Lá Fora</h1>
    <div class="s-msg">Carregando<span class="s-dots"></span></div>
    <div class="s-tap">toque ou clique para começar!</div>
  </div>
  <div class="s-grass"></div>
  <div id="s-walk"><img src="splash-ramona.png" alt="Ramona"></div>
</div>
<style>
#splash{position:fixed;inset:0;z-index:1000000;pointer-events:none;overflow:hidden;
  background:linear-gradient(#5fadde 0%,#a9d7f2 55%,#cfeafd 100%);
  display:flex;align-items:center;justify-content:center;
  font-family:"Segoe UI",system-ui,sans-serif;transition:opacity .6s ease}
#splash.out{opacity:0}
.s-mid{text-align:center;z-index:2;padding-bottom:9vh}
.s-title{margin:0 0 2rem;color:#fff;font-size:clamp(2.4rem,8vw,5rem);line-height:1.06;
  text-shadow:0 3px 0 #2a7d2a,0 7px 20px rgba(0,40,0,.4);letter-spacing:.02em}
.s-msg{color:#1d5c1d;font-weight:bold;font-size:clamp(1.1rem,3vw,1.6rem)}
.s-dots::after{content:"";animation:sdots 1.2s steps(4,end) infinite}
@keyframes sdots{0%{content:""}25%{content:"."}50%{content:".."}75%{content:"..."}}
.s-tap{margin-top:1.1rem;color:#fff;font-weight:bold;font-size:clamp(1rem,2.6vw,1.3rem);
  text-shadow:0 2px 4px rgba(0,0,0,.4);opacity:0;animation:stap 1.4s ease-in-out 4s infinite}
@keyframes stap{0%,100%{opacity:.15}50%{opacity:1}}
.s-sun{position:absolute;top:6vh;right:8vw;width:17vmin;height:17vmin;border-radius:50%;
  background:radial-gradient(circle,#fff7c8 30%,#ffe36e 58%,rgba(255,227,110,0) 72%);
  animation:ssun 3.5s ease-in-out infinite}
@keyframes ssun{0%,100%{transform:scale(1)}50%{transform:scale(1.14)}}
.s-grass{position:absolute;left:0;right:0;bottom:0;height:22%;
  background:linear-gradient(#7cc24f,#3f8f2c 60%,#2f6e21)}
#s-walk{position:absolute;bottom:calc(22% - 3.2vmin);left:0;z-index:3;
  animation:swalk 7.5s linear infinite}
#s-walk img{width:clamp(90px,15vmin,150px);image-rendering:pixelated;
  animation:shop .38s ease-in-out infinite alternate}
@keyframes swalk{from{transform:translateX(-22vw)}to{transform:translateX(106vw)}}
@keyframes shop{from{transform:translateY(0) rotate(-2deg)}to{transform:translateY(-9px) rotate(3deg)}}
</style>
<script>
(function(){
  // Roda antes do #canvas existir no DOM, entao consulta a cada tick
  // (tambem cobre o caso do runtime trocar o elemento canvas)
  var fim=false;
  function sair(){
    var sp=document.getElementById('splash');
    if(fim||!sp)return;
    fim=true;
    sp.classList.add('out');
    setTimeout(function(){sp.remove();},700);
    clearInterval(timer);
  }
  function jogoAbriu(){
    var cv=document.getElementById('canvas');
    return cv&&(cv.width|0)>64;
  }
  var timer=setInterval(function(){if(jogoAbriu())sair();},300);
  // Failsafe: nunca prender o jogador no splash - se 12s depois do
  // primeiro toque o jogo nao abriu, mostra a tela do pygbag por baixo
  window.addEventListener('pointerdown',function(){
    setTimeout(function(){if(!jogoAbriu())sair();},12000);
  },{once:true});
})();
</script>
"""


def main():
    tmp = tempfile.mkdtemp()
    try:
        # Nome fixo: o pygbag batiza o .apk com o nome da pasta
        staging = os.path.join(tmp, "chovelafora")
        os.makedirs(staging)
        # 1. Staging so com o codigo do jogo
        for item in FONTE:
            src = os.path.join(RAIZ, item)
            dst = os.path.join(staging, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst,
                                ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(src, dst)

        # 2. Build do pygbag
        subprocess.run([sys.executable, "-m", "pygbag", "--build", "main.py"],
                       cwd=staging, check=True)

        # 3. Recria docs/ com build + arquivos do PWA
        docs = os.path.join(RAIZ, "docs")
        if os.path.isdir(docs):
            shutil.rmtree(docs)
        shutil.copytree(os.path.join(staging, "build", "web"), docs)
        for arq in ("manifest.json", "icon-192.png", "icon-512.png",
                    "splash-ramona.png"):
            shutil.copy2(os.path.join(RAIZ, "web", arq), os.path.join(docs, arq))

        # 4. Injeta as tags do PWA no <head> e a tela de abertura no <body>
        index = os.path.join(docs, "index.html")
        with open(index, encoding="utf-8") as f:
            html = f.read()
        assert "</head>" in html, "index.html sem </head>?"
        assert "<body>" in html, "index.html sem <body>?"
        html = html.replace("</head>", PWA_TAGS + "</head>", 1)
        html = html.replace("<body>", "<body>\n" + SPLASH, 1)
        with open(index, "w", encoding="utf-8") as f:
            f.write(html)

        print("\nOK! docs/ atualizado. Agora: git add -A && git commit && git push")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
