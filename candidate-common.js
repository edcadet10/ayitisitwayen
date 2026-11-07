(function(){
  'use strict';
  const menu=document.querySelector('.nav-toggle'),links=document.querySelector('.nav-links');
  if(menu&&links){
    menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));links.classList.toggle('active',open);});
    document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){menu.setAttribute('aria-expanded','false');links.classList.remove('active');menu.focus();}});
  }
  document.querySelector('.lang-switch')?.addEventListener('click',event=>{if(location.hash)event.currentTarget.hash=location.hash;try{localStorage.setItem('lang',document.documentElement.lang==='en'?'ht':'en');}catch(_){}});
  const portraitObserver='IntersectionObserver' in window?new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){const image=entry.target;image.src=image.dataset.portraitSrc;image.removeAttribute('data-portrait-src');portraitObserver.unobserve(image);}}},{rootMargin:'0px'}):null;
  function loadPortraits(){for(const image of document.querySelectorAll('img[data-portrait-src]')){if(portraitObserver)portraitObserver.observe(image);else{image.src=image.dataset.portraitSrc;image.removeAttribute('data-portrait-src');}}}
  loadPortraits();
  window.AyitiCandidates={copy:JSON.parse(document.getElementById('candidate-copy').textContent),lang:document.documentElement.lang==='en'?'en':'ht',loadPortraits};
})();
