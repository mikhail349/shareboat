$(document).ready(() => {
    $("#saveBtn").click(async () => {
        console.log('click');

        let formData = new FormData();

        const appendFile = (url) => {
            let response = fetch(url);
            //formData.append('file', file);
            console.log(response)
        }

        $(".card img").each( async function(index, element) {
            let url = $( this ).attr('src');
            file = await fetch(url);
            appendFile(url);
            formData.append('file', file);
        })

        console.log(formData);
        
        //const file = $("#btnAddFiles").attr('data-id')
        
        $.ajax({ 
            type: "POST",
            url: `/asset/create/`,
            data: formData,
            processData: false,
            contentType: false 
            //contentType: "application/json; charset=utf-8",
            //success: onSuccess,
            //error: onError
        });
    });
});