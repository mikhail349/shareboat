var lastScrollTop = 0;

window.addEventListener("scroll", () => {
   var st = window.pageYOffset || document.documentElement.scrollTop;
   if (st > lastScrollTop && st > 62){
        $('body > header > nav').css("top", "-80px")
   } else {
        $('body > header > nav').css("top", "0")
   }
   lastScrollTop = st <= 0 ? 0 : st;
}, false);