$(document).ready(() => {

    const searchParams = new URLSearchParams(window.location.search);
    const inputDatesExist = searchParams.has('dateFrom') && searchParams.has('dateTo');

    const dateRange = new AirDatepicker('#dateRange', {
        selectedDates: [
            inputDatesExist ? new Date(searchParams.get('dateFrom')) : undefined,
            inputDatesExist ? new Date(searchParams.get('dateTo')) : undefined
        ],
        autoClose: true,
        range: true,
        minDate: new Date(Math.max.apply(null,[firstPriceDate, new Date()])),
        maxDate: lastPriceDate,
        multipleDatesSeparator: ' - ',
        position: 'top left',
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
            return;
        }

        window.selectedStartDate = dateRange.selectedDates[0];
        window.selectedEndDate = dateRange.selectedDates[1];
        window.totalSum = null;

        if (!!xhr) xhr.abort();
        xhr = $.ajax({ 
            type: "GET",
            url: `/boats/api/calc_booking/${boatId}/?start_date=${toJSONLocal(dateRange.selectedDates[0])}&end_date=${toJSONLocal(dateRange.selectedDates[1])}`,
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
            
            $('#priceAlert').removeClass('alert-success');
            $('#priceAlert').removeClass('alert-secondary');
            $('#priceAlert').addClass('alert-danger');
            $('#priceAlert').html(`
                <h5>${parseJSONError(error.responseJSON)}</h5>
            `);
        }   
    }

    var xhr = null;

    $("form").on('submit', function(e) {
        e.preventDefault();

        if (!$(this).checkValidity(false)) return;
        
        showOverlayPanel("Бронирование...");
        const url = $(this).attr("action");
        const formData = new FormData();
        formData.append('start_date', toJSONLocal(window.selectedStartDate));
        formData.append('end_date', toJSONLocal(window.selectedEndDate));
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
    });
})