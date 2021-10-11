$(document).ready(() => {

    $('#confirmDeleteModal').on('shown.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const id = button.attr('data-id');
        const name = button.attr('data-name');
        $('#btnConfirmDelete').attr('data-id', id);
        $('#confirmDeleteModal .modal-body > p').text(`Удалить актив "${name}"?`);
      })

    $('#btnConfirmDelete').click(() => {
        $('#confirmDeleteModal').modal('hide');
        const id = $("#btnConfirmDelete").attr('data-id');

        $.ajax({ 
            type: "POST",
            url: `/asset/api/delete/${id}/`,
            contentType: "application/json; charset=utf-8",
            success: onSuccess,
            error: onError
        });
    
        function onSuccess(data, status) {
            location.reload();
        }
    
        function onError(error) {
            //console.log(error);
            //alert(error.responseJSON.message);
            $(".toast").toast("show");
        }
    })
})