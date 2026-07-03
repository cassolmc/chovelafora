/* Logica da pagina de instalacao (install-only PWA).
   Carregado sincrono no <head>, logo apos pwa.js: o redirect e a captura
   do beforeinstallprompt precisam rodar antes do resto da pagina. */
(function () {
  "use strict";

  /* Ja esta rodando como app instalado? Vai direto para o jogo. */
  if (window.chvPWA && window.chvPWA.instalado()) {
    location.replace("jogo.html");
    return;
  }

  /* Service worker: requisito de instalabilidade + fallback offline */
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  }

  var FLAG = "chv_app_instalado";
  var bip  = null;   /* evento beforeinstallprompt guardado */
  var ui   = null;

  /* Chromium: capturar o quanto antes (pode disparar antes do DOM pronto).
     Se o navegador OFERECE instalar, e porque NAO esta instalado agora -
     evidencia mais confiavel que qualquer flag: limpa flag antiga
     (caso o usuario tenha desinstalado) e libera o botao. */
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    bip = e;
    try { localStorage.removeItem(FLAG); } catch (err) {}
    if (ui) ui.habilita();
  });

  /* Chromium: dispara quando a instalacao termina de verdade */
  window.addEventListener("appinstalled", function () {
    try { localStorage.setItem(FLAG, "1"); } catch (err) {}
    if (ui) ui.sucesso();
  });

  function montaUI() {
    var el     = function (id) { return document.getElementById(id); };
    var btn    = el("btn"), txt = el("btn-txt"), spin = el("spin");
    var dica   = el("dica"), ios = el("ios"), painel = el("painel-ok");

    ui = {
      habilita: function () {
        painel.hidden = true;
        btn.hidden = false;
        btn.disabled = false;
        spin.hidden = true;
        txt.textContent = "Instalar o jogo";
        dica.hidden = true;
      },
      /* Feedback forte depois que a instalacao conclui */
      sucesso: function () {
        btn.hidden = true;
        dica.hidden = true;
        painel.hidden = false;
        el("painel-titulo").textContent = "Jogo instalado!";
        el("painel-msg").innerHTML =
          "Agora abra o <strong>Chove Lá Fora</strong> pelo ícone " +
          "na tela inicial para jogar.";
      },
      /* Aparelho onde o app ja esta instalado, aberto no navegador */
      jaInstalado: function () {
        btn.hidden = true;
        dica.hidden = true;
        painel.hidden = false;
        el("painel-titulo").textContent = "Você já instalou o jogo!";
        el("painel-msg").innerHTML =
          "Abra pelo <strong>ícone na tela inicial</strong> para jogar.<br>" +
          "<small>Desinstalou? O botão de instalar volta a aparecer " +
          "aqui sozinho.</small>";
      },
      /* Prompt nunca liberou e nao ha evidencia de instalacao */
      manual: function () {
        spin.hidden = true;
        txt.textContent = "Instalar o jogo";
        dica.hidden = false;
        dica.innerHTML =
          "O instalador automático não liberou por aqui. " +
          "<strong>Já instalou?</strong> Abra pelo ícone na tela inicial. " +
          "<strong>Ainda não?</strong> No Chrome: menu &#8942; &rarr; " +
          "<em>\"Adicionar à tela inicial\"</em>.";
      }
    };

    /* iOS Safari: sem beforeinstallprompt - so o passo a passo */
    if (window.chvPWA.ehIOS()) {
      btn.hidden = true;
      dica.hidden = true;
      ios.hidden = false;
      return;
    }

    btn.addEventListener("click", function () {
      var evento = bip;
      if (!evento) return;
      bip = null;   /* o prompt so pode ser chamado uma vez */
      evento.prompt();
      evento.userChoice.then(function (escolha) {
        if (escolha.outcome === "accepted") {
          spin.hidden = false;
          btn.disabled = true;
          txt.textContent = "Instalando…";
          /* O appinstalled mostra o sucesso; failsafe caso nao dispare */
          setTimeout(function () {
            if (painel.hidden) ui.sucesso();
          }, 7000);
        } else {
          /* Recusou: o Chrome reoferece o prompt depois (o listener
             do beforeinstallprompt reabilita o botao sozinho) */
          spin.hidden = false;
          btn.disabled = true;
          txt.textContent = "Preparando instalação…";
          dica.hidden = false;
          dica.textContent =
            "Tudo bem! Quando quiser jogar, o botão libera de novo.";
        }
      });
    });

    if (bip) {
      ui.habilita();
      return;
    }

    /* Sem prompt (ainda): sera que ja esta instalado neste aparelho? */
    var achou = false;
    function marcaJa() {
      if (!bip) { achou = true; ui.jaInstalado(); }
    }

    /* Evidencia local: este aparelho instalou por esta pagina antes */
    try { if (localStorage.getItem(FLAG) === "1") marcaJa(); } catch (e) {}

    /* Chromium: pergunta ao navegador. Exige related_applications no
       manifest apontando para o proprio app (plataforma "webapp"). */
    if (navigator.getInstalledRelatedApps) {
      navigator.getInstalledRelatedApps().then(function (apps) {
        if (apps && apps.length) marcaJa();
      }).catch(function () {});
    }

    /* 6s sem prompt e sem evidencia: troca o spinner por instrucoes */
    setTimeout(function () {
      if (!bip && !achou) ui.manual();
    }, 6000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", montaUI);
  } else {
    montaUI();
  }
})();
