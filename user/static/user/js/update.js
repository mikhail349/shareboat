$(document).ready(() => {
    const btnSubmit = $("#formProfile button[type=submit]");
    $("#formProfile").on('submit', (e) => {
        e.preventDefault();
        btnSubmit.attr("disabled", true);

        $.ajax({ 
            type: "POST",
            data: $("#formProfile").serialize(),
            url: "/user/api/update/",
            success: onSuccess,
            error: onError
        });
    
        function onSuccess(data, status) {
            btnSubmit.attr("disabled", false);
            $("#toast .toast-body").text("Изменения сохранены");
            $("#toast").addClass("bg-success");
            $("#toast").toast('show');
        }
    
        function onError(error) {
            btnSubmit.attr("disabled", false);
            $("#toast .toast-body").text(error.responseJSON.message);
            $("#toast").addClass("bg-danger");
            $("#toast").toast('show');
            console.log('error', error);
        }
    })

    $("toast button[data-bs-dismiss=toast]").on('click', () => {
        $("#toast").toast('hide')
    })
})