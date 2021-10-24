$(document).ready(() => {

    $("img.avatar").on("click", (e) => {
        $('input[name=avatar]').trigger('click'); 
    })

    const src = $("img.avatar").attr("src");
    var avatarName = src.replace(/^.*[\\\/]/, '');

    $('input[name=avatar]').on("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            var reader = new FileReader();

            reader.onload = (e) => {
                $("img.avatar").attr('src', e.target.result);
                $("img.avatar").attr('data-do-save', "true");
            };
            avatarName = e.target.files[0].name;
            reader.readAsDataURL(e.target.files[0]);
        }
    })

    $("#btnSendConfirmation").on("click", (e) => {
        e.preventDefault();
        const email = $("#formProfile input[name=email]").val()
        showInfoToast(`Письмо с подтверждением отправлено на почту ${email}`)
    })

    $("#formProfile").on('submit', async (e) => {
        e.preventDefault();   

        const form = $("#formProfile");
        const btnSubmit = form.find("button[type=submit]");
        
        if (!form.checkValidity()) return;

        const formData = new FormData(form[0]);

        if ($("img.avatar")[0].hasAttribute('data-do-save')) {
            let response = await fetch($("img.avatar").attr("src"));
            let data = await response.blob();
            formData.set("avatar", data, avatarName);
        }
    
        $.ajax({ 
            type: "POST",
            data: formData,
            url: "/user/api/update/",
            processData: false,
            contentType: false,
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