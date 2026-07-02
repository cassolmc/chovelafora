# Plano do Jogo: Marina no Sítio Chove Lá Fora

## 1. Visão Geral

Jogo arcade web para celular e navegador, sem instalação. Inspirado na Marina, nas galinhas e nos finais de semana no Sítio Chove Lá Fora em São Pedro de Alcântara.

**Gênero:** Arcade casual, fases curtas  
**Plataformas:** Android, iPhone, tablet, Chrome/Safari/Edge  
**Acesso:** Link direto, sem app store  
**Tom:** Colorido, fofo, humor familiar, pixel art

---

## 2. Personagens

### Jogável
| Personagem | Descrição | Habilidade no Jogo |
|---|---|---|
| **Marina** | Menina adorável, apaixonada por galinhas | Correr, pegar itens, guiar galinhas |
| **Mamãe Melina** | Cuida da casa e do galinheiro | Fases de limpeza e plantio |
| **Papai Jean** | Tarefas pesadas do sítio | Fases de construção e força |

### NPCs
| Personagem | Papel |
|---|---|
| **Gilson** | Vizinho amigo, aparece em fases de churrasco e construção |
| **Grazi** | Traz bônus: banana, pitaia, aipim |

### Galinhas (NPCs com comportamento próprio)
| Nome | Visual | Personalidade / IA |
|---|---|---|
| **Ramona** | Média, preta, topete branco | Segue Marina facilmente |
| **White** | Branco (é um galo!) | Tenta liderar as outras galinhas |
| **Bicadona** | Grande, Leghorn | Lenta, matriarca, ovos brancos grandes |
| **Bunda Pelada** | Grande, vermelha, sem penas no rabo | Curiosa, se afasta bastante |
| **Garni** | Garnizé pequena | Ovos azuis, nervosa |
| **Ganiza** | Filhote da Garni | Segue a mãe |
| **As Irmãs** | Três cinzas idênticas | Andam juntas, confundem o jogador |
| **Zebrinha** | Caipira brigona | Vai na direção errada, briga com as outras |

---

## 3. Referência Visual

Fotos em `jogo/` devem guiar cores, proporções e ambientação dos sprites:
- `marina.jpg`, `marina e ramona.jpg` → sprite da Marina e da Ramona
- `ramona.jpg`, `ramona 2.jpg`, `ramona e white.jpg`, `marina ramona white.jpg` → galinhas
- `stidio vista frontal.jpg` → cenário principal (gramado, casa, galinheiro)
- `flores.jpg` → decoração do cenário
- `galpao do churrasco e local das lenhas.jpg`, `galpao para churrasco.jpg` → fase do churrasco
- `marina e cacho de bananas.jpg` → elemento de bônus

---

## 4. Arquitetura Técnica

### Stack
- **Engine:** Phaser 3 (via CDN, sem build step)
- **Linguagem:** JavaScript ES6+
- **Renderização:** Canvas 2D
- **Hospedagem:** GitHub Pages ou Netlify (link direto)

### Resolução
- Canvas lógico: **480 × 854** (9:16 portrait)
- Scale mode: `Phaser.Scale.FIT` com `autoCenter`
- Funciona em portrait; sem necessidade de rotacionar

### Estrutura de Arquivos
```
game2/
├── index.html
├── game.js               ← entry point, configura Phaser
├── scenes/
│   ├── BootScene.js      ← carrega assets mínimos
│   ├── PreloadScene.js   ← barra de loading
│   ├── MenuScene.js      ← tela inicial
│   ├── HUDScene.js       ← pontos e tempo (overlay)
│   ├── Phase1Scene.js    ← Construir o Galinheiro
│   ├── Phase2Scene.js    ← Gaviões
│   ├── Phase3Scene.js    ← Galinhas Doentes
│   ├── Phase4Scene.js    ← Fugindo dos Lagartos
│   ├── Phase5Scene.js    ← Catar os Ovos
│   ├── Phase6Scene.js    ← Churrasco
│   ├── Phase7Scene.js    ← Anoiteceu
│   └── EndScene.js       ← tela de fim de fase / pontuação
├── entities/
│   ├── Marina.js
│   ├── Chicken.js        ← classe base para todas as galinhas
│   └── Hazard.js         ← gavião, lagarto
├── assets/
│   ├── images/           ← sprites, tiles, backgrounds
│   └── sounds/           ← efeitos e música
└── jogo/                 ← fotos de referência (não entram no bundle)
```

