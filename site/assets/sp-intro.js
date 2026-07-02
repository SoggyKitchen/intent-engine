(function(){
  var b=document.body,title=b.getAttribute('data-intro-title');
  if(!title)return;
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var key='sp-pintro:'+location.pathname;
  try{if(sessionStorage.getItem(key))return;sessionStorage.setItem(key,'1');}catch(e){}
  var eyebrow=b.getAttribute('data-intro-eyebrow')||'SaaSpare';
  var ov=document.createElement('div');
  ov.className='sp-pintro';ov.setAttribute('aria-hidden','true');
  ov.innerHTML='<canvas class="ai-orb sp-pintro-orb" data-scale="0.5" data-density="1.1"></canvas>'+
    '<div class="sp-pintro-c"><div class="sp-pintro-eyebrow">'+eyebrow+'</div>'+
    '<div class="sp-pintro-title">'+title+'</div>'+
    '<div class="sp-pintro-bar"><i></i></div></div>';
  b.appendChild(ov);
  if(window.spPlexus)window.spPlexus(ov.querySelector('canvas'));
  var done=false;
  function dismiss(){if(done)return;done=true;ov.classList.add('done');setTimeout(function(){ov.remove();},800);}
  var timer=setTimeout(dismiss,1700);
  ov.addEventListener('click',function(){clearTimeout(timer);dismiss();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'||e.key===' '){clearTimeout(timer);dismiss();}},{once:true});
})();
