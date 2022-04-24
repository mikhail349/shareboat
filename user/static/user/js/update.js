$(document).ready(() => {

    $("img.avatar").on("click", (e) => {
        $('input[name=avatar]').trigger('click'); 
    })

    const src = $("img.avatar").attr("src");
    var avatarName = src.replace(/^.*[\\\/]/, '');

    $('input[name=avatar]').on("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            const avatar = e.target.files[0];

            const formData = new FormData(); 
            formData.set("avatar", avatar, avatar.name);

            $.ajax({ 
                type: "POST",
                data: formData,
                url: "/user/api/update_avatar/",
                processData: false,
                contentType: false,
                success: (data) => {
                    showSuccessToast("Аватар изменён.");
                    $("img.avatar").attr('src', data.data);
                },
                //error: onError
            });

            /*var reader = new FileReader();

            reader.onload = (e) => {
                $("img.avatar").attr('src', e.target.result);
            };
            avatarName = e.target.files[0].name;
            reader.readAsDataURL(e.target.files[0]);*/
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

    $("#formProfile").on('submit', async (e) => {
        e.preventDefault();   

        const form = $("#formProfile");
        if (!form.checkValidity()) return;

        const formData = new FormData(form[0]);

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
            $("#navbarDropdownUserProfile span").text(userName || email);        
        }
    
        function onError(error) {
            hideOverlayPanel();
            showErrorToast(parseJSONError(error.responseJSON));
        }
    })
})