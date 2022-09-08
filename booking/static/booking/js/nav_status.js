$(document).ready(() => {
    function convertRemToPixels(rem) {
        var value;
        if (typeof rem === 'string') {
            value = parseFloat(rem.replace('rem', ''));
        } else {
            value = rem;
        }
        return value * parseFloat(getComputedStyle(document.documentElement).fontSize);
    }

    const $el = $('.nav-status .nav-item .nav-link.active');

    const halfWindow = $(window).width() / 2;
    const halfEl = $el.width() / 2;
    const linkPadding = convertRemToPixels(getComputedStyle($el[0]).getPropertyValue('--bs-nav-link-padding-x'));

    $('.nav-status').animate({scrollLeft: $el.position().left - halfWindow + halfEl + linkPadding}, 250);
})