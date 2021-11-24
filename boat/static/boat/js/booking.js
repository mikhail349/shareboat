$(document).ready(() => {
    $('#bookingdaterangepicker').daterangepicker({
        drops: 'up',
        autoUpdateInput: false,
        minDate: new Date(Math.max.apply(null,[firstPriceDate, new Date()])),
        maxDate: lastPriceDate,
        isInvalidDate: function(date) {
            for (let priceRange of priceRanges) {
                if (date._d >= priceRange.startDate && date._d <= priceRange.endDate) {
                    return false;
                }
            }
            return true;
        },
        /*isCustomDate: function(date) {
            const d = new Date(2021, 10, 30);
            if (date._d.getTime() == d.getTime()) {
                return 'booked';
            }            
        },*/
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
    $('#bookingdaterangepicker').on('apply.daterangepicker', function(e, picker) {
        var range = picker.startDate.format(picker.locale.format) + ' - ' + picker.endDate.format(picker.locale.format);

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
            <h5>Идет расчет цены за период ${range}...</h5>
        `);
       
        function onSuccess(data) {
            $('#bookingdaterangepicker').val(range);
            
            $('#priceAlert').removeClass('alert-danger');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-success');
            let sumStr = data.sum.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' });
            let daysStr = plural(data.days, 'день', 'дня', 'дней');
            $('#priceAlert').html(`
                <h4>${sumStr}</h4>
                <div>за ${data.days} ${daysStr}</div>
            `)
        }
    
        function onError(error) {
            if (error.status == 0) return;
            $('#bookingdaterangepicker').val('');
            
            $('#priceAlert').removeClass('alert-success');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-danger');
            $('#priceAlert').html(`
                <h5>${parseJSONError(error.responseJSON)}</h5>
            `);
        }
    });
})