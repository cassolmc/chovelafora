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
        for arq in ("manifest.json", "icon-192.png", "icon-512.png"):
            shutil.copy2(os.path.join(RAIZ, "web", arq), os.path.join(docs, arq))

        # 4. Injeta as tags do PWA no <head>
        index = os.path.join(docs, "index.html")
        with open(index, encoding="utf-8") as f:
            html = f.read()
        assert "</head>" in html, "index.html sem </head>?"
        html = html.replace("</head>", PWA_TAGS + "</head>", 1)
        with open(index, "w", encoding="utf-8") as f:
            f.write(html)

        print("\nOK! docs/ atualizado. Agora: git add -A && git commit && git push")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
