$(document).ready(() => {

    const $modalMap = $("#modalMap");

    var map;
    var marker = {};

    $modalMap.on("shown.bs.modal", function (e) {
        const $rel = $(e.relatedTarget);

        var latlng = {
            lat: $rel.attr('data-coordinates-lat'),
            lng: $rel.attr('data-coordinates-lon')
        }

        map = L.map('map', { dragging: true }).setView(latlng, 12);
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);

        createMarker(latlng);
        $('.addressLabel').text($rel.attr('data-coordinates-address'));
        $('.addressLabel').addClass('text-primary');
    });

    $modalMap.on("hidden.bs.modal", function (e) {
        map.remove();
        map = null;
    });

    function createMarker(latlng) {
        map?.removeLayer(marker);
        marker = new L.marker(latlng, {draggable: false, icon: window.markerIcon});

        if (map) {
            marker?.addTo(map);
        }
    }

});
            
            

            