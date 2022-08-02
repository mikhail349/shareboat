$(document).ready(() => {

    const searchParams = new URLSearchParams(window.location.search);
    const inputDatesExist = searchParams.has('dateFrom') && searchParams.has('dateTo');

    const dateRange = new AirDatepicker('#dateRange', {
        selectedDates: [
            inputDatesExist ? new Date(searchParams.get('dateFrom')) : undefined,
            inputDatesExist ? new Date(searchParams.get('dateTo')) : undefined
        ],
        autoClose: true,
        isMobile: window.isMobile(),
        range: true,
        minDate: new Date(Math.max.apply(null,[firstPriceDate, new Date()])),
        maxDate: lastPriceDate,
        multipleDatesSeparator: ' - ',
        position: 'bottom left',
        onHide: (isFinished) => {if (isFinished) calc_booking()},
        onRenderCell: ({date}) => {
            for (let acceptedBookingRange of acceptedBookingsRanges) {
                if (date >= acceptedBookingRange.startDate && date <= acceptedBookingRange.endDate) {
                    return {
                        disabled: true
                    };
                }
            }

            for (let priceRange of priceRanges) {
                if (date >= priceRange.startDate && date <= priceRange.endDate) {
                    return {
                        disabled: false
                    };
                }
            }

            return {
                disabled: true
            };
        }
    });

    if (inputDatesExist) {
        calc_booking();
    }
    
    var xhr = null;
    function calc_booking() {
        
        if (dateRange.selectedDates.length !== 2) {
            window.selectedStartDate = null;
            window.selectedEndDate = null;
            window.calculatedData = null;

            $('#priceAlert').html('<span>Выберите период</span>');
        }

        window.selectedStartDate = dateRange.selectedDates[0];
        window.selectedEndDate = dateRange.selectedDates[1];
        window.calculatedData = null;

        if (!!xhr) xhr.abort();
        xhr = $.ajax({ 
            type: "GET",
            url: `/boats/api/calc_booking/${boatId}/?start_date=${toJSONLocal(dateRange.selectedDates[0])}&end_date=${toJSONLocal(dateRange.selectedDates[1])}`,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        $('#priceAlert').html('<span>Идет расчет цены...</span>');
       
        function onSuccess(data) {
            if (!data?.sum) {
                $('#priceAlert').html('<span>Подходящий тариф не найден</span>');
                window.calculatedData = null;
                return;
            }
            parsedFloat = parseFloat(data.sum);
            let sumStr = parsedFloat.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' });
            let daysStr = plural(data.days, 'день', 'дня', 'дней');

            window.calculatedData = data;
            console.log(data);

            $('#priceAlert').html(`<strong class="text-success">${sumStr}</strong><span> за ${data.days} ${daysStr}</span>`)
        }
    
        function onError(error) {
            window.selectedStartDate = null;
            window.selectedEndDate = null;
            window.calculatedData = null;

            if (error.status == 0) return;
            
            $('#priceAlert').html(`<h5>${parseJSONError(error.responseJSON)}</h5>`);
        }   
    }

    var xhr = null;

    $("form").on('submit', function(e) {
        

        //if (!$(this).checkValidity(false)) return;

        if (!window.selectedStartDate || !window.selectedEndDate) {
            showErrorToast('Выберите период');
            e.preventDefault();
            return;
        }

        if (!window.calculatedData) {
            showErrorToast('Выберите другой период');
            e.preventDefault();
            return;            
        }

        $("form input[name='start_date']").val(toJSONLocal(window.selectedStartDate));
        $("form input[name='end_date']").val(toJSONLocal(window.selectedEndDate));
        $("form input[name='calculated_data']").val(JSON.stringify(window.calculatedData));

        /*
        
        showOverlayPanel("Бронирование...");
        const url = $(this).attr("action");
        const formData = new FormData();
        formData.append('start_date', toJSONLocal(window.selectedStartDate));
        formData.append('end_date', toJSONLocal(window.selectedEndDate));
        formData.append('calculated_data', JSON.stringify(window.calculatedData));
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
            hideOverlayPanel();
            window.location.href = data.redirect;
        }
    
        function onError(error) {
            hideOverlayPanel();
            showErrorToast(error.responseJSON.message);
            if (error.responseJSON?.code === 'outdated_price') {
                calc_booking();
            }
        }
        */
    });
})