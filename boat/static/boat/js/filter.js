var dpRange;

$(document).ready(() => {
    const params = new URLSearchParams(window.location.search);

    var dateFrom,
        dateTo;

    if (params.has('dateFrom')) {
        dateFrom = new Date(params.get('dateFrom'));
    }
    
    if (params.has('dateTo')) {
        dateTo = new Date(params.get('dateTo'));
    }

    dpRange = new AirDatepicker('#dpRange', {
        selectedDates: [
            dateFrom,
            dateTo
        ],
        autoClose: true,
        isMobile: window.isMobile(),
        range: true,
        minDate: new Date(),
        multipleDatesSeparator: ' - ',
        buttons: ['clear']
    });

    $('#formFilter').on('submit', function(e) {

        if (dpRange.selectedDates.length == 1) {
            showErrorToast('Выберите период бронирования или очистите это поле');
            e.preventDefault();
            return;
        }

        if (!$(this).checkValidity()) return;

        if (dpRange.selectedDates.length == 2) {
            $("#hiddenDateFrom").val(toJSONLocal(dpRange.selectedDates[0]));
            $("#hiddenDateTo").val(toJSONLocal(dpRange.selectedDates[1]));
        }

        const $btnSubmit = $('#formFilter button[type=submit]');
        $btnSubmit.attr('disabled', true);
        $btnSubmit.text('Идет поиск...');
    });

    $("#btnOffcanvasBoatFilterClear").on('click', function(e) {
        clearFilter();
    });
});

function clearFilter() {
    dpRange.clear();
    $("#offcanvasBoatFilter input[type=checkbox]").prop("checked", false);
    $("#offcanvasBoatFilter input").val("");
    $("#offcanvasBoatFilter select").val("");
    $("#offcanvasBoatFilter button[type=submit]").click();
}