var lastScrollTop = 0;

/*$(document).ready(() => {
     $('.navbar-nav a.active').removeClass('active bg-light text-dark');
     $('.navbar-nav a[href="' + location.pathname + '"').addClass("active bg-light text-dark");
})*/

window.addEventListener("scroll", () => {
   var st = window.pageYOffset || document.documentElement.scrollTop;
   if (st > lastScrollTop && st > 62){
        $('body > header > nav').css("top", "-80px")
   } else {
        $('body > header > nav').css("top", "0")
   }
   lastScrollTop = st <= 0 ? 0 : st;
}, false);