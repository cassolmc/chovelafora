# Sítio Chove Lá Fora

Jogo da Marina e da galinha punk Ramona — 5 fases no sítio da família.
Feito em Python + Pygame, roda no navegador (desktop e celular) via
[pygbag](https://pypi.org/project/pygbag/) (WebAssembly).

## Jogar no navegador

**https://cassolmc.github.io/chovelafora/**

Funciona no Chrome (desktop e Android) e Safari (iOS). No celular é só
tocar/arrastar — todas as fases jogam com o dedo.

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
4. **Catar os Ovos** — pegue 20 ovos que caem dos ninhos em 90s
5. **Anoitecer** — leve as 8 galinhas pro galinheiro antes de escurecer

## Instalar como app (PWA)

No **Chrome Android**: abra o jogo → menu ⋮ → **"Adicionar à tela inicial"**
(ou "Instalar app"). No **Safari iOS**: botão compartilhar →
**"Adicionar à Tela de Início"**. O jogo abre em tela cheia, com ícone
próprio, como um app nativo.

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