### Game Loop por Fase
1. **PreloadScene** carrega sprites e sons da fase
2. **Cena da fase** inicia, spawna entidades
3. **HUDScene** roda em paralelo (overlay de pontos/tempo)
4. Condição de vitória → transição para **EndScene**
5. **EndScene** exibe pontos, botões "Próxima Fase" e "Jogar Novamente"

---

## 5. Controles Mobile

Controles desenhados na própria canvas (não HTML sobreposto):

| Controle | Posição | Ação |
|---|---|---|
| Joystick virtual | Canto inferior esquerdo | Movimento |
| Botão de ação (grande) | Canto inferior direito | Pegar / Interagir |
| Botão pausa | Topo direito | Pausa |
| Botão reiniciar | Dentro do menu de pausa | Reinicia fase |

Em fases de arrastar (ovos, construção): touch drag diretamente no objeto.

---

## 6. Fases — Especificação Detalhada

### Fase 1: Construir o Galinheiro *(Papai Jean + Gilson + Marina)*

- **Mecânica:** Side-scrolling de tarefas. Itens (madeira, prego, tábua) aparecem no cenário. Marina carrega um por vez até a área de construção.
- **Obstáculo:** Galinhas atrapalhando o caminho.
- **Vitória:** Barra de progresso "construção" chega a 100% antes do timer.
- **Timer:** 90 segundos.
- **Bônus:** +50 pts por cada segundo sobrando.

### Fase 2: Proteger as Galinhas dos Gaviões *(Marina)*

- **Mecânica:** Visão top-down do gramado. Gaviões entram pela parte de cima da tela em parábolas. Marina toca na galinha para fazê-la correr para o galinheiro.
- **Obstáculo:** Zebrinha vai na direção errada toda vez. Gaviões aceleram com o tempo.
- **Vitória:** Salvar ≥ 6 de 8 galinhas.
- **Derrota:** Gavião pega 3 galinhas.
- **Timer:** 120 segundos.

### Fase 3: Galinhas Doentes *(Marina)*

- **Mecânica:** Puzzle de correspondência. Cada galinha exibe um ícone de sintoma. Bandeja com remédios diferentes. Arrastar remédio certo até a galinha certa.
- **Galinhas doentes por rodada:** 3 (aleatório).
- **Vitória:** Curar todas antes do timer.
- **Timer:** 60 segundos por rodada; 3 rodadas.

### Fase 4: Fugindo dos Lagartos *(Mamãe Melina + Marina)*

- **Mecânica:** Endless runner horizontal. Lagartos perseguem por baixo. Pular/desviar de obstáculos (pedras, buracos, flores).
- **Progressão:** Velocidade aumenta gradualmente.
- **Vitória:** Sobreviver 90 segundos.
- **Tom:** Engraçado — gritos exagerados, lagartos cartunescos.

### Fase 5: Catar os Ovos *(Marina)*

- **Mecânica:** Ovos caem de diferentes alturas. Marina se move horizontalmente para pegar. Cada ovo tem cor/tamanho identificável.
- **Ovos:**
  - Azul pequeno → Garni → cesto azul
  - Marrom grande → Bunda Pelada → cesto marrom
  - Branco grande → Bicadona → cesto branco
- **Erro:** Ovo no cesto errado = -10 pts. Ovo no chão = -5 pts.
- **Vitória:** Pegar 20 ovos corretos antes do timer.
- **Timer:** 90 segundos.

### Fase 6: Churrasco no Sítio *(Marina + Grazi + Gilson)*

- **Mecânica:** Jogo de defesa. Grazi entrega itens de comida. Marina coloca na mesa. Galinhas tentam roubar da mesa. Clicar/tocar na galinha invasora a afasta.
- **Bônus Grazi:** Banana, pitaia ou aipim → +30 pts ao pegar.
- **Vitória:** Mesa completa com 8 itens antes do fim da rodada.
- **Timer:** 120 segundos.

### Fase 7: Anoiteceu, Hora do Galinheiro *(Marina)*

- **Mecânica:** Visão top-down, céu escurecendo progressivamente. Marina guia galinhas ao galinheiro. Cada galinha tem comportamento diferente (tabela abaixo).
- **Comportamentos:**
  - Ramona: segue Marina se ela se aproximar
  - White: começa a guiar outras galinhas (ajuda)
  - Zebrinha: vai sempre na direção oposta
  - As Irmãs: seguem juntas, mas pausam muito
  - Bunda Pelada: vai longe, demora a reagir
- **Vitória:** Todas as 8 galinhas dentro do galinheiro antes de escurecer total.
- **Timer visual:** Céu passa de laranja → roxo → preto. Sem número, só visual.

