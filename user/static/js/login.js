$(document).ready(() => {
    $("form").on("submit", () => {
        $("button[type=submit]").attr("disabled", true);
        this.submit();
    })
})