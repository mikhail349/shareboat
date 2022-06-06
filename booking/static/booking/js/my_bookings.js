$(document).ready(() => {

    $("a[data-booking-id][data-status]").on('click', function(e) {
        e.preventDefault();
        
        const bookingId = $(this).attr('data-booking-id');
        const status = $(this).attr('data-status');
        const formData = new FormData();
        formData.append('status', status);
        formData.append('search', window.location.search);

        const $btn = $(`#dropdownMenuStatus${bookingId}`);
        $btn.attr("disabled", true);
        
        $.ajax({ 
            type: "POST",
            url: `/bookings/api/set_status/${bookingId}/`,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        function onSuccess() {
            window.location.href = data.redirect;
        }

        function onError(error) {
            $btn.attr("disabled", false);
            showErrorToast(parseJSONError(error.responseJSON));
        }
    })

});