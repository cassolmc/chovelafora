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

## Deploy (GitHub Pages)

O jogo compilado fica em `docs/`. Para atualizar depois de mudar o código:

```bash
python -m pygbag --build main.py
rm -rf docs && mkdir docs && cp -r build/web/* docs/
git add -A && git commit -m "Atualiza build web" && git push
```

No GitHub: **Settings → Pages → Source: Deploy from a branch →
Branch: `main`, pasta `/docs`**.
