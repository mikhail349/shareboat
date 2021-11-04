$(document).ready(() => {
    $("form").on("input", (e) => {

        const $password1 = $("#password1Input");
        const $password2 = $("#password2Input");
        const $password2Tooltip = $("#password2Input ~ .invalid-tooltip");

        const passwordsAreDiff = $password1.val() != $password2.val();

        $password2[0].setCustomValidity(passwordsAreDiff ? "Пароли не совпадают" : "");     

        if (passwordsAreDiff) {
            $password2Tooltip.text("Пароли не совпадают");
        }

        if (!$password2.val().length) {
            $password2Tooltip.text("Повторите пароль");
        }
    });
})