var lastScrollTop = 0;

/*$(document).ready(() => {
     $('.navbar-nav a.active').removeClass('active bg-light text-dark');
     $('.navbar-nav a[href="' + location.pathname + '"').addClass("active bg-light text-dark");
})*/

window.addEventListener("scroll", () => {
   var st = window.pageYOffset || document.documentElement.scrollTop;
   if (st > lastScrollTop && st > 62){
        $('body > header > nav').css("top", "-80px");
        $('.alert-container ').attr("style", "top: 0 !important;");
        $('.toast-container ').attr("style", "top: 58px !important;");
   } else {
        $('body > header > nav').css("top", "0");
        $('.alert-container ').attr("style", "top: 62px !important;");
        $('.toast-container ').attr("style", "top: 120px !important;");
   }
   lastScrollTop = st <= 0 ? 0 : st;
}, false);