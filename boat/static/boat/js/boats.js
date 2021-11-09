$(document).ready(() => {

    $("#btnFilterClear").on('click', function (e) {
        $("#offcanvasBoatFilter input[type=checkbox]").prop("checked", false);
        $("#offcanvasBoatFilter input").val("");
    })

    $("#formApplyFilter").on('submit input', function(e) {

        const $priceFromInput = $("form input[name=priceFrom]")
        const $priceToInput = $("form input[name=priceTo]")
        const isInvalidPriceRange = (parseFloat($priceFromInput.val()) > parseFloat($priceToInput.val()));
        const INVALID_PRICE_RANGE_MSG = 'Цена от не должна быть больше цены до';
        $priceFromInput[0].setCustomValidity(isInvalidPriceRange ? INVALID_PRICE_RANGE_MSG : "");

        if (isInvalidPriceRange) {
            $priceFromInput.siblings(".invalid-tooltip").text(INVALID_PRICE_RANGE_MSG);
        } else {
            $priceFromInput.siblings(".invalid-tooltip").text("Укажите корректную цену");
        }

        const $dateFromInput = $("form input[name=dateFrom]");
        const $dateToInput = $("form input[name=dateTo]");
        const INVALID_DATE_RANDGE_MSG = 'Аренда с не должна быть позже аренды по';
        
        let isInvalidDateRange = false;
        if ($dateFromInput.val() && $dateToInput.val()) {
            const dateFrom = new Date($dateFromInput.val());
            const dateTo = new Date($dateToInput.val());
            isInvalidDateRange = dateFrom > dateTo;
        }
        $dateFromInput[0].setCustomValidity(isInvalidDateRange ? INVALID_DATE_RANDGE_MSG : "");
        if (isInvalidDateRange) {
            $dateFromInput.siblings(".invalid-tooltip").text(INVALID_DATE_RANDGE_MSG);
        } else {
            $dateFromInput.siblings(".invalid-tooltip").text("Укажите корректную дату");
        }
   
        if (isInvalidPriceRange || isInvalidDateRange) {
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        for (let boatTypeInput of $('input[data-boat-type]:checked')) {
            let boatType = $(boatTypeInput).attr('data-boat-type');
            $(this).prepend(`<input type="hidden" name="boatType" value="${boatType}" />`);
        }
    })
})