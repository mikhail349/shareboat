$(document).ready(() => {
    const forms = document.getElementsByClassName("needs-validation");
    Array.prototype.filter.call(forms, (form) => {
        form.addEventListener("submit", (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add("was-validated");
            },
            false
        );
    });
});