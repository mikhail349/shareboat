function _onFormSubmit(event, form) {
    if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
    }

    form.classList.add('was-validated')
}

function activateFormValidation(form) {
    form.addEventListener('submit', (event) => _onFormSubmit(event, form), false)    
}

function deactivateFormValidation(form) {
    form.removeEventListener('submit', (event) => _onFormSubmit(event, form), false)
}