$(document).ready(() => {
    $(".btn-fav-icon").on('click', function(e) {
        const pk = $(this).attr('data-pk');
        
        $.ajax({ 
            type: "POST",
            url: `/boats/api/switch_fav/${pk}/`
        }); 

        if ($(this).hasClass('text-primary')) {
            $(this).removeClass('text-primary');
            $(this).addClass('text-danger');            
        } else {
            $(this).removeClass('text-danger');
            $(this).addClass('text-primary');
        }
    })
})