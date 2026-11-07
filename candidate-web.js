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
  let complete=!data.source_catalog_url,pending=null,loadSequence=0,archivePage=0,filterTimer,filteredCache=null;
  const filters={year:'',query:'',relation:'',type:'',sort:'newest'},categoryCache=new Map();
  const normal=value=>String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
  const years=source=>{const dates=[source.published_at,source.event_date,source.event_year,source.native?source.reviewed_at:null].filter(Boolean).map(value=>value.slice(0,4));return dates.length?[...new Set(dates)]:['unknown'];};
  function invalidate(){filteredCache=null;categoryCache.clear();}
  function filtered(){
    if(!filteredCache){
      const words=normal(filters.query).split(/\s+/).filter(Boolean);
      filteredCache=data.sources.filter(source=>(!filters.year||years(source).includes(filters.year))&&(!filters.relation||source.relation===filters.relation)&&(!filters.type||source.type===filters.type)&&words.every(word=>normal(source.title[lang]+' '+source.publisher+' '+(source.editorial_level==='index'?'':source.summary[lang])).includes(word)));
      filteredCache.sort((a,b)=>{const x=a.published_at||a.event_date||a.event_year||(a.native?a.reviewed_at:'')||'',y=b.published_at||b.event_date||b.event_year||(b.native?b.reviewed_at:'')||'';if(!x)return y?1:0;if(!y)return -1;return filters.sort==='oldest'?x.localeCompare(y):y.localeCompare(x);});
    }return filteredCache;
  }
  const list=()=>{if(category===null)return data.categories;if(!categoryCache.has(category))categoryCache.set(category,filtered().filter(source=>source.categories.includes(category)));return categoryCache.get(category);};
  const visible=()=>list().slice(page*size,page*size+size);
  const count=key=>!complete?data.topic_counts[key]:filtered().filter(source=>source.categories.includes(key)).length;
  const format=source=>c['format_'+source.format]||c.format_article;
  function hash(value){history.replaceState(null,'',location.pathname+location.search+'#'+value);}
  const viewParams=()=>{const params=new URLSearchParams();if(filters.year)params.set('year',filters.year);if(filters.query)params.set('q',filters.query);if(filters.relation)params.set('relation',filters.relation);return params;};
  const topicAddress=key=>{const params=viewParams();return (key===null?'information-web':'topic='+encodeURIComponent(key))+(params.size?'&'+params:'');};
  const sourceAddress=item=>{const params=viewParams();return 'source='+encodeURIComponent(item.id)+'&topic='+encodeURIComponent(category)+(params.size?'&'+params:'');};
  async function ensureSources(){
    if(complete)return true;
    stage.setAttribute('aria-busy','true');hint.textContent=c.source_loading;
    try{
      if(!pending)pending=fetch(data.source_catalog_url).then(response=>{if(!response.ok)throw Error('Source catalogue unavailable');return response.json();}).then(result=>{if(result.id!==data.id||!Array.isArray(result.sources))throw Error('Wrong source catalogue');data.sources=result.sources;complete=true;invalidate();});
      await pending;return true;
    }catch(_){pending=null;hint.textContent=c.source_load_error;const retry=element('button','candidate-clear',c.retry);retry.type='button';retry.addEventListener('click',()=>applyFilters());hint.append(' ',retry);return false;}
    finally{stage.removeAttribute('aria-busy');}
  }
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
    if(updateHash)hash(topicAddress(category));
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
    type.textContent=c[item.type]+' · '+format(item)+(item.editorial_level==='index'?' · '+c.index_entry:'');title.textContent=item.title[lang];summary.textContent=item.summary[lang];publisher.textContent=c.source+': '+item.publisher;
    date.textContent=(item.published_at?c.published+': '+item.published_at:c.date_unknown)+' · '+(item.review_status==='indexed'?c.indexed:c.reviewed)+': '+item.reviewed_at;
    if(item.event_date||item.event_year)date.textContent+=' · '+c.event_date+': '+(item.event_date||item.event_year);
    const link=element('a','candidate-button',item.native?c.registry_title+' ↑':c.original+' ↗');link.href=item.native?'#registration':item.url;
    if(!item.native){link.target='_blank';link.rel='noopener noreferrer';}
    else link.addEventListener('click',()=>close());
    action.append(link);
    if(item.relation==='mention')action.append(element('p','source-relationship',c.mention_note));
    else if(['candidate_channel','archive_context'].includes(item.relation))action.append(element('p','source-relationship',c['relation_'+item.relation]));
    if(item.availability==='archived_page_only')action.append(element('p','source-access-note',c.video_archive_note));
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
  async function expand(key,{writeHash=true,openSingle=true}={}){
    const request=++loadSequence;if(!await ensureSources()||request!==loadSequence)return;
    close();category=key;page=0;archivePage=0;draw();if(writeHash)hash(topicAddress(key));
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
      if(category!==null)button.dataset.sourceId=item.id;
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
    renderArchive();
  }
  back.addEventListener('click',()=>{const previous=category;close();category=null;page=0;archivePage=0;draw();hash(topicAddress(null));focusNode(nodes.children[data.categories.findIndex(topic=>topic.key===previous)]);});
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
  const typeFilter=document.getElementById('source-type-filter'),sort=document.getElementById('source-date-sort');document.querySelector('.candidate-archive-filters').hidden=false;
  const controls=element('form','web-archive-controls'),searchLabel=element('label','',c.archive_search),search=element('input'),yearLabel=element('label','',c.archive_year),year=element('select');
  search.type='search';search.id='web-source-query';search.autocomplete='off';searchLabel.append(search);year.id='web-source-year';year.append(new Option(c.all_years,''));
  for(const value of (data.years||[]).filter(value=>value!=='unknown'))year.append(new Option(value,value));if(data.years?.includes('unknown'))year.append(new Option(c.unknown_year,'unknown'));yearLabel.append(year);
  const advanced=element('details','web-archive-more'),summaryControl=element('summary','',c.more_filters),relationLabel=element('label','',c.archive_relation),relation=element('select'),clear=element('button','candidate-clear',c.clear);relation.id='web-source-relation';
  for(const [value,text] of [['',c.all_references],['headline',c.relation_headline],['mention',c.relation_mention],['candidate_channel',c.relation_candidate_channel],['archive_context',c.relation_archive_context]])relation.append(new Option(text,value));
  relationLabel.append(relation);clear.type='reset';advanced.append(summaryControl,relationLabel,clear);controls.append(searchLabel,yearLabel,advanced);hint.before(controls);
  const resultStatus=element('p','web-filter-status');resultStatus.id='web-filter-status';resultStatus.setAttribute('role','status');controls.after(resultStatus);
  const fullArchiveLink=archive.querySelector('.candidate-coverage'),archivePager=element('nav','candidate-pagination');archivePager.id='source-archive-pagination';archivePager.setAttribute('aria-label',c.page);archive.after(archivePager);
  function renderArchive(){
    const rows=filtered(),total=complete?rows.length:(data.total_sources||rows.length),pages=Math.max(1,Math.ceil(total/24));archivePage=Math.min(archivePage,pages-1);const fragment=document.createDocumentFragment();
    for(const source of rows.slice(archivePage*24,archivePage*24+24)){
      const card=element('article','candidate-source-card');card.dataset.sourceId=source.id;card.dataset.sourceType=source.type;card.dataset.sourceDate=source.published_at||'';
      const meta=element('div');meta.append(element('span','source-type',c[source.type]+' · '+format(source)+(source.editorial_level==='index'?' · '+c.index_entry:'')),element('span','',source.published_at||c.date_unknown));
      card.append(meta,element('h3','',source.title[lang]),element('p','',source.summary[lang]),element('p','source-publisher',c.source+': '+source.publisher));
      if(source.relation==='mention')card.append(element('p','source-relationship',c.mention_note));
      if(source.access==='account')card.append(element('p','source-access-note',c.source_account_note));
      if(source.availability==='archived_page_only')card.append(element('p','source-access-note',c.video_archive_note));
      const original=element('a','',source.native?c.registry_title+' ↑':c.original+' ↗');original.href=source.native?'#registration':source.url;if(!source.native){original.target='_blank';original.rel='noopener noreferrer';}
      if(source.event_date||source.event_year)card.append(element('p','source-date',c.event_date+': '+(source.event_date||source.event_year)));
      if(['candidate_channel','archive_context'].includes(source.relation))card.append(element('p','source-relationship',c['relation_'+source.relation]));
      const preview=element('a','source-preview-link',c.view_web+' →');preview.href='#source='+encodeURIComponent(source.id)+'&topic='+encodeURIComponent(source.categories[0])+(filters.year?'&year='+encodeURIComponent(filters.year):'');
      card.append(original,preview);fragment.append(card);
    }
    if(!rows.length)fragment.append(element('p','candidate-archive-empty',c.source_no_results));if(fullArchiveLink)fragment.append(fullArchiveLink);archive.replaceChildren(fragment);archivePager.replaceChildren();
    if(pages>1){
      for(const delta of [-1,0,1]){
        if(!delta){archivePager.append(element('span','',c.page+' '+(archivePage+1)+' '+c.of+' '+pages));continue;}
        const button=element('button','candidate-button secondary',delta<0?c.previous:c.next);button.type='button';button.disabled=delta<0?archivePage===0:archivePage>=pages-1;button.id=delta<0?'source-archive-previous':'source-archive-next';
        button.addEventListener('click',async()=>{if(!await ensureSources())return;archivePage+=delta;renderArchive();document.getElementById('source-archive').scrollIntoView({block:'start',behavior:'instant'});});archivePager.append(button);
      }
    }
    resultStatus.textContent=(complete?rows.length:(data.total_sources||rows.length)).toLocaleString()+' '+c.sources+(filters.year?' · '+(filters.year==='unknown'?c.unknown_year:filters.year):'');
    if(complete&&!rows.length)hint.textContent=c.source_no_results;
  }
  async function applyFilters(){
    const request=++loadSequence;filters.year=year.value;filters.query=search.value.trim();filters.relation=relation.value;filters.type=typeFilter.value;filters.sort=sort.value;invalidate();
    if(!await ensureSources()||request!==loadSequence)return;close();page=0;archivePage=0;if(category!==null&&!count(category))category=null;draw();hash(topicAddress(category));
  }
  controls.addEventListener('submit',event=>{event.preventDefault();clearTimeout(filterTimer);applyFilters();});search.addEventListener('input',()=>{clearTimeout(filterTimer);filterTimer=setTimeout(applyFilters,200);});year.addEventListener('change',applyFilters);relation.addEventListener('change',applyFilters);
  controls.addEventListener('reset',event=>{event.preventDefault();search.value='';year.value='';relation.value='';typeFilter.value='';sort.value='newest';applyFilters();});
  typeFilter.addEventListener('change',applyFilters);sort.addEventListener('change',applyFilters);
  section.hidden=false;draw();
  new ResizeObserver(()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(draw);}).observe(stage);
  const share=document.getElementById('candidate-share');share.hidden=false;share.addEventListener('click',()=>copyLink(shareStatus));
  const openWeb=document.getElementById('candidate-open-web');if(openWeb)openWeb.hidden=false;
  try{const saved=JSON.parse(sessionStorage.getItem('candidate-directory-return'));if(saved){const url=new URL(saved.path,location.origin),expected=(lang==='en'?'/en/':'/')+'candidates/';if(url.origin===location.origin&&url.pathname.startsWith(expected))document.getElementById('candidate-back').href=url.pathname+url.search;}}catch(_){}
  async function restoreHash(){
    const params=new URLSearchParams(location.hash.slice(1));
    if(['source','topic','year','q','relation'].some(key=>params.has(key))){
      const request=++loadSequence;if(!await ensureSources()||request!==loadSequence)return;
      filters.year=data.years?.includes(params.get('year'))?params.get('year'):'';filters.query=params.get('q')||'';filters.relation=['headline','mention','candidate_channel','archive_context'].includes(params.get('relation'))?params.get('relation'):'';
      year.value=filters.year;search.value=filters.query;relation.value=filters.relation;invalidate();
    }
    if(location.hash.startsWith('#source=')){
      const id=params.get('source'),source=data.sources.find(item=>item.id===id);
      if(source&&!filtered().includes(source)){filters.query='';filters.relation='';filters.type='';filters.year='';search.value='';relation.value='';typeFilter.value='';year.value='';invalidate();}
      if(source){close();category=source.categories.includes(params.get('topic'))?params.get('topic'):source.categories[0];const index=list().findIndex(item=>item.id===id);page=Math.floor(index/size);draw();activate(index%size);section.scrollIntoView({block:'start',behavior:'instant'});}
      else{close();category=null;page=0;draw();breadcrumb.textContent=c.link_unavailable;}
    }else if(location.hash.startsWith('#topic=')){
      const key=params.get('topic');
      if(data.categories.some(topic=>topic.key===key)&&count(key))expand(key,{writeHash:false,openSingle:false});
    }else if(location.hash.startsWith('#information-web')){close();category=null;page=0;draw();}
  }
  window.addEventListener('hashchange',restoreHash);restoreHash();
  if(location.hash.startsWith('#information-web')||location.hash.startsWith('#source=')||location.hash.startsWith('#topic='))requestAnimationFrame(()=>section.scrollIntoView({block:'start',behavior:'instant'}));
})();
