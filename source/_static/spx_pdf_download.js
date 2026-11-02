// SPX_PDF_DOWNLOAD_JS_V3
(function(){
  function spxAddPdfLink(){
    try{
      var p=String(window.location.pathname||'');
      if(p.indexOf('/preview/')===0){return;}
      var pdfUrl='/project_pdf';
      var m=p.match(/^\/docs\/([^\/]+)\//);
      if(m&&m[1]){pdfUrl='/docs/'+encodeURIComponent(m[1])+'/pdf';}
      if(document.getElementById('spx-pdf-download-link')||document.getElementById('spx-pdf-download-btn')){return;}
      var aside=document.querySelector('.wy-breadcrumbs-aside');
      if(aside){
        var link=document.createElement('a');
        link.id='spx-pdf-download-link';
        link.href=pdfUrl;
        link.rel='noopener';
        link.target='_blank';
        link.textContent='Download PDF';
        try{aside.appendChild(document.createTextNode(' | '));}catch(_e){}
        aside.appendChild(link);
        return;
      }
      var a=document.createElement('a');
      a.id='spx-pdf-download-btn';
      a.href=pdfUrl;
      a.rel='noopener';
      a.target='_blank';
      a.textContent='Download PDF';
      (document.body||document.documentElement).appendChild(a);
      try{
        var r=document.querySelector('.wy-nav-top, .navbar, header');
        if(r&&r.getBoundingClientRect){
          var rect=r.getBoundingClientRect();
          if(rect&&rect.bottom&&rect.bottom>0){a.style.top=(Math.round(rect.bottom)+12)+'px';}
        }
      }catch(_e){}
    }catch(e){}
  }
  try{
    if(document.readyState==='loading'){
      document.addEventListener('DOMContentLoaded', spxAddPdfLink);
    } else {
      spxAddPdfLink();
    }
  }catch(_e){}
})();
