(function(){
  'use strict';
  const {copy:c,lang}=window.AyitiCandidates,data=JSON.parse(document.getElementById('candidate-profile-data').textContent);
  const section=document.getElementById('information-web'),stage=document.getElementById('web-stage'),threads=document.getElementById('web-threads'),nodes=document.getElementById('web-nodes');
  const empty=document.getElementById('web-preview-empty'),panel=document.getElementById('web-preview-content'),action=document.getElementById('web-preview-action'),video=document.getElementById('web-video');
  const archive=document.querySelector('.candidate-source-list'),back=document.getElementById('web-back'),breadcrumb=document.getElementById('web-breadcrumb');
  const ns='http://www.w3.org/2000/svg',size=8;
  const element=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  let category=null,page=0,selected=-1,resizeFrame=0;
  const list=()=>category===null?data.categories:data.sources.filter(source=>source.categories.includes(category));
  const visible=()=>list().slice(page*size,page*size+size);
  const count=key=>data.sources.filter(source=>source.categories.includes(key)).length;
  function highlight(index){
    for(const button of nodes.children)button.classList.toggle('selected',Number(button.dataset.index)===index);
    for(const strand of threads.querySelectorAll('[data-branch]'))strand.classList.toggle('lit',index>=0&&Number(strand.dataset.branch)===Number(nodes.children[index]?.dataset.slot));
  }
  function close(){selected=-1;panel.hidden=true;empty.hidden=false;video.replaceChildren();highlight(-1);}
  function show(index){
    const item=visible()[index];if(!item)return;
    const prior=selected;selected=index;empty.hidden=true;panel.hidden=false;highlight(index);action.replaceChildren();if(prior!==index)video.replaceChildren();
    const type=document.getElementById('web-preview-type'),title=document.getElementById('web-preview-title'),summary=document.getElementById('web-preview-summary'),publisher=document.getElementById('web-preview-publisher'),date=document.getElementById('web-preview-date');
    if(category===null){
      const total=count(item.key);type.textContent=total+' '+c.sources;title.textContent=item.label;summary.textContent=total?c.follow:c.no_sources;publisher.textContent='';date.textContent='';
      if(total){const button=element('button','candidate-button',c.follow+' →');button.type='button';button.addEventListener('click',()=>expand(item.key));action.append(button);}return;
    }
    type.textContent=c[item.type];title.textContent=item.title[lang];summary.textContent=item.summary[lang];publisher.textContent=c.source+': '+item.publisher;
    date.textContent=(item.published_at?c.published+': '+item.published_at:c.date_unknown)+' · '+c.reviewed+': '+item.reviewed_at;
    const link=element('a','candidate-button',item.native?c.registry_title+' ↑':c.original+' ↗');link.href=item.native?'#registration':item.url;
    if(!item.native){link.target='_blank';link.rel='noopener noreferrer';}
    action.append(link);
    if(item.native)action.append(element('p','source-date',c.native_record));
    if(item.video_id&&/^[A-Za-z0-9_-]{11}$/.test(item.video_id)){
      const play=element('button','candidate-button secondary',c.play+' ▷');play.type='button';
      play.addEventListener('click',()=>{video.replaceChildren();const iframe=element('iframe');iframe.src='https://www.youtube-nocookie.com/embed/'+item.video_id+'?autoplay=0';iframe.title=item.title[lang];iframe.allow='encrypted-media; picture-in-picture';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';video.append(iframe);play.disabled=true;});
      action.append(play,element('p','source-date',c.no_autoplay));
    }
  }
  function expand(key){category=key;page=0;selected=-1;close();draw();nodes.firstElementChild?.focus({preventScroll:true});}
  function svg(tag,attrs){const el=document.createElementNS(ns,tag);for(const[key,value]of Object.entries(attrs))el.setAttribute(key,value);threads.append(el);return el;}
  function draw(){
    const focusIndex=nodes.contains(document.activeElement)?Number(document.activeElement.dataset.index):-1;
    const w=stage.clientWidth,h=stage.clientHeight,cx=w/2,cy=h/2,r=Math.min(w*.35,h*.35),outer=r/.73;
    const angles=Array.from({length:16},(_,i)=>-Math.PI/2+i*Math.PI/8),rings=[.19,.30,.41,.52,.63,.73,.85,1];
    const polar=(angle,radius)=>({x:cx+Math.cos(angle)*radius,y:cy+Math.sin(angle)*radius});
    const points=rings.map((fraction,ring)=>angles.map((angle,i)=>polar(angle,outer*fraction*(1+Math.sin(i*1.7+ring*.27)*.018))));
    threads.replaceChildren();nodes.replaceChildren();threads.setAttribute('viewBox',`0 0 ${w} ${h}`);
    angles.forEach((angle,i)=>{
      const reach=Math.min((w/2-8)/Math.max(Math.abs(Math.cos(angle)),.0001),(h/2-8)/Math.max(Math.abs(Math.sin(angle)),.0001)),anchor=polar(angle,reach);
      let d=`M ${cx} ${cy}`;for(const ring of points)d+=` L ${ring[i].x} ${ring[i].y}`;d+=` L ${anchor.x} ${anchor.y}`;
      svg('path',{d,class:'web-radius'+(i%2===0?' main':''),'data-branch':i%2===0?i/2:-1});
    });
    points.forEach((ring,ringIndex)=>{
      let d=`M ${ring[0].x} ${ring[0].y}`;ring.forEach((point,i)=>{const next=ring[(i+1)%16],mx=(point.x+next.x)/2,my=(point.y+next.y)/2;d+=` Q ${cx+(mx-cx)*.958} ${cy+(my-cy)*.958} ${next.x} ${next.y}`;});
      svg('path',{d:d+' Z',class:'web-loop'});
      if(ringIndex>1)ring.forEach((point,i)=>svg('circle',{cx:point.x,cy:point.y,r:i%2===0?1.4:1,class:'web-knot','data-branch':i%2===0?i/2:-1}));
    });
    const items=visible();
    items.forEach((item,index)=>{
      const slot=Math.floor(index*8/items.length),point=points[5][slot*2],total=category===null?count(item.key):null;
      const button=element('button','web-node'+(total===0?' empty':''));button.type='button';button.dataset.index=index;button.dataset.slot=slot;button.style.left=point.x+'px';button.style.top=point.y+'px';
      const icon=element('span','web-node-icon',category===null?item.icon:(item.format==='video'?'▷':item.type==='official'?'▥':item.categories.includes('social')?'@':'▤'));icon.setAttribute('aria-hidden','true');
      const text=category===null?item.label:item.publisher;button.append(icon,element('span','web-node-label',text));
      button.setAttribute('aria-label',category===null?item.label+' — '+total+' '+c.sources:item.title[lang]+' — '+item.publisher);
      if(category===null)button.append(element('span','web-node-count',String(total)));
      button.addEventListener('mouseenter',()=>show(index));button.addEventListener('focus',()=>show(index));
      button.addEventListener('click',()=>{if(category===null&&total)expand(item.key);else{show(index);if(category!==null)history.replaceState(null,'',location.pathname+'#source='+encodeURIComponent(item.id));}});
      button.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowUp','ArrowRight','ArrowDown','Home','End'].includes(event.key)){event.preventDefault();const next=event.key==='Home'?0:event.key==='End'?items.length-1:(index+(['ArrowLeft','ArrowUp'].includes(event.key)?-1:1)+items.length)%items.length;nodes.children[next].focus();}});
      nodes.append(button);
    });
    back.hidden=category===null;breadcrumb.textContent=category===null?c.web_hint:data.categories.find(topic=>topic.key===category).label;
    const totalPages=Math.max(1,Math.ceil(list().length/size));document.getElementById('web-pages').hidden=totalPages<=1;document.getElementById('web-page-count').textContent=(page+1)+' / '+totalPages;document.getElementById('web-previous').disabled=page===0;document.getElementById('web-next').disabled=page>=totalPages-1;
    if(!items.length){empty.hidden=false;document.querySelector('#web-preview-empty h3').textContent=c.no_sources;}
    if(selected>=0&&selected<items.length)show(selected);
    if(focusIndex>=0)nodes.children[Math.min(focusIndex,items.length-1)]?.focus({preventScroll:true});
  }
  back.addEventListener('click',()=>{category=null;page=0;close();draw();nodes.firstElementChild?.focus({preventScroll:true});});
  document.getElementById('web-close').addEventListener('click',close);
  document.addEventListener('keydown',event=>{if(event.key==='Escape')close();});
  for(const[key,delta]of [['web-previous',-1],['web-next',1]])document.getElementById(key).addEventListener('click',()=>{page+=delta;close();draw();nodes.firstElementChild?.focus({preventScroll:true});});
  section.hidden=false;draw();
  new ResizeObserver(()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(draw);}).observe(stage);
  const typeFilter=document.getElementById('source-type-filter'),sort=document.getElementById('source-date-sort');document.querySelector('.candidate-archive-filters').hidden=false;
  function filterArchive(){const cards=[...archive.querySelectorAll('[data-source-id]')];cards.sort((a,b)=>{const x=a.dataset.sourceDate,y=b.dataset.sourceDate;if(!x)return y?1:0;if(!y)return -1;return sort.value==='oldest'?x.localeCompare(y):y.localeCompare(x);});for(const card of cards){card.hidden=Boolean(typeFilter.value&&card.dataset.sourceType!==typeFilter.value);archive.append(card);}}
  typeFilter.addEventListener('change',filterArchive);sort.addEventListener('change',filterArchive);filterArchive();
  const share=document.getElementById('candidate-share');share.hidden=false;share.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);document.getElementById('candidate-share-status').textContent=c.copied;}catch(_){document.getElementById('candidate-share-status').textContent=c.copy_failed;}});
  try{const saved=JSON.parse(sessionStorage.getItem('candidate-directory-return'));if(saved){const url=new URL(saved.path,location.origin),expected=(lang==='en'?'/en/':'/')+'candidates/';if(url.origin===location.origin&&url.pathname.startsWith(expected))document.getElementById('candidate-back').href=url.pathname+url.search;}}catch(_){}
  if(location.hash.startsWith('#source=')){const id=new URLSearchParams(location.hash.slice(1)).get('source'),source=data.sources.find(item=>item.id===id);if(source){category=source.categories[0];const index=list().findIndex(item=>item.id===id);page=Math.floor(index/size);selected=index%size;draw();section.scrollIntoView({block:'start'});}}
  else if(location.hash==='#information-web')requestAnimationFrame(()=>section.scrollIntoView({block:'start',behavior:'auto'}));
})();
