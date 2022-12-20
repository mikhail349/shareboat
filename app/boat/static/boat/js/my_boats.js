$(document).ready(() => {

    $("#confirmDeleteModal").on('show.bs.modal', function (e) {
        const boatId = $(e.relatedTarget).attr('data-boat-id');
        $(this).attr('data-boat-id', boatId);
    })

    $("#confirmDeleteModal").on('hide.bs.modal', function (e) {
        $(this).attr('data-boat-id', -1);
    });

    $("#btnConfirmDelete").on("click", () => {
        const $confirmDeleteModal = $('#confirmDeleteModal');
        const boatId = $confirmDeleteModal.attr("data-boat-id");
        $confirmDeleteModal.modal('hide');
        
        showOverlayPanel("Удаление...");
        $.ajax({ 
            type: "POST",
            url: `/boats/api/delete/${boatId}/`,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            document.location.reload();
        }
    
        function onError(error) {
            hideOverlayPanel();
            showErrorToast(parseJSONError(error.responseJSON));
        }
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