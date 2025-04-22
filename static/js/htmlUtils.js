
// loginButton triggered on "Enter" keypress
document.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        const loginButton = document.querySelector("button.connexion");
        if (loginButton && document.body.contains(loginButton)) {
            event.preventDefault();
            loginButton.click();
        }
    }
});

document.addEventListener("input", function (event) {
    let formField = event.target.closest(".form-control"); if (!formField) return;
    removeFormErrorStyle(formField);
});

function removeFormErrorStyle(formField) {
    formField.classList.remove('input-error');
    let errMsgObj = formField.closest('label').querySelector('.form-error-msg'); if (!errMsgObj) return;
    errMsgObj.style.display = "none"
}