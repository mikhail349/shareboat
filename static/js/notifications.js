$(document).ready(() => {
    $('button[data-notification-id]').on('click', function (e) {
        $(this).attr('disabled', true);
        const notificationId = $(this).attr('data-notification-id');
        $.ajax({ 
            type: "POST",
            url: `/notifications/api/delete/${notificationId}/`,
            success: onSuccess
        });

        function onSuccess() {
            $(`#notificationCard${notificationId}`).remove();
        }
    })

    $("#btnDeleteAll").on('click', function (e) {
        $(this).attr('disabled', true);
        $.ajax({ 
            type: "POST",
            url: `/notifications/api/delete_all/`,
            success: onSuccess
        });

        function onSuccess() {
            $('[id*="notificationCard"]').remove();
            $("#offcanvasNotifications").offcanvas('hide');
        }
       
    })
})