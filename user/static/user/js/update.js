$(document).ready(() => {

    $("#btnSendConfirmation").on("click", () => {
        const email = $("#formProfile input[name=email]").val()
        showInfoToast(`Письмо с подтверждением отправлено на почту ${email}`)
    })

    $("#formProfile").on('submit', (e) => {
        e.preventDefault();   

        const form = $("#formProfile");
        const btnSubmit = form.find("button[type=submit]");
        
        if (!form.isValid()) return;
        
        btnSubmit.attr("disabled", true);
        $.ajax({ 
            type: "POST",
            data: form.serialize(),
            url: "/user/api/update/",
            success: onSuccess,
            error: onError
        });
    
        function onSuccess(data, status) {
            btnSubmit.attr("disabled", false);
            showSuccessToast();
        }
    
        function onError(error) {
            btnSubmit.attr("disabled", false);
            showErrorToast(error.responseJSON.message);
        }
    })
})