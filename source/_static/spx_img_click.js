document.addEventListener('DOMContentLoaded', function(){
  var sels = ['.rst-content img', '.bd-article-container img', '.bd-content img', '.md-content img'];
  var imgs = [];
  sels.forEach(function(s){ document.querySelectorAll(s).forEach(function(n){ imgs.push(n); }); });
  imgs = Array.from(new Set(imgs));
  imgs.forEach(function(img){
    if(!img) return;
    if(img.closest('a')) return; // don't override existing links
    var src = img.getAttribute('src');
    if(!src || src.indexOf('data:')===0) return;
    img.classList.add('spx-zoomable');
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', function(e){ try { window.open(src, '_blank', 'noopener'); } catch(err) {} });
  });
});
