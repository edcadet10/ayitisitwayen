(function(){
  'use strict';
  const {copy:c,lang}=window.AyitiCandidates,data=JSON.parse(document.getElementById('candidate-profile-data').textContent);
  const section=document.getElementById('information-web'),stage=document.getElementById('web-stage'),threads=document.getElementById('web-threads'),nodes=document.getElementById('web-nodes');
  const empty=document.getElementById('web-preview-empty'),panel=document.getElementById('web-preview-content'),action=document.getElementById('web-preview-action'),video=document.getElementById('web-video');
  const archive=document.querySelector('.candidate-source-list'),back=document.getElementById('web-back'),breadcrumb=document.getElementById('web-breadcrumb');
  const title=document.getElementById('web-preview-title'),shareStatus=document.getElementById('candidate-share-status');
  const narrow=matchMedia('(max-width:900px)'),hover=matchMedia('(hover:hover)'),ns='http://www.w3.org/2000/svg',size=8;
  const element=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  const dialog=element('dialog','web-preview-dialog');dialog.id='web-mobile-preview';dialog.setAttribute('aria-labelledby','web-preview-title');document.body.append(dialog);title.tabIndex=-1;
  const context=element('p','preview-candidate',data.name);document.getElementById('web-preview-type').before(context);
  let category=null,page=0,selected=-1,pinned=false,suppressFocus=false,resizeFrame=0,returnFocus=null,oldOverflow='';
  const list=()=>category===null?data.categories:data.sources.filter(source=>source.categories.includes(category));
  const visible=()=>list().slice(page*size,page*size+size);
  const count=key=>data.sources.filter(source=>source.categories.includes(key)).length;
  const format=source=>c['format_'+source.format]||c.format_article;
  function hash(value){history.replaceState(null,'',location.pathname+location.search+'#'+value);}
  const sourceAddress=item=>'source='+encodeURIComponent(item.id)+'&topic='+encodeURIComponent(category);
  function focusNode(node){if(!node)return;suppressFocus=true;node.focus({preventScroll:true});suppressFocus=false;}
  function highlight(index){
    for(const button of nodes.children){const active=Number(button.dataset.index)===index;button.classList.toggle('selected',active);button.setAttribute('aria-pressed',String(active));}
    for(const strand of threads.querySelectorAll('[data-branch]'))strand.classList.toggle('lit',index>=0&&Number(strand.dataset.branch)===Number(nodes.children[index]?.dataset.slot));
  }
  function dismissDialog(){
    if(!dialog.open)return;
    dialog.close();empty.after(panel);document.body.style.overflow=oldOverflow;
  }
  function close({restore=false,updateHash=false}={}){
    const target=returnFocus?.isConnected?returnFocus:nodes.children[selected];
    suppressFocus=true;dismissDialog();suppressFocus=false;
    selected=-1;pinned=false;panel.hidden=true;empty.hidden=false;video.replaceChildren();highlight(-1);
    if(updateHash)hash(category===null?'information-web':'topic='+encodeURIComponent(category));
    if(restore)focusNode(target);returnFocus=null;
  }
  async function copyLink(status){
    try{await navigator.clipboard.writeText(location.href);status.textContent=c.copied;}
    catch(_){status.textContent=c.copy_failed;}
  }
  function show(index){
    const item=visible()[index];if(!item)return;
    const prior=selected;selected=index;empty.hidden=true;panel.hidden=false;highlight(index);action.replaceChildren();if(prior!==index)video.replaceChildren();
    const type=document.getElementById('web-preview-type'),summary=document.getElementById('web-preview-summary'),publisher=document.getElementById('web-preview-publisher'),date=document.getElementById('web-preview-date');
    if(category===null){
      const total=count(item.key);type.textContent=total+' '+c.sources;title.textContent=item.label;summary.textContent=c.web_source_hint;publisher.textContent='';date.textContent='';
      if(total){const button=element('button','candidate-button',c.follow+' →');button.type='button';button.addEventListener('click',()=>expand(item.key));action.append(button);}return;
    }
    type.textContent=c[item.type]+' · '+format(item);title.textContent=item.title[lang];summary.textContent=item.summary[lang];publisher.textContent=c.source+': '+item.publisher;
    date.textContent=(item.published_at?c.published+': '+item.published_at:c.date_unknown)+' · '+c.reviewed+': '+item.reviewed_at;
    const link=element('a','candidate-button',item.native?c.registry_title+' ↑':c.original+' ↗');link.href=item.native?'#registration':item.url;
    if(!item.native){link.target='_blank';link.rel='noopener noreferrer';}
    else link.addEventListener('click',()=>close());
    action.append(link);
    if(item.native){
      const facts=element('dl','web-record-facts');
      for(const fact of data.registration||[]){const row=element('div');row.append(element('dt','',fact.label),element('dd','',fact.value));facts.append(row);}
      action.prepend(facts);action.append(element('p','source-date',c.native_record));
    }
    if(item.access==='account')action.append(element('p','source-access-note',c.source_account_note));
    if(item.video_id&&/^[A-Za-z0-9_-]{11}$/.test(item.video_id)){
      const play=element('button','candidate-button secondary',c.play+' ▷');play.type='button';
      play.addEventListener('click',()=>{pinned=true;video.replaceChildren();const iframe=element('iframe');iframe.src='https://www.youtube-nocookie.com/embed/'+item.video_id+'?autoplay=0';iframe.title=item.title[lang];iframe.allow='encrypted-media; picture-in-picture';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';video.append(iframe);play.disabled=true;iframe.scrollIntoView({block:'nearest',behavior:'smooth'});});
      action.append(play,element('p','source-date',c.no_autoplay));
    }
    const copy=element('button','candidate-clear source-copy',c.share_source);copy.type='button';const status=element('span','source-copy-status');status.setAttribute('role','status');
    copy.addEventListener('click',()=>{hash(sourceAddress(item));copyLink(status);});action.append(copy,status);
  }
  function activate(index){
    show(index);pinned=true;
    if(category===null)return;
    hash(sourceAddress(visible()[index]));
    if(narrow.matches&&typeof dialog.showModal==='function'){
      returnFocus=nodes.children[index];oldOverflow=document.body.style.overflow;dialog.append(panel);dialog.showModal();document.body.style.overflow='hidden';title.focus({preventScroll:true});
    }
  }
  function expand(key,{writeHash=true,openSingle=true}={}){
    close();category=key;page=0;draw();if(writeHash)hash('topic='+encodeURIComponent(key));
    focusNode(nodes.firstElementChild);
    if(list().length===1&&openSingle)activate(0);
  }
  function svg(tag,attrs){const el=document.createElementNS(ns,tag);for(const[key,value]of Object.entries(attrs))el.setAttribute(key,value);threads.append(el);return el;}
  function draw(){
    const focused=nodes.contains(document.activeElement)?Number(document.activeElement.dataset.index):-1;
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
      const button=element('button','web-node'+(total===0?' empty':'')+(category!==null?' source-node':''));button.type='button';button.dataset.index=index;button.dataset.slot=slot;button.style.left=point.x+'px';button.style.top=point.y+'px';
      const icon=element('span','web-node-icon',category===null?item.icon:(item.format==='video'?'▷':item.type==='official'?'▥':item.format==='portrait'?'◉':item.format==='account'?'@':String(page*size+index+1)));icon.setAttribute('aria-hidden','true');
      const text=category===null?item.label:(item.short_title?.[lang]||item.title[lang]);button.append(icon,element('span','web-node-label',text));
      button.setAttribute('aria-label',category===null?item.label+' — '+total+' '+c.sources:item.title[lang]+' — '+item.publisher);button.title=category===null?item.label+(total===0?' — '+c.no_sources:''):item.title[lang];
      if(category===null)button.append(element('span','web-node-count',String(total)));
      if(total===0){button.disabled=true;button.setAttribute('aria-label',item.label+' — '+c.no_sources);}
      else{
        button.addEventListener('mouseenter',()=>{if(hover.matches&&!pinned)show(index);});
        button.addEventListener('focus',()=>{if(!suppressFocus&&!dialog.open)show(index);});
        button.addEventListener('click',()=>{if(category===null)expand(item.key);else activate(index);});
        button.addEventListener('keydown',event=>{
          if(!['ArrowLeft','ArrowUp','ArrowRight','ArrowDown','Home','End'].includes(event.key))return;
          event.preventDefault();const enabled=[...nodes.children].filter(node=>!node.disabled),position=enabled.indexOf(button),next=event.key==='Home'?0:event.key==='End'?enabled.length-1:(position+(['ArrowLeft','ArrowUp'].includes(event.key)?-1:1)+enabled.length)%enabled.length;enabled[next]?.focus();
        });
      }
      nodes.append(button);
    });
    back.hidden=category===null;breadcrumb.textContent=category===null?c.web_hint:data.categories.find(topic=>topic.key===category).label+' · '+list().length+' '+c.sources;
    document.getElementById('web-state-hint').textContent=category===null?c.web_available_hint:c.web_source_hint;
    const totalPages=Math.max(1,Math.ceil(list().length/size));document.getElementById('web-pages').hidden=totalPages<=1;document.getElementById('web-page-count').textContent=(page+1)+' / '+totalPages;document.getElementById('web-previous').disabled=page===0;document.getElementById('web-next').disabled=page>=totalPages-1;
    if(selected>=0&&selected<items.length)highlight(selected);
    if(focused>=0)focusNode(nodes.children[Math.min(focused,items.length-1)]);
  }
  back.addEventListener('click',()=>{const previous=category;close();category=null;page=0;draw();hash('information-web');focusNode(nodes.children[data.categories.findIndex(topic=>topic.key===previous)]);});
  document.getElementById('web-close').addEventListener('click',()=>close({restore:true,updateHash:true}));
  dialog.addEventListener('cancel',event=>{event.preventDefault();close({restore:true,updateHash:true});});
  dialog.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const controls=[...dialog.querySelectorAll('a[href],button:not(:disabled),iframe')].filter(control=>control.getClientRects().length);
    const first=controls[0],last=controls.at(-1),active=document.activeElement;
    if(event.shiftKey&&(active===first||!controls.includes(active))){event.preventDefault();last?.focus();}
    else if(!event.shiftKey&&(active===last||!controls.includes(active))){event.preventDefault();first?.focus();}
  });
  dialog.addEventListener('click',event=>{if(event.target===dialog){const box=dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)close({restore:true,updateHash:true});}});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!dialog.open)close({restore:true,updateHash:true});});
  for(const[key,delta]of [['web-previous',-1],['web-next',1]])document.getElementById(key).addEventListener('click',()=>{close();page+=delta;draw();focusNode(nodes.firstElementChild);});
  const hint=element('p','web-state-hint');hint.id='web-state-hint';hint.setAttribute('role','status');document.querySelector('.candidate-web-toolbar').after(hint);
  if(data.sources.every(source=>source.native)){const note=element('p','web-coverage-note',c.web_registry_only);document.querySelector('.candidate-web-heading').after(note);}
  document.querySelector('.web-centre').setAttribute('aria-label',c.view_registration+' — '+data.name);
  document.querySelector('.web-centre').addEventListener('click',()=>close());
  section.hidden=false;draw();
  new ResizeObserver(()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(draw);}).observe(stage);
  const typeFilter=document.getElementById('source-type-filter'),sort=document.getElementById('source-date-sort');document.querySelector('.candidate-archive-filters').hidden=false;
  function filterArchive(){const cards=[...archive.querySelectorAll('[data-source-id]')];cards.sort((a,b)=>{const x=a.dataset.sourceDate,y=b.dataset.sourceDate;if(!x)return y?1:0;if(!y)return -1;return sort.value==='oldest'?x.localeCompare(y):y.localeCompare(x);});for(const card of cards){card.hidden=Boolean(typeFilter.value&&card.dataset.sourceType!==typeFilter.value);archive.append(card);}}
  typeFilter.addEventListener('change',filterArchive);sort.addEventListener('change',filterArchive);filterArchive();
  const share=document.getElementById('candidate-share');share.hidden=false;share.addEventListener('click',()=>copyLink(shareStatus));
  const openWeb=document.getElementById('candidate-open-web');if(openWeb)openWeb.hidden=false;
  try{const saved=JSON.parse(sessionStorage.getItem('candidate-directory-return'));if(saved){const url=new URL(saved.path,location.origin),expected=(lang==='en'?'/en/':'/')+'candidates/';if(url.origin===location.origin&&url.pathname.startsWith(expected))document.getElementById('candidate-back').href=url.pathname+url.search;}}catch(_){}
  function restoreHash(){
    if(location.hash.startsWith('#source=')){
      const params=new URLSearchParams(location.hash.slice(1)),id=params.get('source'),source=data.sources.find(item=>item.id===id);
      if(source){close();category=source.categories.includes(params.get('topic'))?params.get('topic'):source.categories[0];const index=list().findIndex(item=>item.id===id);page=Math.floor(index/size);draw();activate(index%size);}
      else{close();category=null;page=0;draw();breadcrumb.textContent=c.link_unavailable;}
    }else if(location.hash.startsWith('#topic=')){
      const key=new URLSearchParams(location.hash.slice(1)).get('topic');
      if(data.categories.some(topic=>topic.key===key)&&count(key))expand(key,{writeHash:false,openSingle:false});
    }else if(location.hash==='#information-web'){close();category=null;page=0;draw();}
  }
  window.addEventListener('hashchange',restoreHash);restoreHash();
  if(location.hash==='#information-web'||location.hash.startsWith('#source=')||location.hash.startsWith('#topic='))requestAnimationFrame(()=>section.scrollIntoView({block:'start',behavior:'instant'}));
})();
