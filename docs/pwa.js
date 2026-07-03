/* Deteccao de PWA instalado - modulo compartilhado entre a pagina de
   instalacao (index.html) e o jogo (jogo.html). */
window.chvPWA = (function () {
  "use strict";

  function instalado() {
    try {
      /* iOS Safari: nao implementa display-mode; expoe navigator.standalone
         quando aberto pelo icone da Tela de Inicio */
      if (window.navigator.standalone === true) return true;
      /* Chromium/Firefox: display-mode reflete o modo REAL do app.
         Nosso manifest usa "fullscreen", entao checar so "standalone"
         nao basta - um app fullscreen casa com (display-mode: fullscreen). */
      var modos = ["fullscreen", "standalone", "minimal-ui"];
      for (var i = 0; i < modos.length; i++) {
        if (window.matchMedia("(display-mode: " + modos[i] + ")").matches)
          return true;
      }
    } catch (e) { /* matchMedia indisponivel: trata como nao instalado */ }
    return false;
  }

  function ehIOS() {
    /* iPad com iPadOS 13+ se identifica como "MacIntel", mas tem touch */
    var ua = window.navigator.userAgent;
    return /iPad|iPhone|iPod/.test(ua) ||
      (window.navigator.platform === "MacIntel" &&
       window.navigator.maxTouchPoints > 1);
  }

  return { instalado: instalado, ehIOS: ehIOS };
})();
