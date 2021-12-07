$(document).ready(() => {
    $('#btnDeleteDeclinedModeration').on('click', function (e) {
        const boatId = $(this).attr('data-boat-id');
        $.ajax({ 
            type: "POST",
            url: `/boats/api/delete_declined_moderation/${boatId}/`
        });
    })
})