---

## 7. Sistema de Pontuação

| Ação | Pontos |
|---|---|
| Galinha salva | +100 |
| Ovo no cesto certo | +20 |
| Ovo no cesto errado | -10 |
| Fase completa com tempo sobrando | +50 × segundos restantes |
| Galinha capturada por gavião | -50 |
| Item de bônus da Grazi | +30 |
| Fase completa sem erro | bônus estrela |

**Estrelas por fase:** 1 (completou), 2 (poucos erros), 3 (perfeito)

---

## 8. Progressão de Dificuldade

| Elemento | 1ª vez | 2ª jogada | 3ª jogada+ |
|---|---|---|---|
| Gaviões | 2, lentos | 3, médios | 4, rápidos |
| Timer | +30s | padrão | -15s |
| Zebrinha | ausente | presente | muito ativa |
| Ovos simultâneos | 1 | 2 | 3 |
| Lagartos | 1 | 2 | 3 |

---

## 9. Visual — Diretrizes de Arte

- **Resolução sprites:** 32×32 ou 64×64 px (pixel art)
- **Paleta:** Cores quentes, saturadas; verde gramado vivo, céu azul claro
- **Animações mínimas por sprite:** idle (2 frames), walk (4 frames), action (2 frames)
- **Cenários:** Fundo estático + elementos em camadas (parallax leve)
- **UI:** Fonte pixel, bordas arredondadas, ícones grandes para touch

### Cenários por Fase
| Fase | Fundo |
|---|---|
| 1 | Vista frontal do sítio, área de construção |
| 2 | Gramado top-down, galinheiro visível |
| 3 | Interior do galinheiro |
| 4 | Lateral do sítio com mato |
| 5 | Gramado com ninhos, vista lateral |
| 6 | Galpão do churrasco |
| 7 | Gramado top-down, céu escurecendo |

---

## 10. Sons

| Som | Quando |
|---|---|
| Música de fundo alegre (loop) | Durante as fases |
| Cocoricó do White | Início da fase 7 |
| Cacarejar | Galinha pega ou salva |
| Martelada | Fase de construção |
| Gavião (shhhhwww) | Gavião aparecendo |
| Grito engraçado | Lagarto encontrado |
| Ding | Item coletado |
| Erro (boing) | Ação errada |
| Fanfarra curta | Fase completa |

**Estratégia:** começar com sons placeholder (freesound.org, licença CC0). Trocar depois.

---

## 11. Roadmap de Desenvolvimento

### Marco 0 — Esqueleto (1–2 dias)
- [ ] `index.html` com Phaser 3 via CDN
- [ ] `MenuScene` com título e botão "Jogar"
- [ ] `Phase5Scene` (Catar Ovos) completa com placeholder sprites
- [ ] `EndScene` com pontuação e botão reiniciar
- [ ] Controles mobile funcionando (joystick virtual)

### Marco 1 — Fase Completa (3–5 dias)
- [ ] Sprites reais desenhados (Marina, galinhas, ovos, cenário)
- [ ] Sons básicos adicionados
- [ ] Fase 5 polida e jogável
- [ ] Deploy no GitHub Pages — link compartilhável

### Marco 2 — Mais Fases (1–2 semanas)
- [ ] Fase 2 (Gaviões)
- [ ] Fase 7 (Anoiteceu)
- [ ] Seletor de fases no menu

### Marco 3 — Fases Restantes (2–3 semanas)
- [ ] Fases 1, 3, 4, 6
- [ ] Sistema de estrelas
- [ ] Progressão de dificuldade

### Marco 4 — Polimento
- [ ] Música de fundo
- [ ] Animações de entrada/saída de fase
- [ ] Efeitos de partícula (penas voando, confete)
- [ ] Tela de créditos com fotos da família
- [ ] Teste em celular real (Android + iPhone)

---

## 12. Deploy e Acesso

1. Repositório público no GitHub
2. GitHub Pages ativado na branch `main`
3. Link: `https://[usuario].github.io/game2/`
4. Testar no Chrome Android e Safari iOS antes de compartilhar

---

## 13. Critério de "Pronto para Compartilhar"

O jogo está pronto para mostrar à família quando:
- [ ] Abre no celular sem erros
- [ ] Marina aparece e se move
- [ ] Pelo menos 1 fase completa é jogável do início ao fim
- [ ] Pontuação aparece
- [ ] Botão reiniciar funciona
- [ ] Não trava nem some da tela ao rotacionar
