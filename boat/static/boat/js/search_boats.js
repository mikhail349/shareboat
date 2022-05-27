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
});