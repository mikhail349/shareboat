$(document).ready(() => {

    $("#btnFilterClear").on('click', function (e) {
        $("#offcanvasBoatFilter input[type=checkbox]").prop("checked", false);
        $("#offcanvasBoatFilter input").val("");
    })

    $("#formApplyFilter").on('submit input', function(e) {

        const $priceFromInput = $("form input[name=priceFrom]")
        const $priceToInput = $("form input[name=priceTo]")
        const isInvalidRange = (parseFloat($priceFromInput.val()) > parseFloat($priceToInput.val()));
        const INVALID_RANDGE_MSG = 'Цена от не должна быть больше цены до';
        $priceFromInput[0].setCustomValidity(isInvalidRange ? INVALID_RANDGE_MSG : "");

        if (INVALID_RANDGE_MSG) {
            $priceFromInput.siblings(".invalid-tooltip").text(INVALID_RANDGE_MSG);
        } else {
            $priceFromInput.siblings(".invalid-tooltip").text("Укажите корректную цену");
        }
        
        if (isInvalidRange) {
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