/* Koute — custom audio player controls (CSP-safe: external file, no inline handlers).
   Progressive enhancement over <div class="koute"><audio></audio></div>. */
(function () {
  function fmt(t) {
    if (!isFinite(t) || t < 0) t = 0;
    t = Math.floor(t);
    return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0');
  }
  function init() {
    var players = document.querySelectorAll('.koute');
    for (var i = 0; i < players.length; i++) {
      (function (k) {
        var audio = k.querySelector('audio');
        var btn = k.querySelector('.koute-btn');
        var fill = k.querySelector('.koute-fill');
        var time = k.querySelector('.koute-time');
        var track = k.querySelector('.koute-track');
        if (!audio || !btn) return;

        btn.addEventListener('click', function () {
          if (audio.paused) {
            // only one player at a time
            var others = document.querySelectorAll('.koute audio');
            for (var j = 0; j < others.length; j++) if (others[j] !== audio) others[j].pause();
            audio.play();
          } else {
            audio.pause();
          }
        });
        audio.addEventListener('play', function () {
          k.classList.add('playing');
          btn.setAttribute('aria-label', 'Kanpe');
        });
        audio.addEventListener('pause', function () {
          k.classList.remove('playing');
          btn.setAttribute('aria-label', 'Koute paj sa a');
        });
        audio.addEventListener('timeupdate', function () {
          var d = audio.duration || 0;
          if (fill) fill.style.width = (d ? (audio.currentTime / d) * 100 : 0) + '%';
          if (time) time.textContent = fmt(audio.currentTime);
        });
        audio.addEventListener('ended', function () {
          k.classList.remove('playing');
          if (fill) fill.style.width = '0%';
          if (time) time.textContent = '0:00';
        });
        if (track) {
          track.addEventListener('click', function (e) {
            var r = track.getBoundingClientRect();
            var p = (e.clientX - r.left) / r.width;
            if (audio.duration) audio.currentTime = Math.max(0, Math.min(1, p)) * audio.duration;
          });
        }
      })(players[i]);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
