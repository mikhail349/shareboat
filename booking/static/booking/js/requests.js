$(document).ready(() => {

    const $declineModal = $('#declineRequestModal');
    const $formDecline = $('#formDecline'); 

    $declineModal.on('show.bs.modal', function(e) {
        const $btn = $(e.relatedTarget);
        $(this).attr('data-booking-id', $btn.attr('data-booking-id'));  
    })

    $declineModal.on('shown.bs.modal', function(e) {
        $('#textareaText').focus();
    })

    $declineModal.on('hidden.bs.modal', function(e) {
        $(this).removeAttr('data-booking-id');
        $formDecline[0].reset();
    })

    $formDecline.on('submit', function(e) {
        e.preventDefault();
        if (!$(this).checkValidity()) return;

        const bookingId = $declineModal.attr('data-booking-id');
        const formData = new FormData($(this)[0]);
        formData.append('search', window.location.search);
        const $btnSubmit = $('#formDecline button[type="submit"]')

        $btnSubmit.attr('disabled', true);
        $.ajax({ 
            type: "POST",
            url: `/bookings/api/set_request_status/${bookingId}/`,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        function onSuccess(data) {
            window.location.href = data.redirect;
        }

        function onError(error) {
            $btnSubmit.attr("disabled", false);
            showErrorToast(parseJSONError(error.responseJSON));
        }
    })

    $('a.accept-request').on('click', function(e) {
        e.preventDefault();
        const bookingId = $(this).attr('data-booking-id');
        const status = $(this).attr('data-status');
        const $btn = $(this);
        
        const formData = new FormData();
        formData.append('status', status);
        formData.append('search', window.location.search);

        $btn.attr('disabled', true);
        $.ajax({ 
            type: "POST",
            url: `/bookings/api/set_request_status/${bookingId}/`,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        function onSuccess(data) {
            window.location.href = data.redirect;
        }

        function onError(error) {
            $btn.attr("disabled", false);
            showErrorToast(parseJSONError(error.responseJSON));
        }
    })
});