$(document).ready(() => {
    $(".card-img-small").on('click', function(e) {
        const src = $(this).attr('src');
        $('.card-img-lg-big').attr('src', src);

        $(".card-img-small").removeClass('active');
        $(this).addClass('active');
    });
})