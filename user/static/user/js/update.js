$(document).ready(() => {

    $("img.avatar").on("click", (e) => {
        $('input[name=avatar]').trigger('click'); 
    })

    $('input[name=avatar]').on("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            const avatar = e.target.files[0];

            const formData = new FormData(); 
            formData.set("avatar", avatar, avatar.name);
            
            $("img.avatar").removeClass("enlarge-anim");
            $("img.avatar").addClass("downsize-anim");
            $("#loadingShipWheel").delay(200).show(0);

            $.ajax({ 
                type: "POST",
                data: formData,
                url: "/user/api/update_avatar/",
                processData: false,
                contentType: false,
                success: (data) => {
                    $("#loadingShipWheel").hide(0);
                    showSuccessToast("Аватар изменён");
                    
                    $("img.avatar").attr('src', data.avatar);
                    $("img.avatar").removeClass("downsize-anim");
                    $("img.avatar").addClass("enlarge-anim");

                    $("#navbarDropdownUserProfile > img").attr('src', data.avatar_sm);
                },
                error: (error) => {
                    $("#loadingShipWheel").hide(0);
                    $("img.avatar").removeClass("downsize-anim");
                    $("img.avatar").addClass("enlarge-anim");

                    showErrorToast(error?.responseJSON?.data);
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