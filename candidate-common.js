(function(){
  'use strict';
  const menu=document.querySelector('.nav-toggle'),links=document.querySelector('.nav-links');
  if(menu&&links){
    menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));links.classList.toggle('active',open);});
    document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){menu.setAttribute('aria-expanded','false');links.classList.remove('active');menu.focus();}});
  }
  document.querySelector('.lang-switch')?.addEventListener('click',event=>{if(location.hash)event.currentTarget.hash=location.hash;try{localStorage.setItem('lang',document.documentElement.lang==='en'?'ht':'en');}catch(_){}});
  function revealPortrait(image){
    if(image.dataset.portraitSizes)image.sizes=image.dataset.portraitSizes;
    if(image.dataset.portraitSrcset)image.srcset=image.dataset.portraitSrcset;
    image.src=image.dataset.portraitSrc;
    for(const attribute of ['data-portrait-src','data-portrait-srcset','data-portrait-sizes'])image.removeAttribute(attribute);
  }
  const portraitObserver='IntersectionObserver' in window?new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){revealPortrait(entry.target);portraitObserver.unobserve(entry.target);}}},{rootMargin:'0px'}):null;
  function loadPortraits(){for(const image of document.querySelectorAll('img[data-portrait-src]')){if(portraitObserver)portraitObserver.observe(image);else revealPortrait(image);}}
  loadPortraits();
  window.AyitiCandidates={copy:JSON.parse(document.getElementById('candidate-copy').textContent),lang:document.documentElement.lang==='en'?'en':'ht',loadPortraits};
})();
