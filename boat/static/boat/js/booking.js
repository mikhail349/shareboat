$(document).ready(() => {
    $('#bookingdaterangepicker').daterangepicker({
        format: 'DD.MM.YYYY',
        drops: 'up',
        autoUpdateInput: false,
        minDate: new Date(Math.max.apply(null,[firstPriceDate, new Date()])),
        maxDate: lastPriceDate,
        isInvalidDate: function(date) {

            for (let acceptedBookingRange of acceptedBookingsRanges) {
                if (date._d >= acceptedBookingRange.startDate && date._d <= acceptedBookingRange.endDate) {
                    return true;
                }
            }

            for (let priceRange of priceRanges) {
                if (date._d >= priceRange.startDate && date._d <= priceRange.endDate) {
                    return false;
                }
            }

            return true;
        },
        locale: {
            format: 'DD.MM.YYYY',
            applyLabel: "Ок",
            "cancelLabel": "Отмена",
            "fromLabel": "От",
            "toLabel": "До",
            "customRangeLabel": "Произвольный",
            "daysOfWeek": [
                "Вс",
                "Пн",
                "Вт",
                "Ср",
                "Чт",
                "Пт",
                "Сб"
            ],
            "monthNames": [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь"
            ],
            firstDay: 1
        }
    })
    
    var xhr = null;
    function calc_booking() {
        const picker = $('#bookingdaterangepicker').data('daterangepicker');
        
        var range = picker.startDate.format(picker.locale.format) + ' - ' + picker.endDate.format(picker.locale.format);
        window.selectedStartDate = picker.startDate;
        window.selectedEndDate = picker.endDate;
        window.totalSum = null;

        if (!!xhr) xhr.abort();
        xhr = $.ajax({ 
            type: "GET",
            url: `/boats/api/calc_booking/${boatId}/?start_date=${picker.startDate.format('YYYY-MM-DD')}&end_date=${picker.endDate.format('YYYY-MM-DD')}`,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        $('#priceAlert').removeClass('alert-danger');
        $('#priceAlert').removeClass('alert-success');
        $('#priceAlert').addClass('alert-secondary');
        $('#priceAlert').html(`
            <strong>Идет расчет цены...</strong>
        `);
       
        function onSuccess(data) {
            $('#bookingdaterangepicker').val(range);

            window.totalSum = data.sum;
            
            $('#priceAlert').removeClass('alert-danger');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-success');
            let sumStr = data.sum.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' });
            let daysStr = plural(data.days, 'день', 'дня', 'дней');
            $('#priceAlert').html(`
                <strong>${sumStr}</strong><span> за ${data.days} ${daysStr}</span>
            `)
        }
    
        function onError(error) {
            window.selectedStartDate = null;
            window.selectedEndDate = null;
            window.totalSum = null;

            if (error.status == 0) return;
            $('#bookingdaterangepicker').val('');
            
            $('#priceAlert').removeClass('alert-success');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-danger');
            $('#priceAlert').html(`
                <h5>${parseJSONError(error.responseJSON)}</h5>
            `);
        }        
    }

    var xhr = null;
    $('#bookingdaterangepicker').on('apply.daterangepicker', function(e) {
        calc_booking();
    });

    $("form").on('submit', function(e) {
        e.preventDefault();
        const $datePicker = $('#bookingdaterangepicker');
        $datePicker.removeAttr('readonly');

        if (!$(this).checkValidity(false)) return;
        
        showOverlayPanel("Бронирование...");
        const url = $(this).attr("action");
        const formData = new FormData();
        formData.append('start_date', window.selectedStartDate.format('YYYY-MM-DD'));
        formData.append('end_date', window.selectedEndDate.format('YYYY-MM-DD'));
        formData.append('total_sum', window.totalSum);
        formData.append('boat_id', window.boatId);

        $.ajax({ 
            type: "POST",
            url: url,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            $datePicker.attr('readonly', true);
            hideOverlayPanel();
            window.location.href = data.redirect;
        }
    
        function onError(error) {
            $datePicker.attr('readonly', true);
            hideOverlayPanel();
            showErrorToast(error.responseJSON.message);
            if (error.responseJSON?.code === 'outdated_price') {
                calc_booking();
            }
        }
    });
})