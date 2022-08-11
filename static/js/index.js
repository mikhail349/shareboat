var dpRange;

$(document).ready(() => {

    dpRange = new AirDatepicker('#dpRange', {
        autoClose: true,
        isMobile: window.isMobile(),
        range: true,
        minDate: new Date(),
        multipleDatesSeparator: ' - ',
        buttons: ['clear']
    });

    $('#formSearch').on('submit', function(e) {

        if (dpRange.selectedDates.length == 1) {
            showErrorToast('Выберите период бронирования или очистите это поле');
            e.preventDefault();
            return;
        }

        if (dpRange.selectedDates.length == 2) {
            $("#hiddenDateFrom").val(toJSONLocal(dpRange.selectedDates[0]));
            $("#hiddenDateTo").val(toJSONLocal(dpRange.selectedDates[1]));
        }
    });
})

function setAppHeight() {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

window.addEventListener('resize', setAppHeight);
setAppHeight();
