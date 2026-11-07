(function(){
  'use strict';
  const {copy:c,lang,loadPortraits}=window.AyitiCandidates;
  const main=document.querySelector('[data-directory-office]'),form=document.getElementById('candidate-search'),results=document.getElementById('candidate-results'),count=document.getElementById('candidate-count'),pagination=document.getElementById('candidate-pagination'),error=document.getElementById('candidate-load-error');
  if(!main)return;
  const base=(lang==='en'?'/en/':'/')+'candidates/',size=24;
  const normalize=value=>String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  const element=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el;};
  const catalogs=new Map();let rows=null,sequence=0,timer;
  let state={office:main.dataset.directoryOffice,page:Number(main.dataset.directoryPage),q:'',department:'',place:'',party:'',status:''};
  for(const key of Object.keys(state)){const value=new URLSearchParams(location.search).get(key);if(value!==null)state[key]=key==='page'?Math.max(1,Number(value)||1):value;}
  for(const key of ['q','department','place','party','status'])form.elements.namedItem(key).value=state[key];
  form.hidden=false;
  const filterToggle=document.getElementById('candidate-filter-toggle'),filterPanel=document.getElementById('candidate-filters');
  function expandFilters(open){filterPanel.hidden=!open;filterToggle.setAttribute('aria-expanded',String(open));filterToggle.textContent=(open?c.fewer_filters:c.more_filters)+(open?' −':' +');}
  filterToggle.addEventListener('click',()=>expandFilters(filterPanel.hidden));
  if(state.department||state.place||state.party||state.status)expandFilters(true);
  function catalog(){
    const office=state.office;
    if(!catalogs.has(office))catalogs.set(office,fetch('/data/candidate-public/catalog'+(office==='all'?'':'-'+office)+'.json').then(response=>{if(!response.ok)throw Error('Directory unavailable');return response.json();}).then(data=>data.candidates.map(row=>({...row,search:normalize([row.name,row.party,...row.locality].join(' '))}))).catch(e=>{catalogs.delete(office);throw e;}));
    return catalogs.get(office);
  }
  function fill(select,values,first){
    const current=state[select.name],fragment=document.createDocumentFragment();fragment.append(new Option(first,''));
    for(const value of [...new Set(values)].filter(Boolean).sort((a,b)=>a.localeCompare(b)))fragment.append(new Option(value,value));
    select.replaceChildren(fragment);select.value=current;
    if(select.value!==current){state[select.name]='';select.value='';}
  }
  function populateFilters(){
    if(!rows)return;
    const relevant=rows.filter(row=>state.office==='all'||row.office===state.office);
    const departments=form.elements.department,places=form.elements.place;
    fill(departments,relevant.filter(row=>row.office!=='president').map(row=>row.locality[0]),c.all_departments);
    fill(places,relevant.filter(row=>!state.department||row.locality[0]===state.department).map(row=>row.locality.slice(1).join(' · ')),c.all_communes);
    fill(form.elements.party,relevant.map(row=>row.party),c.all_parties);
    departments.disabled=state.office==='president';places.disabled=state.office==='president'||!relevant.some(row=>row.locality.length>1);
  }
  function card(row){
    const article=element('article','candidate-card'),link=element('a','candidate-card-link');link.href=base+row.id+'/#information-web';link.setAttribute('aria-label',row.name+' — '+c.view_web);
    const photo=element('div','candidate-photo');
    if(row.portrait){const image=element('img');image.dataset.portraitSrc=row.portrait.path;image.dataset.portraitSrcset=row.portrait.variants.map(v=>v.path+' '+v.width+'w').join(', ');image.dataset.portraitSizes=row.portrait.sizes;image.alt=row.name;image.width=320;image.height=400;image.decoding='async';image.style.objectPosition=row.portrait.position;photo.append(image);}
    else{const initials=element('span','candidate-initials',row.initials);initials.setAttribute('aria-hidden','true');photo.append(initials,element('span','photo-pending',c.photo_pending));}
    const arrow=element('span','photo-open','↗');arrow.setAttribute('aria-hidden','true');photo.append(arrow);
    const info=element('div','candidate-card-info');info.append(element('p','candidate-card-office',c[row.office]+' · '+row.party),element('h2','',row.name),element('p','candidate-card-place',row.locality.join(' · ')),element('span','candidate-status',c[row.status]));
    const action=element('span','candidate-card-cta',c.view_web);action.append(element('span','','↗'));info.append(action);link.append(photo);if(row.portrait)link.append(element('p','candidate-card-photo-credit',c.photo_credit+': '+row.portrait.credit));link.append(info);article.append(link);return article;
  }
  function updateUrl(){
    const query=new URLSearchParams();for(const[key,value]of Object.entries(state))if(value!==''&&(key!=='page'||value!==1))query.set(key,String(value));
    history.replaceState(null,'',base+'?'+query.toString());
  }
  function updateTabs(){for(const tab of document.querySelectorAll('[data-office]')){const active=tab.dataset.office===state.office;tab.classList.toggle('active',active);if(active)tab.setAttribute('aria-current','page');else tab.removeAttribute('aria-current');}}
  async function render(writeUrl=true){
    const request=++sequence;error.hidden=true;results.setAttribute('aria-busy','true');count.textContent=c.loading;
    try{
      const all=await catalog();if(request!==sequence)return;rows=all;populateFilters();
      const words=normalize(state.q).split(' ').filter(Boolean);
      const matches=all.filter(row=>(state.office==='all'||row.office===state.office)&&(!state.department||row.locality[0]===state.department)&&(!state.place||row.locality.slice(1).join(' · ')===state.place)&&(!state.party||row.party===state.party)&&(!state.status||row.status===state.status)&&words.every(word=>row.search.includes(word)));
      const pages=Math.max(1,Math.ceil(matches.length/size));state.page=Math.min(Math.max(1,state.page),pages);
      const fragment=document.createDocumentFragment();for(const row of matches.slice((state.page-1)*size,state.page*size))fragment.append(card(row));
      if(!matches.length)fragment.append(element('p','candidate-archive-empty',c.no_results));
      results.replaceChildren(fragment);loadPortraits();count.textContent=new Intl.NumberFormat(lang==='en'?'en-US':'fr-HT').format(matches.length)+' '+c.results;
      pagination.replaceChildren();const nav=element('nav','candidate-pagination');nav.setAttribute('aria-label',c.page);
      for(const direction of [-1,0,1]){
        if(direction===0){nav.append(element('span','',c.page+' '+state.page+' '+c.of+' '+pages));continue;}
        const button=element('button','candidate-button secondary',direction===-1?c.previous:c.next);button.type='button';button.disabled=direction===-1?state.page<=1:state.page>=pages;
        button.addEventListener('click',()=>{state.page+=direction;render();document.querySelector('.candidate-results-bar').scrollIntoView({block:'start',behavior:'auto'});});nav.append(button);
      }
      pagination.append(nav);updateTabs();if(writeUrl)updateUrl();
    }catch(_){if(request===sequence){error.hidden=false;count.textContent=c.load_error;}}
    finally{if(request===sequence)results.removeAttribute('aria-busy');}
  }
  function readForm(){for(const key of ['q','department','place','party','status'])state[key]=form.elements.namedItem(key).value;state.page=1;}
  form.addEventListener('submit',event=>{event.preventDefault();clearTimeout(timer);readForm();render();});
  form.elements.q.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{readForm();render();},200);});
  form.addEventListener('change',event=>{if(event.target.tagName!=='SELECT')return;if(event.target===form.elements.department){form.elements.place.value='';state.place='';}readForm();populateFilters();render();});
  form.addEventListener('reset',event=>{event.preventDefault();clearTimeout(timer);state={office:'all',page:1,q:'',department:'',place:'',party:'',status:''};for(const key of ['q','department','place','party','status'])form.elements.namedItem(key).value='';populateFilters();render();});
  form.addEventListener('focusin',()=>{const office=state.office;catalog().then(all=>{if(office===state.office){rows=all;populateFilters();}}).catch(()=>{error.hidden=false;});},{once:true});
  for(const tab of document.querySelectorAll('[data-office]'))tab.addEventListener('click',event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();clearTimeout(timer);readForm();state.office=tab.dataset.office;rows=null;state.department='';state.place='';state.party='';render();});
  document.getElementById('candidate-retry').addEventListener('click',()=>render());
  results.addEventListener('click',event=>{if(event.target.closest('.candidate-card-link'))try{sessionStorage.setItem('candidate-directory-return',JSON.stringify({path:location.pathname+location.search,scroll:scrollY}));}catch(_){}});
  if(location.search){render(false).then(()=>{try{const saved=JSON.parse(sessionStorage.getItem('candidate-directory-return'));if(saved&&saved.path===location.pathname+location.search)scrollTo(0,saved.scroll||0);}catch(_){}});}
  else updateTabs();
})();
