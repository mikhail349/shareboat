$(document).ready(() => {

    var nextEmailDatetime = null;
    var emailTimer = null;
    const $fieldset = $("form fieldset");

    function emailInterval() {
        const now = new Date();

        var diff = nextEmailDatetime.getTime() - now.getTime();
        var totalSeconds = Math.round(diff / 1000);

        if (totalSeconds <= 0) {
            clearInterval(emailTimer);
            $("#alertEmail").hide();
            $fieldset.attr("disabled", false);
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
        
        $("#alertEmail").show();
        $("#alertEmail").html(`Письмо отправлено на почту. Повторная отправка возможна через <span style='word-wrap:break-word; display:inline-block;' >${val}</span>`)
    }

    $("form").on('submit', async (e) => {
        e.preventDefault();

        const $form = $("form");
        
        if (!$form.checkValidity()) return;
        const formData = new FormData($form[0]);

        $fieldset.attr("disabled", true);
        $.ajax({ 
            type: "POST",
            url: "/user/api/send_restore_password_email/",
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        });
    
        function onSuccess(data, status) {
            nextEmailDatetime = new Date(data.next_email_datetime);
            emailInterval();
            emailTimer = setInterval(emailInterval, 1000);
        }
    
        function onError(error) {
            showErrorToast(error.responseJSON?.message);
            $fieldset.attr("disabled", false);
        }   
    });
})