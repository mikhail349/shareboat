$(document).ready(()=>{
    
    $("form").on("submit", async (e) => {
        e.preventDefault();

        const $form = $("form");
        if (!$form.checkValidity()) return;
           
        const formData = new FormData($form[0]);
        const method = $form.attr("method");
        const url = $form.attr("action");
        
        showOverlayPanel();
        $.ajax({ 
            type: method,
            data: formData,
            url: url,
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
            showErrorToast((error.responseJSON.message || error.data));
        }
    })
});