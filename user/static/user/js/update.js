$(document).ready(() => {

    var verificationEmailTimer = null;

    if ( $("#alertEmailNotConfirmed").length ) {
        verificationEmailInterval();
        verificationEmailTimer = setInterval(verificationEmailInterval, 1000);
    }

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


    function verificationEmailInterval() {
        const now = new Date();

        var diff = nextVerificationEmailDatetime.getTime() - now.getTime();
        var totalSeconds = Math.round(diff / 1000);

        if (totalSeconds <= 0) {
            clearInterval(verificationEmailTimer);
            $("#alertEmailNotConfirmed span").text("Ваша почта пока ещё не подтверждена.");
            $("#btnSendConfirmation").show();
            return;
        }

        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
        const seconds = totalSeconds - (hours * 3600) - (minutes * 60);
        let val = '';
        if (hours > 0) val += `${hours} ч.`;
        if (minutes > 0) val += ` ${minutes} мин.`;
        if (seconds > 0) val += ` ${seconds} сек.`;
        val = val.trim()
        
        $("#alertEmailNotConfirmed span").html(`Письмо отправлено на почту. Повторная отправка возможна через <span style='word-wrap:break-word; display:inline-block;' >${val}</span>`)
    }

    $("#btnSendConfirmation").on("click", (e) => {
        e.preventDefault();

        $("#btnSendConfirmation").hide();
        $.ajax({ 
            type: "POST",
            url: "/user/api/send_verification_email/",
            success: onSuccess,
            error: onError
        });
    
        function onSuccess(data, status) {
            nextVerificationEmailDatetime = new Date(data.next_verification_email_datetime);
            verificationEmailInterval();
            verificationEmailTimer = setInterval(verificationEmailInterval, 1000);
        }
    
        function onError(error) {
            showErrorToast(error.responseJSON.message);
            $("#btnSendConfirmation").show();
        }   
    })



    $("#formProfile").on('submit', async (e) => {
        e.preventDefault();   

        const form = $("#formProfile");
        if (!form.checkValidity()) return;

        const formData = new FormData(form[0]);

        if ($("img.avatar")[0].hasAttribute('data-do-save')) {
            let response = await fetch($("img.avatar").attr("src"));
            let data = await response.blob();
            formData.set("avatar", data, avatarName);
        }

        showOverlayPanel();
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
            hideOverlayPanel();
            showSuccessToast();
            const userName = $('input[name=first_name]').val()
            const email = $("#formProfile input[name=email]").val();
            $("#userNameNavBar").text(userName || email);
        }
    
        function onError(error) {
            hideOverlayPanel();
            showErrorToast(error.responseJSON.message);
        }
    })
})