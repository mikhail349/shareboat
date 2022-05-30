$(document).ready(() => {

    const params = new URLSearchParams(window.location.search);

    var dateFrom,
        dateTo;

    if (params.has('dateFrom')) {
        dateFrom = new Date(params.get('dateFrom'));
    }
    
    if (params.has('dateTo')) {
        dateTo = new Date(params.get('dateTo'));
    }

    const defaultDatePickerOptions = {
        autoClose: true,
        minDate: new Date(),
        altFieldDateFormat: 'yyyy-MM-dd',
        isMobile: window.isMobile()
    }

    new AirDatepicker('#dateFrom', {
        selectedDates: [dateFrom],
        altField: '#hiddenDateFrom',
        ...defaultDatePickerOptions
    });

    new AirDatepicker('#dateTo', {
        selectedDates: [dateTo],
        altField: '#hiddenDateTo',
        ...defaultDatePickerOptions
    });

    $('#formSearch').on('submit', function(e) {

        var isInvalid = false;
        for (let input of $("#formSearch input")) {
            if ($(input).is(':invalid')) {
                isInvalid = true;
                break;
            }
        }
        
        if (!isInvalid) {
            const $btnSubmit = $('#formSearch button[type=submit]');
            $btnSubmit.attr('disabled', true);
            $btnSubmit.text('Идет поиск...');
        }

    });

    $(".form-book-boat").on('submit', function(e) {
        e.preventDefault();
        const btn = $(this).find('button[type="submit"]');

        btn.attr('disabled', true);
        $.ajax({ 
            type: "POST",
            url: $(this).attr('action'),
            data: new FormData($(this)[0]),
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            window.location.href = data.redirect;
        }

        function onError(error) {
            showErrorToast(error.responseJSON.message);
            btn.attr('disabled', false);
        }
    })

    $('#sortSelect').on('change', () => {
        $("#formSearch").submit();
    })

    $(".pagination a").on('click', function(e) {

        const pageParams = new Proxy(new URLSearchParams($(this).attr('href')), {
            get: (searchParams, prop) => searchParams.get(prop),
        });
        
        $('#formSearch input[name="page"]').val(pageParams.page);
        $("#formSearch").submit();

        e.preventDefault();
    })
});