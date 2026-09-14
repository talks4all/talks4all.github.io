/* Lembra o idioma escolhido, para que a raiz do site abra nele da próxima vez. */
(function () {
  var match = location.pathname.match(/^\/(pt|en|es)\//);
  if (!match) return;
  try { localStorage.setItem("talks4all:lang", match[1]); } catch (e) {}
})();
