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
    var marker = {};

    $("#switchCustomLocation").on('click', function (e) {
        if ($(this).is(":checked")) {
            $("#mapContainer").show();
             
            map = L.map('map', { /*dragging: !L.Browser.mobile*/ }).setView([55.72524,37.62896], 12);
            map.on('click', function(e){
                var markerIcon = L.icon({
                    iconUrl: markerIconUrl,
                    shadowUrl: markerShadowUrl,
                
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                map?.removeLayer(marker);
                marker = new L.marker(e.latlng, {draggable: true, icon: markerIcon}).on('dragend', function(e) {
                    //map?.removeLayer(marker);
                    console.log('dragend', e.target.getLatLng());
                    reverseGeocode(e.target.getLatLng());
                }).addTo(map);

               reverseGeocode(e.latlng);
            });            
        
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
        } else {
            $("#mapContainer").hide();
            map?.remove();
        }
    })

    var addressInputTimeout;

    $('#addressInput').on('input', function(e) {
        //console.log(e, e.target.value);

        function onSuccess(data) {
            /*if (data.display_name) {
                $("#addressInput").val(data.display_name);
                $("#addressInput").attr('disabled', false);
            }*/
            
            //for (let item of data) {
            //    $("#addressList").append($("<option>").attr('value', 'item.display_name'));
            //}

            $.each(data, function(i, item) {
                //if (item.class !== 'boundary') {
                    //console.log(item);
                    $("#addressList").append($("<li>").text(item.display_name));
                //}
                
            });
        }

        clearTimeout(addressInputTimeout);
        addressInputTimeout = setTimeout(function() {
            $("#addressList").empty();
            $.ajax({
                type: 'GET',
                url: `https://nominatim.openstreetmap.org/search?q=${e.target.value}&format=json&accept-language=ru`,
                success: onSuccess
            });
        }, 300);
    })

    function reverseGeocode(latlng) {
        $("#addressInput").val('Идет поиск...');
        $("#addressInput").attr('disabled', true);
        $.ajax({
            type: 'GET',
            url: `https://nominatim.openstreetmap.org/reverse?lat=${latlng.lat}&lon=${latlng.lng}&format=json&accept-language=ru`,
            success: onSuccess
        })
        function onSuccess(data) {
            if (data.display_name) {
                $("#addressInput").val(data.display_name);
                $("#addressInput").attr('disabled', false);
            }
        }
    }
})