$(document).ready(() => {
    console.log('ready');
    $("#btnConfirmDelete").on("click", () => {
        console.log('delete');
        const $confirmDeleteModal = $('#confirmDeleteModal');
        $confirmDeleteModal.modal('hide');
        const postId = $confirmDeleteModal.attr("data-post-id");
        
        showOverlayPanel("Удаление...");
        $.ajax({ 
            type: "POST",
            url: `/posts/api/delete/${postId}/`,
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