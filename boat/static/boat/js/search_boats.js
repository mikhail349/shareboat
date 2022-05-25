$(document).ready(() => {
    $('form').on('submit', function(e) {
        const $btnSubmit = $('form button[type=submit]');
        $btnSubmit.attr('disabled', true);
        $btnSubmit.text('Идет поиск...');
    });
});