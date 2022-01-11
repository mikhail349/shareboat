$(document).ready(() => {
    const $map = $("#map")
    if ($map.length > 0) {
        const lat = parseFloat($map.attr('data-lat').replace(",", ".")),
            lng = parseFloat($map.attr('data-lng').replace(",", "."));

        const map = L.map('map', { dragging: false }).setView([lat, lng], 12);
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
        L.marker([lat, lng], {icon: window.markerIcon}).addTo(map);
    }
});
            
            

            