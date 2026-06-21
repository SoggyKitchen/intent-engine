function spPlexus(canvas){
  if(!canvas||canvas._spOrb)return;canvas._spOrb=1;
  var ctx=canvas.getContext('2d');
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cfg=canvas.dataset||{};
  var SCALE=parseFloat(cfg.scale)||0.42;
  var DENSITY=parseFloat(cfg.density)||1;
  var DPR=Math.min(window.devicePixelRatio||1,2),W,H;
  function resize(){var p=canvas.parentElement;var w=p.offsetWidth,h=p.offsetHeight;if(!w||!h)return;W=w;H=h;canvas.width=W*DPR;canvas.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0);}
  resize();window.addEventListener('resize',resize,{passive:true});
  if(window.ResizeObserver){var ro=new ResizeObserver(function(){resize();});ro.observe(canvas.parentElement);}
  window.addEventListener('load',resize,{passive:true});
  var N=Math.round((window.innerWidth<700?130:220)*DENSITY),GOLDEN=Math.PI*(3-Math.sqrt(5)),nodes=[];
  for(var i=0;i<N;i++){var y=1-(i/(N-1))*2,rad=Math.sqrt(Math.max(0,1-y*y)),th=i*GOLDEN;nodes.push({x:Math.cos(th)*rad,y:y,z:Math.sin(th)*rad,pulse:Math.random()*6.283});}
  var LINK=0.52,edges=[];
  for(var a=0;a<N;a++)for(var b=a+1;b<N;b++){var dx=nodes[a].x-nodes[b].x,dy=nodes[a].y-nodes[b].y,dz=nodes[a].z-nodes[b].z,d=Math.sqrt(dx*dx+dy*dy+dz*dz);if(d<LINK)edges.push([a,b,1-d/LINK]);}
  var rotY=0,rotX=-0.16,t=0,mx=0,my=0,smx=0,smy=0,start=performance.now(),proj=new Array(N);
  window.addEventListener('mousemove',function(e){var r=canvas.getBoundingClientRect();mx=(e.clientX-r.left)/r.width-0.5;my=(e.clientY-r.top)/r.height-0.5;},{passive:true});
  function frame(now){
    if(!W||!H)return;
    smx+=(mx-smx)*0.05;smy+=(my-smy)*0.05;
    var intro=Math.min(1,(now-start)/2000),ease=reduce?1:1-Math.pow(1-intro,4);
    ctx.clearRect(0,0,W,H);
    var cx=W*0.5,cy=H*0.5,R=Math.min(W,H)*SCALE*ease,op=0.4+0.6*ease;
    var spin=reduce?0:(1-ease)*3.2;
    var ay=rotY+smx*0.5+spin,ax=rotX+smy*0.35;
    var cY=Math.cos(ay),sY=Math.sin(ay),cX=Math.cos(ax),sX=Math.sin(ax);
    for(var i=0;i<N;i++){var n=nodes[i],x1=n.x*cY-n.z*sY,z1=n.x*sY+n.z*cY,y2=n.y*cX-z1*sX,z2=n.y*sX+z1*cX,persp=1/(2.1-z2);proj[i]={sx:cx+x1*R*persp*1.55,sy:cy+y2*R*persp*1.55,z:z2};}
    ctx.lineWidth=0.8;
    for(var e2=0;e2<edges.length;e2++){var p1=proj[edges[e2][0]],p2=proj[edges[e2][1]],depth=(p1.z+p2.z)*0.5,la=edges[e2][2]*0.55*((depth+1)*0.5)*op;if(la<0.02)continue;ctx.strokeStyle='rgba(255,90,120,'+la+')';ctx.beginPath();ctx.moveTo(p1.sx,p1.sy);ctx.lineTo(p2.sx,p2.sy);ctx.stroke();}
    for(var k=0;k<N;k++){var p=proj[k],dp=(p.z+1)*0.5,pr=0.82+0.18*Math.sin(t*1.5+nodes[k].pulse),rr=(1+dp*2.6)*pr,al=(0.3+dp*0.62)*op;ctx.beginPath();ctx.arc(p.sx,p.sy,rr,0,6.283);ctx.fillStyle=dp>0.55?'rgba(255,150,170,'+al+')':'rgba(255,255,255,'+al*0.8+')';ctx.fill();}
  }
  var raf=0;
  function loop(){frame(performance.now());if(reduce)return;rotY+=0.0013;t+=0.016;raf=requestAnimationFrame(loop);}
  loop();
  document.addEventListener('visibilitychange',function(){if(!document.hidden&&!reduce){cancelAnimationFrame(raf);raf=requestAnimationFrame(loop);}},{passive:true});
}
window.spPlexus=spPlexus;
(function(){var c=document.querySelectorAll('canvas.ai-orb,canvas#ai-orb');for(var i=0;i<c.length;i++)spPlexus(c[i]);})();
