$(document).ready(() => {
    $(".card-img-small").on('click', function(e) {
        const src = $(this).attr('src');
        $('.card-img-main').attr('src', src);

        $(".card-img-small").removeClass('active');
        $(this).addClass('active');
    });
})