$(document).ready(() => {

    var map;
    var marker = {};

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

        if ($("#switchCustomLocation").is(":checked") && $.isEmptyObject(marker)) {
            showErrorToast('Поставьте точку на карте');
            return;
        }
        
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
        if (!$.isEmptyObject(marker)) {
            formData.append('custom_coordinates', JSON.stringify(marker.getLatLng()));
            formData.append('custom_address', window.customAddress);
        } else {
            //formData.append('custom_coordinates', {});
        }

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

    if (window.customCoordinates.length > 0) {
        var latlng = {
            lat: window.customCoordinates[0].fields.lat,
            lng: window.customCoordinates[0].fields.lon
        }
        createMarker(latlng);
        $('#addressLabel').text(window.customAddress);
    }

    $("#switchCustomLocation").on('click', function () {
        if ($(this).is(":checked")) {
            $("#baseSelect").attr('disabled', true);
            $("#mapContainer").show();

            var defaultLanLng = [55.72524,37.62896];

            if (!$.isEmptyObject(marker)) {
                defaultLanLng = marker.getLatLng();
            }
             
            map = L.map('map', { dragging: true }).setView(defaultLanLng, 12);
            if (!$.isEmptyObject(marker)) {
                marker.addTo(map);
            }
            map.on('click', function(e) {
               createMarker(e.latlng);
               reverseGeocode(e.latlng);
            });            
        
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
        } else {
            $("#mapContainer").hide();
            map.remove();
            map = null;
            $("#baseSelect").attr('disabled', false);
        }
    })

    if (window.customCoordinates.length > 0) {
        $("#switchCustomLocation").trigger('click');
    }

    function createMarker(latlng) {
        var markerIcon = L.icon({
            iconUrl: markerIconUrl,
            shadowUrl: markerShadowUrl,
        
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        map?.removeLayer(marker);
        marker = new L.marker(latlng, {draggable: true, icon: markerIcon}).on('dragend', function(e) {
            reverseGeocode(e.target.getLatLng());
        });

        if (map) {
            marker?.addTo(map);
        }
    }

    /*var addressInputTimeout;

    
    $('#addressInput').on('input', function(e) {
        //console.log(e, e.target.value);

        function onSuccess(data) {
            //if (data.display_name) {
            //    $("#addressInput").val(data.display_name);
            //    $("#addressInput").attr('disabled', false);
            //}
            
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
    })*/

    function reverseGeocode(latlng) {
        //$("#addressInput").val('Идет поиск...');
        //$("#addressInput").attr('disabled', true);
        $('#addressLabel').text('Идет поиск...');
        $.ajax({
            type: 'GET',
            url: `https://nominatim.openstreetmap.org/reverse?lat=${latlng.lat}&lon=${latlng.lng}&format=json&accept-language=ru`,
            success: onSuccess
        })
        function onSuccess(data) {
            if (data.display_name) {
                $('#addressLabel').text(data.display_name);
                window.customAddress = data.display_name;
            }
        }
    }
})