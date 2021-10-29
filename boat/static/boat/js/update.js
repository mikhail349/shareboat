$(document).ready(() => {
    $("#btnConfirmDelete").on("click", () => {
        const $confirmDeleteModal = $('#confirmDeleteModal');
        $confirmDeleteModal.modal('hide');
        const boatId = $confirmDeleteModal.attr("data-boat-id");
        
        showOverlayPanel("Удаление...");
        $.ajax({ 
            type: "POST",
            url: `/boats/api/delete/${boatId}/`,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            hideOverlayPanel();
            window.location.href = data.redirect;
        }
    
        function onError(error) {
            hideOverlayPanel();
            showErrorToast((error.responseJSON.message));
        }
    })
})