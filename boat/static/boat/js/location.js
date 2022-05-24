$(document).ready(() => {

    $(".modal.map").on("shown.bs.modal", function (e) {
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
});
            
            

            