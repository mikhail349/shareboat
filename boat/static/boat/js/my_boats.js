$(document).ready(() => {
    $("a[data-boat-id]").on('click', function (e) {
        e.preventDefault();
    })

    $("a[data-boat-id][data-status]").on('click', function(e) {
        e.preventDefault();
        
        const boatId = $(this).attr('data-boat-id');
        const status = $(this).attr('data-status');
        const formData = new FormData();
        formData.append('status', status);

        const $btn = $(`#dropdownMenuStatus${boatId}`);
        $btn.attr("disabled", true);
        
        $.ajax({ 
            type: "POST",
            url: `/boats/api/set_status/${boatId}/`,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        function onSuccess(data) {
            document.location.reload();
        }

        function onError(error) {
            $btn.attr("disabled", false);
            showErrorToast(parseJSONError(error.responseJSON));
        }
    })
})