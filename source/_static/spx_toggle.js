document.addEventListener('DOMContentLoaded', function(){
  var KEY='spx_sidebar_collapsed';
  function applyState(collapsed){ document.documentElement.classList.toggle('spx-sidebar-collapsed', !!collapsed); }
  function ensureBtn(){
    if(document.getElementById('spx-sidebar-toggle')) return;
    var b=document.createElement('button');
    b.id='spx-sidebar-toggle'; b.className='spx-sidebar-toggle'; b.type='button'; b.setAttribute('aria-label','Toggle sidebar');
    b.setAttribute('title','Toggle sidebar');
    b.innerHTML='<span aria-hidden="true">'+
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+
      '<line x1="3" y1="6" x2="21" y2="6"></line>'+
      '<line x1="3" y1="12" x2="21" y2="12"></line>'+
      '<line x1="3" y1="18" x2="21" y2="18"></line>'+
      '</svg></span>';
    b.addEventListener('click', function(){
      var newVal=!document.documentElement.classList.contains('spx-sidebar-collapsed');
      applyState(newVal);
      try{ localStorage.setItem(KEY, newVal ? '1' : '0'); }catch(e){}
    });
    document.body.appendChild(b);
  }
  try{ applyState(localStorage.getItem(KEY)==='1'); }catch(e){}
  ensureBtn();
});
