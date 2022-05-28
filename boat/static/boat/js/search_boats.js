$(document).ready(() => {
    $('form').on('submit', function(e) {

        var isInvalid = false;
        for (let input of $("form input")) {
            if ($(input).is(':invalid')) {
                isInvalid = true;
                break;
            }
        }
        
        if (!isInvalid) {
            const $btnSubmit = $('form button[type=submit]');
            $btnSubmit.attr('disabled', true);
            $btnSubmit.text('Идет поиск...');
        }

    });

    $('#sortSelect').on('change', () => {
        $("form").submit();
    })

    $(".pagination a").on('click', function(e) {
        
        const params = new Proxy(new URLSearchParams($(this).attr('href')), {
            get: (searchParams, prop) => searchParams.get(prop),
        });

        $('form input[name="page"]').val(params.page);
        $("form").submit();

        e.preventDefault();
    })
});