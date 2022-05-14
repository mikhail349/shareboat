var lastScrollTop = 0,
     currentNavTop = 0,
     currentToastTop = 62;     

$(document).ready(() => {

     const $mainNav = $('body > header > nav');
     const $mainToast = $('#toastContainer');

     const mainNavHeight = 62;

     function mainMenuHide(){
          const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
          const diffScrollTop = scrollTop - lastScrollTop;
          currentNavTop += diffScrollTop;
          currentNavTop = currentNavTop > mainNavHeight ? mainNavHeight : currentNavTop < 0 ? 0 : currentNavTop;

          $mainNav.attr("style", `top: -${currentNavTop}px !important;`);
          $mainToast.attr("style", `top: ${-currentNavTop+mainNavHeight}px !important;`);
          
          lastScrollTop = scrollTop;
     }

     window.addEventListener("scroll", mainMenuHide, false);
});