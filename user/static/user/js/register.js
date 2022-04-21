function recaptchaCallback() {
    $('form button[type="submit"]').removeAttr('disabled');
}

$(document).ready(() => {
    $("form").on("input", (e) => {

        const password1 = $("#password1");
        const password2 = $("#password2");
        const password2Tooltip = $("form input[name=password2] ~ .invalid-tooltip");

        password2[0].setCustomValidity(password1.val() != password2.val() ? "Пароли не совпадают" : "");     

        if (password1.val() != password2.val()) {
            password2Tooltip.text("Пароли не совпадают");
        }

        if (!password2.val().length) {
            password2Tooltip.text("Повторите пароль");
        }
    });
})