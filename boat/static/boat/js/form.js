function onAfterPopupClosed(window, data) {
    window.close();
    $('select[name="term"]').append(new Option(text=data.name, value=data.pk, defaultSelected=true, selected=true));
}

$(document).ready(() => {

    var map;
    var marker = {};

    const $manufacturerSelect = $("#manufacturerSelect");
    const $modelSelect = $("#modelSelect");

    $manufacturerSelect.on('change', function(e) {
        $modelSelect.html('<option selected disabled value="">Выберите из списка</option>');
        
        const pk = parseInt($("#manufacturerSelect option:selected").val());
        if (isNaN(pk)) {
            return;
        }
        
        $.ajax({ 
            type: "GET",
            url: `/boats/api/get_models/${pk}/`,
            success: (data) => {
                for (let model of data.data) {
                    $modelSelect.append(`
                        <option value="${model.id}">${model.name}</option>
                    `);
                }
            }
        }); 
    })

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
            showErrorToast('Укажите адрес');
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

        if ($("#switchCustomLocation").is(":checked")) {
            const latlng = marker.getLatLng();
            window.boatCoordinates.lat = latlng.lat;
            window.boatCoordinates.lon = latlng.lng;
            formData.append('boat_coordinates', JSON.stringify(window.boatCoordinates));
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

    $("#addressMapModal").on("shown.bs.modal", function (e) {
        var defaultLanLng = [55.75524,37.62896];

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
    });

    $("#addressMapModal").on("hidden.bs.modal", function (e) {
        map.remove();
        map = null;
    });

    $("#switchCustomLocation").on('click', function (e) {
        if ($(this).is(":checked")) {
            $("#baseSelect").attr('disabled', true);
            $("#collapseBase").collapse('hide');
            $("#collapseCustomAddress").collapse('show');
            if (e?.originalEvent?.isTrusted) {
                $('#btnShowAddressMapModal').click();
            }
        } else {
            $("#collapseBase").collapse('show');
            $("#collapseCustomAddress").collapse('hide');
            $("#baseSelect").attr('disabled', false);
        }
    })

    $("#btnAddTerm").on('click', function() {
        const url = $(this).attr('data-action');
        //const params = 'scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no';
        window.open(url, 'addTerm');
    })

    $("#addressMapModalSearchButton").on('click', function(e) {
        const text = $("#addressMapModalSearchText").val();
        if (!text) {
            showErrorToast('Введите адрес');
            return;
        }
        geocode(text);
    })

    $(document).on("keypress", "#addressMapModalSearchText", function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            e.preventDefault();
            const $btn = $("#addressMapModalSearchButton");
            $btn.focus();
            $btn.click(); 
            return false;
        }
    });

    if (window.isCustomLocation) {
        var latlng = {
            lat: window.boatCoordinates.lat,
            lng: window.boatCoordinates.lon
        }
        createMarker(latlng);
        $('.addressLabel').text(window.boatCoordinates.address);
        $('.addressLabel').addClass('text-primary');

        $("#switchCustomLocation").trigger('click');
    }


    function createMarker(latlng) {
        map?.removeLayer(marker);
        marker = new L.marker(latlng, {draggable: true, icon: window.markerIcon}).on('dragend', function(e) {
            reverseGeocode(e.target.getLatLng());
        });

        if (map) {
            marker?.addTo(map);
        }
    }

    function geocode(text) {
        $.ajax({
            type: 'GET',
            url: `https://nominatim.openstreetmap.org/?q=${text}&format=json&accept-language=ru`,
            success: onSuccess,
        })
        function onSuccess(data) {
            if (data.length == 0) {
                return showErrorToast('Ничего не найдено');
            }
            const obj = data[0];

            var latlng = {
                lat: obj.lat,
                lng: obj.lon
            }

            map.setView(latlng);
            createMarker(latlng);
            reverseGeocode(latlng);
        }
    }

    function reverseGeocode(latlng) {
        $("form button[type=submit").attr('disabled', true);
        
        $('.addressLabel').text('Идет поиск...');
        $('.addressLabel').removeClass('text-primary');

        $.ajax({
            type: 'GET',
            url: `https://nominatim.openstreetmap.org/reverse?lat=${latlng.lat}&lon=${latlng.lng}&format=json&accept-language=ru`,
            success: onSuccess,
            error: onError
        })
        function onSuccess(data) {
            if (data.display_name) {
                $('.addressLabel').text(data.display_name);
                $('.addressLabel').addClass('text-primary');
                window.boatCoordinates.address = data.display_name;
                window.boatCoordinates.state = data?.address?.state;
                $("form button[type=submit").attr('disabled', false);
            }
        }
        function onError() {
            $("form button[type=submit").attr('disabled', false);
            map?.removeLayer(marker);
            marker = null;
        }
    }
})