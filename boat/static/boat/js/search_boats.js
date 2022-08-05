$(document).ready(() => {

    $(".pagination a").on('click', function(e) {

        const pageParams = new Proxy(new URLSearchParams($(this).attr('href')), {
            get: (searchParams, prop) => searchParams.get(prop),
        });
        
        $('#formFilter input[name="page"]').val(pageParams.page);
        $("#formFilter").submit();

        e.preventDefault();
    })

    $("#btnNotFoundClearFilter").on('click', function(e) {
        clearFilter();
    })
});