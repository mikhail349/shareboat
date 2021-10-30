$(document).ready(() => {

    /*class InputValidator {
        constructor(input, tooltip) {
            this.input = input;
            this.tooltip = $(input).siblings(".invalid-tooltip");
            this.errorsList = [];
        }

        addError(msg, f) {
            if (f(this.input.val())) {
                this.errorsList.push(msg);
            }
        }

        validate() {
            const error = this.errorsList.join("\n");
            this.input[0].setCustomValidity(error);
            this.tooltip.text(error);            
        }
    }

    $("input[name=name]").on("input", (e) => {
        const length = new InputValidator($("input[name=name]"));
        length.addError("Введите название лодки", (val) => !val);
        length.addError("Слишком длинное название", (val) => val.length > 255);
        length.validate();
    })

    $("input[name=length]").on("input", (e) => {
        const length = new InputValidator($("input[name=length]"));
        length.addError("Укажите длину лодки", (val) => !val || val < 0.1);
        length.addError("Слишком длинная лодка", (val) => val > 999.9);
        length.validate();
    })

    $("input[name=width]").on("input", () => {
        const length = new InputValidator($("input[name=width]"));
        length.addError("Укажите ширину лодки", (val) => !val || val < 0.1);
        length.addError("Слишком широкая лодка", (val) => val > 99.9);
        length.validate();
    })

    $("input[name=draft]").on("input", () => {
        const length = new InputValidator($("input[name=draft]"));
        length.addError("Укажите осадку лодки", (val) => !val || val < 0.1);
        length.addError("Слишком большая осадка", (val) => val > 9.9);
        length.validate();
    })

    $("input[name=capacity]").on("input", () => {
        const length = new InputValidator($("input[name=capacity]"));
        length.addError("Укажите вместимость лодки", (val) => !val || val == 0);
        length.addError("Слишком большая вместимость лодки", (val) => val > 99);
        length.validate();
    })*/

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
            console.log(src);  
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
            console.log(error);
            hideOverlayPanel();
            showErrorToast((error.responseJSON.message || error.data));
        }
    })

})