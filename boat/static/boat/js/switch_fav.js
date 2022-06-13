$(document).ready(() => {
    $(".btn-fav-icon").on('click', function(e) {
        const pk = $(this).attr('data-pk');
        
        const self = this;
        $.ajax({ 
            type: "POST",
            url: `/boats/api/switch_fav/${pk}/`,
            success: (data) => {
                if (data?.data === 'redirect') {
                    window.location.href = data?.url;
                } else if (data?.data === 'added') {
                    $(self).removeClass('text-primary');
                    $(self).addClass('text-danger');                          
                } else if (data?.data === 'deleted') {
                    $(self).removeClass('text-danger');
                    $(self).addClass('text-primary');                       
                }
            }
        }); 

        $(this).removeClass('scale-anim');
        $(this)[0].offsetWidth; // reflow
        $(this).addClass('scale-anim');
    })
})