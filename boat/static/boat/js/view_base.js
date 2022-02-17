$(document).ready(() => {
    /*const $map = $("#map")
    if ($map.length > 0) {
        const lat = parseFloat($map.attr('data-lat').replace(",", ".")),
            lng = parseFloat($map.attr('data-lng').replace(",", "."));

        const map = L.map('map', { dragging: false }).setView([lat, lng], 12);
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
        L.marker([lat, lng], {icon: window.markerIcon}).addTo(map);
    }*/

    var map;
    var marker = {};

    $("#addressMapModal").on("shown.bs.modal", function (e) {
        var defaultLanLng = [55.75524,37.62896];

        if (!$.isEmptyObject(marker)) {
            defaultLanLng = marker.getLatLng();
        }
         
        map = L.map('map', { dragging: true }).setView(defaultLanLng, 12);
        if (!$.isEmptyObject(marker)) {
            marker.addTo(map);
        }       
    
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
    });

    $("#addressMapModal").on("hidden.bs.modal", function (e) {
        map.remove();
        map = null;
    });

    if (!$.isEmptyObject(window.coordinates)) {
        var latlng = {
            lat: window.coordinates.lat,
            lng: window.coordinates.lon
        }
        createMarker(latlng);
        $('.addressLabel').text(window.coordinates.address);
        $('.addressLabel').addClass('text-primary');
    }

    function createMarker(latlng) {
        map?.removeLayer(marker);
        marker = new L.marker(latlng, {draggable: false, icon: window.markerIcon});

        if (map) {
            marker?.addTo(map);
        }
    }
});
            
            

            