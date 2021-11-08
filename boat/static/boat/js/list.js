$(document).ready(() => {
    $("a[data-boat-id]").on('click', function (e) {
        e.preventDefault();
        console.log($(this).attr('data-boat-id'));
    })
})