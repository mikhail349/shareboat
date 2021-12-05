$(document).ready(() => {

    const modified = $("div[data-boat-modified]").attr('data-boat-modified');

    $('#btnAcceptBoat').on('click', function (e) {
        e.preventDefault();
        
        const data = new FormData();
        data.append('modified', modified);
        
        $.ajax({ 
            type: "POST",
            url: $(this).attr('href'),
            data: data,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            window.location.href = data.redirect;
        }
    
        function onError(error) {
            if (error.responseJSON?.code === 'outdated') {
                $("#outdatedModal").modal('show');
            } else {
                showErrorToast(parseJSONError(error.responseJSON)); 
            }
        }
    })

    $("#outdatedModal button").on('click', function (e) {
        document.location.reload();
    })

    $("#formDecline").on('submit', function (e) {
        e.preventDefault();
        console.log('sumbit');
        if (!$(this).checkValidity(doShowErrorToast=false)) return;

        const data = new FormData($(this)[0]);
        data.append('modified', modified);
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: data,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        })

        function onSuccess(data) {
            window.location.href = data.redirect;
        }
    
        function onError(error) {
            if (error.responseJSON?.code === 'outdated') {
                $("#declineModal").modal('hide');
                $("#outdatedModal").modal('show');
            } else {
                showErrorToast(parseJSONError(error.responseJSON)); 
            }
        }
    })
});