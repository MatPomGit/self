/* Hover and keyboard-accessible project previews, with native modal detail panel. */
(function(){
  'use strict';
  const preview=document.createElement('div');
  preview.className='project-preview';
  preview.id='project-preview';
  preview.setAttribute('aria-label','Project preview');
  preview.hidden=true;
  document.body.append(preview);
  const dialog=document.createElement('dialog');
  dialog.className='project-detail-dialog';
  dialog.setAttribute('aria-label','Project details');
  document.body.append(dialog);
  let activeCard=null;
  let pending=null;
  let closePending=null;
  let selected=null;
  let locale='pl';
  const labels={
    pl:{more:'Więcej szczegółów',close:'Zamknij',scope:'Cel i zakres',methods:'Metody i technologie',outcomes:'Rezultaty i produkty',status:'Status',ongoing:'Projekt w realizacji',past:'Projekt zakończony lub archiwalny',preview:'Podgląd projektu',detail:'Szczegóły projektu'},
    en:{more:'More details',close:'Close',scope:'Objectives and scope',methods:'Methods and technologies',outcomes:'Outputs and deliverables',status:'Status',ongoing:'Ongoing project',past:'Completed or archived project',preview:'Project preview',detail:'Project details'}
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
  function mark(project){
    const title=project.sourceTitle||project.title;
    const letters=title.split(/[\s·–/\-]+/u).filter(Boolean).slice(0,2).map(word=>word[0]).join('').toUpperCase();
    return el('span','project-mark',letters||'◇');
  }
  function head(project,headingTag){
    const wrap=el('div','project-preview-head');
    const info=el('div','project-preview-info');
    info.append(el(headingTag,'',clean(project.title)),el('div','project-preview-period',project.period));
    wrap.append(mark(project),info);
    return wrap;
  }
  function chips(methods){
    const container=el('div','project-chip-list');
    methods.slice(0,5).forEach(method=>container.append(el('span','project-chip',method)));
    return container;
  }
  function cancelPending(){
    window.clearTimeout(pending);
    window.clearTimeout(closePending);
    pending=null;
    closePending=null;
  }
  function hide(){
    cancelPending();
    preview.classList.remove('is-visible');
    preview.hidden=true;
    activeCard=null;
    selected=null;
  }
  function position(card){
    const rect=card.getBoundingClientRect();
    const width=preview.offsetWidth;
    const height=preview.offsetHeight;
    const right=window.innerWidth-rect.right;
    const left=right>=width+12?rect.right+10:rect.left-width-10;
    const x=Math.max(12,Math.min(left,window.innerWidth-width-12));
    const y=Math.max(12,Math.min(rect.top,window.innerHeight-height-12));
    preview.style.left=x+'px';
    preview.style.top=y+'px';
  }
  function show(card,project,language){
    if(dialog.open)return;
    cancelPending();
    locale=language;
    const t=labels[locale];
    activeCard=card;
    selected=project;
    preview.setAttribute('aria-label',t.preview);
    preview.replaceChildren(head(project,'h3'));
    preview.append(el('p','project-preview-summary',clean(project.description)));
    const extra=detailsFor(project);
    if(extra.methods.length)preview.append(chips(extra.methods));
    const button=el('button','project-preview-more',t.more+' ↗');
    button.type='button';
    button.addEventListener('click',()=>openDialog(project,language));
    preview.append(button);
    preview.hidden=false;
    position(card);
    preview.classList.add('is-visible');
  }
  function postponeClose(){
    window.clearTimeout(closePending);
    closePending=window.setTimeout(hide,180);
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
    hide();
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
    if(extra.focus)section(body,t.scope,extra.focus);
    dialog.replaceChildren(body);
    if(!dialog.open)dialog.showModal();
    close.focus();
  }
  preview.addEventListener('pointerenter',()=>window.clearTimeout(closePending));
  preview.addEventListener('pointerleave',postponeClose);
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!dialog.open)hide();});
  document.addEventListener('pointerdown',event=>{
    if(!dialog.open&&!preview.contains(event.target)&&!(activeCard&&activeCard.contains(event.target)))hide();
  });
  window.addEventListener('scroll',()=>{if(activeCard)position(activeCard);},{passive:true});
  window.addEventListener('resize',hide);
  function attach(card,project,language){
    const t=labels[language];
    const button=el('button','project-card-action',t.more);
    button.type='button';
    button.setAttribute('aria-label',t.detail+': '+project.title);
    button.addEventListener('click',event=>{event.stopPropagation();openDialog(project,language);});
    card.append(button);
    card.addEventListener('click',event=>{if(event.target.closest('button,a'))return;openDialog(project,language);});
    card.addEventListener('pointerenter',event=>{
      if(event.pointerType!=='mouse'&&event.pointerType!=='pen')return;
      cancelPending();
      pending=window.setTimeout(()=>show(card,project,language),250);
    });
    card.addEventListener('pointerleave',()=>{
      window.clearTimeout(pending);
      if(activeCard===card)postponeClose();
    });
    card.addEventListener('focusin',()=>{if(!dialog.open)show(card,project,language);});
    card.addEventListener('focusout',event=>{
      if(!card.contains(event.relatedTarget)&&!preview.contains(event.relatedTarget))postponeClose();
    });
  }
  window.ProjectPreview=Object.freeze({attach});
})();
