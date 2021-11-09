$(document).ready(() => {
    $("#formApplyFilter").on('submit', function(e) {
        e.preventDefault();
        let url = $(this).attr("action");

        for (let boatTypeInput of $('input[data-boat-type]:checked')) {
            let boatType = $(boatTypeInput).attr('data-boat-type');
            url += `boatType=${boatType}&`
        }
        
        console.log(url);
        
        /*$.ajax({ 
            type: "GET",
            url: '/boats/',
            processData: false, 
            contentType: false,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            //hideOverlayPanel();
            //window.location.href = data.redirect;
        }
    
        function onError(error) {
            //hideOverlayPanel();
            //showErrorToast(parseJSONError(error.responseJSON));
        }*/
    })
})