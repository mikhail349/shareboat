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

    $('#bookingdaterangepicker').on('apply.daterangepicker', function(e, picker) {   
        $.ajax({ 
            type: "GET",
            url: `/boats/api/calc_booking/${boatId}/?start_date=${picker.startDate.format('YYYY-MM-DD')}&end_date=${picker.endDate.format('YYYY-MM-DD')}`,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            $('#bookingdaterangepicker').val(picker.startDate.format(picker.locale.format) + ' - ' + picker.endDate.format(picker.locale.format));
            
            $('#priceAlert').removeClass('alert-danger');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-success');
            let sumStr = data.sum.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' });
            let daysStr = plural(data.days, 'день', 'дня', 'дней');
            $('#priceAlert').text(`${sumStr} за ${data.days} ${daysStr}`);
        }
    
        function onError(error) {
            $('#bookingdaterangepicker').val('');
            
            $('#priceAlert').removeClass('alert-success');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-danger');
            $('#priceAlert').text(parseJSONError(error.responseJSON));
        }
    });
})