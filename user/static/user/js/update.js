function showSuccessAlert() {

    const MSG = 'Аватар изменён.';
    const $alert = $(".alert.alert-success");
    
    if ($alert.length) {
        $alert.html(MSG)
    } else {
        $("#formProfile > .container-lg").prepend(`<div class="alert alert-success">${ MSG }</div>`)
    }
}

$(document).ready(() => {

    $("img.avatar").on("click", (e) => {
        $('input[name=avatar]').trigger('click'); 
    })

    $("img.avatar").on("load", (e) => {
        $("#loadingShipWheel").hide(0);
        $("img.avatar").removeClass("downsize-anim");
        $("img.avatar").addClass("enlarge-anim");
    })

    $('input[name=avatar]').on("change", function(e) {
        if (e.target.files && e.target.files[0]) {
            const avatar = e.target.files[0];

            const formData = new FormData(); 
            formData.set("avatar", avatar, avatar.name);
            
            $("img.avatar").removeClass("enlarge-anim");
            $("img.avatar").addClass("downsize-anim");
            $("#loadingShipWheel").delay(200).show(0);

            var self = this;
            $.ajax({ 
                type: "POST",
                data: formData,
                url: "/user/api/update_avatar/",
                processData: false,
                contentType: false,
                success: (data) => {
                    showSuccessAlert();
                    
                    $("img.avatar").attr('src', data.avatar);
                    $("#navbarDropdownUserProfile > img").attr('src', data.avatar_sm);
                },
                error: (error) => {
                    $("img.avatar").attr('src', $("img.avatar").attr('src'));

                    showErrorToast(error?.responseJSON?.data);
                    $(self).val(null);
                }
            });
        }
    })

    $("#btnGenerateTgCode").on('click', function (e) {
        e.preventDefault();
        
        $btn = $(this);
        $btn.attr("disabled", true);
        $.ajax({ 
            type: "GET",
            url: "/user/api/generate_telegram_code/",
            success: onSuccess,
            error: onError
        });    
        
        function onSuccess(data, status) {
            $btn.remove();
            $("#tgAuth").remove();
            $("#tgCode").html(data.message);
        }

        function onError(error) {
            $btn.attr("disabled", false);
        }
    })
})