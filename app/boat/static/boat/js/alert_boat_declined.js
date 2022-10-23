$(document).ready(() => {
    $('#btnDeleteDeclinedModeration').on('click', function (e) {
        const notificationId = $(this).attr('data-notification-id');
        $.ajax({ 
            type: "POST",
            url: `/notifications/api/delete/${notificationId}/`
        });
    })
})