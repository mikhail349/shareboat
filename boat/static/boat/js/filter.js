$(document).ready(() => {
    $("#btnOffcanvasBoatFilterClear").on('click', function(e) {
        $("#offcanvasBoatFilter input[type=checkbox]").prop("checked", false);
        $("#offcanvasBoatFilter input").val("");
        $("#offcanvasBoatFilter select").val("");
        $("#offcanvasBoatFilter button[type=submit]").click();
    });
});