/* Click and keyboard-activated project detail panel. */
(function(){
  'use strict';
  const dialog=document.createElement('dialog');
  dialog.className='project-detail-dialog';
  dialog.setAttribute('aria-label','Project details');
  document.body.append(dialog);
  let returnFocus=null;
  let locale='pl';
  const labels={
    pl:{close:'Zamknij',scope:'Cel i zakres',links:'Odnośniki',focus:'Kierunek badań',methods:'Metody i technologie',outcomes:'Rezultaty i produkty',status:'Status',ongoing:'Projekt w realizacji',past:'Projekt zakończony lub archiwalny',detail:'Szczegóły projektu'},
    en:{close:'Close',scope:'Objectives and scope',links:'Links',focus:'Research focus',methods:'Methods and technologies',outcomes:'Outputs and deliverables',status:'Status',ongoing:'Ongoing project',past:'Completed or archived project',detail:'Project details'}
  };
  const el=(tag,cls,txt)=>{
    const node=document.createElement(tag);
    if(cls)node.className=cls;
    if(txt!==undefined)node.textContent=txt;
    return node;
  };
  const clean=(text)=>String(text||'').replace(/(?<!\p{L})([aiouwzAIUOWZ])[ \t]+(?=\S)/gu,'$1\u00a0');
  function detailsFor(project){
    const d=project.details && project.details[locale] || {};
    return {methods:Array.isArray(d.methods)?d.methods:[],outcomes:Array.isArray(d.outcomes)?d.outcomes:[],focus:typeof d.focus==='string'?d.focus:''};
  }
  // The logo path is repository-local and validated again by Python in CI.
  // Never allow external, data:, or traversal URLs from editable JSON content.
  function projectLogoPath(value){
    if(typeof value!=='string' || !/^docs\/assets\/images\/projects\/[a-z0-9][a-z0-9_-]*\.(?:svg|png|webp)$/u.test(value))return null;
    return value;
  }
  function mark(project){
    const title=project.sourceTitle||project.title;
    const letters=title.split(/[\s·–/\-]+/u).filter(Boolean).slice(0,2).map(word=>word[0]).join('').toUpperCase();
    const wrapper=el('span','project-mark');
    const fallback=el('span','project-mark-fallback',letters||'◇');
    wrapper.append(fallback);
    const logo=projectLogoPath(project.details&&project.details.logo);
    if(logo){
      const image=el('img','project-logo');
      image.alt='';
      image.decoding='async';
      image.loading='lazy';
      image.addEventListener('load',()=>{fallback.hidden=true;});
      image.addEventListener('error',()=>{image.remove();fallback.hidden=false;});
      image.src=logo;
      wrapper.append(image);
    }
    return wrapper;
  }
  function head(project,headingTag){
    const wrap=el('div','project-preview-head');
    const info=el('div','project-preview-info');
    info.append(el(headingTag,'',clean(project.title)),el('div','project-preview-period',project.period));
    wrap.append(mark(project),info);
    return wrap;
  }
  function safeProjectLink(value){
    if(typeof value!=='string')return null;
    try{
      const url=new URL(value);
      return url.protocol==='https:'&&url.username===''&&url.password==='' ? url.href : null;
    }catch(error){return null;}
  }
  function section(content,title,values){
    if(!values || (Array.isArray(values)&&!values.length))return;
    const wrap=el('section','project-detail-section');
    wrap.append(el('h3','',title));
    if(Array.isArray(values)){
      const list=el('ul','');
      values.forEach(value=>list.append(el('li','',clean(value))));
      wrap.append(list);
    }else wrap.append(el('p','',clean(values)));
    content.append(wrap);
  }
  function openDialog(project,language){
    locale=language;
    const t=labels[locale];
    dialog.setAttribute('aria-label',t.detail+': '+project.title);
    const body=el('div','project-detail-body');
    const toolbar=el('div','project-detail-top');
    const close=el('button','project-detail-close','×');
    close.type='button';
    close.setAttribute('aria-label',t.close);
    close.addEventListener('click',()=>dialog.close());
    toolbar.append(close);
    body.append(toolbar,head(project,'h2'));
    section(body,t.status,project.phase==='current'?t.ongoing:t.past);
    section(body,t.scope,project.description);
    const extra=detailsFor(project);
    section(body,t.methods,extra.methods);
    section(body,t.outcomes,extra.outcomes);
    if(extra.focus)section(body,t.focus,extra.focus);
    const links=project.details&&project.details.links;
    if(Array.isArray(links)&&links.length){
      const sectionLinks=el('section','project-detail-section');
      sectionLinks.append(el('h3','',t.links));
      const list=el('ul','project-detail-links');
      links.forEach(link=>{
        const href=safeProjectLink(link&&link.url);
        if(!href || !link.label || typeof link.label!=='string')return;
        const item=el('li','');
        const a=el('a','',link.label);
        a.href=href;
        a.target='_blank';
        a.rel='noopener noreferrer';
        item.append(a);
        list.append(item);
      });
      if(list.children.length){sectionLinks.append(list);body.append(sectionLinks);}
    }
    dialog.replaceChildren(body);
    if(!dialog.open)dialog.showModal();
    close.focus();
  }
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  dialog.addEventListener('close',()=>{
    if(returnFocus&&returnFocus.isConnected)returnFocus.focus({preventScroll:true});
    returnFocus=null;
  });
  function attach(card,project,language){
    card.tabIndex=0;
    card.setAttribute('role','button');
    card.setAttribute('aria-haspopup','dialog');
    card.setAttribute('aria-label',(language==='en'?'Project details: ':'Szczegóły projektu: ')+project.title);
    const open=()=>{
      if(dialog.open)return;
      returnFocus=card;
      openDialog(project,language);
    };
    card.addEventListener('click',event=>{
      if(event.target.closest('a,button'))return;
      open();
    });
    card.addEventListener('keydown',event=>{
      if(event.target!==card)return;
      if(event.key==='Enter'||event.key===' '){
        event.preventDefault();
        open();
      }
    });
  }
  window.ProjectPreview=Object.freeze({attach});
})();
