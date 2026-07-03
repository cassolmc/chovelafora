# Sítio Chove Lá Fora

Jogo da Marina e da galinha punk Ramona — 6 fases no sítio da família.
Feito em Python + Pygame, roda no navegador (desktop e celular) via
[pygbag](https://pypi.org/project/pygbag/) (WebAssembly).

## Jogar (só instalado!)

**https://cassolmc.github.io/chovelafora/**

O jogo é **install-only**: no navegador comum aparece só a página de
instalação; o jogo roda apenas como app instalado (PWA em tela cheia).
No celular é só tocar/arrastar — todas as fases jogam com o dedo.

Repositório: https://github.com/cassolmc/chovelafora

## Rodar localmente

```bash
pip install pygame pygbag
python main.py              # janela nativa
python -m pygbag main.py    # navegador em http://localhost:8000
```

## Fases

1. **Xô Gavião!** — clique nos gaviões antes que peguem as galinhas
2. **O Galinheiro** — arraste as peças e construa o galinheiro com o Gilson
3. **Galinhas Doentes** — arraste o remédio certo para cada sintoma (3 rodadas)
4. **Achar a Ramona** — labirinto na floresta com a Grazi; cogumelos dão tempo extra
5. **Catar os Ovos** — pegue 24 ovos que caem dos ninhos em 90s (e deixe o ovo podre cair!)
6. **Anoitecer** — leve as 8 galinhas pro galinheiro antes de escurecer

## Instalar como app (PWA)

- **Chrome/Edge (Android e desktop)**: botão **"Instalar o jogo"** na
  própria página (via `beforeinstallprompt`).
- **Safari iOS**: compartilhar → **"Adicionar à Tela de Início"** (a página
  mostra o passo a passo — iOS não tem prompt de instalação).

Como funciona: `index.html` é a página de instalação; o jogo fica em
`jogo.html`, protegido por uma guarda (`pwa.js`) no início do `<head>` —
fora do modo standalone/fullscreen ele volta para a instalação **antes**
de baixar qualquer coisa pesada. O manifest aponta `start_url` para
`jogo.html` e o `sw.js` (service worker) dá cache offline básico.

## Deploy (GitHub Pages)

O jogo compilado fica em `docs/`. Para atualizar depois de mudar o código:

```bash
python deploy.py
git add -A && git commit -m "Atualiza build web" && git push
```

O `deploy.py` compila com o pygbag numa pasta limpa (só o código do jogo),
recria `docs/` e injeta no `index.html` o manifest/ícones do PWA e a tela
de abertura animada (Ramona passeando enquanto carrega). Os ícones e o
sprite vêm de `web/` (para regerar: `python web/gen_icons.py`).

No GitHub: **Settings → Pages → Source: Deploy from a branch →
Branch: `main`, pasta `/docs`**.
