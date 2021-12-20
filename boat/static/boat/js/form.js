$(document).ready(() => {

    $("#typeSelect").on('change', (e) => {

        const boatType = parseInt($("#typeSelect option:selected").val());
        
        const $collapseMotorBoat = $("#collapseMotorBoat");
        const $fieldsetMotorBoat = $collapseMotorBoat.find("fieldset");

        if (window.motorBoatTypes.includes(boatType)) {
            $collapseMotorBoat.collapse("show");
            $fieldsetMotorBoat.removeAttr("disabled");         
        } else {
            $collapseMotorBoat.collapse("hide");
            $fieldsetMotorBoat.attr("disabled", "");
        }

        const $collapseComfortBoat = $("#collapseComfortBoat");
        const $fieldsetComfortBoat = $collapseComfortBoat.find("fieldset");

        if (window.comfortBoatTypes.includes(boatType)) {
            $collapseComfortBoat.collapse("show");
            $fieldsetComfortBoat.removeAttr("disabled");         
        } else {
            $collapseComfortBoat.collapse("hide");
            $fieldsetComfortBoat.attr("disabled", "");
        }
    })

    $("form").on('submit', async (e) => {
        e.preventDefault();

        const $form = $("form");
        if (!$form.checkValidity()) return;
        
        showOverlayPanel();

        const formData = new FormData($form[0]);

        const $files = $(".file-upload-wrapper img.card-img");

        for (let file of $files) {
            const $file = $(file);
            const src = $file.attr("src");
            const fileName = $file.attr("data-filename");

            const response = await fetch(src);
            const data = await response.blob();
            if (fileName) {
                formData.append("file", data, fileName);
            } else {
                formData.append("file", data);
            }
        }
        
        formData.append('prices', JSON.stringify(window.prices));

        const url = $form.attr("action");
        $.ajax({ 
            type: "POST",
            data: formData,
            url: url,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 
       
        function onSuccess(data) {
            hideOverlayPanel();
            window.location.href = data.redirect;
        }
    
        function onError(error) {
            hideOverlayPanel();
            showErrorToast(parseJSONError(error.responseJSON));
        }
    })

    var map;

    $("#switchCustomLocation").on('click', function (e) {
        if ($(this).is(":checked")) {
            $("#map").show();
             
            map = L.map('map', { dragging: !L.Browser.mobile }).setView([51.505, -0.09], 13);
            map.on('click', function(e){
                var marker = new L.marker(e.latlng).addTo(map);
            });
        
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
        } else {
            $("#map").hide();
            map?.remove();
        }
    })


})