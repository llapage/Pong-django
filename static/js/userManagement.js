/* HTML EVENT MANAGEMENT */
document.body.addEventListener('click', function(event) {
	if (event.target && event.target.matches('button.connexion')) {
		connexion(event.target.dataset.path);
	}
	if (event.target && event.target.matches('button.logout'))
		logout();
});

// create dic obj to match status code to function.
const connexionStatusHandlers = {
    200: () => { /* Handle success */ 
		window.history.pushState({}, "", '/home');
		// await updateContent();
		fetchBody();
	},
    202: (errorData) => {
		formErrorStyle(errorData);
	}, 
    500: () => { /* Handle server error */
		alertNonModal('Server error.');
	},
};

async function connexion(path) {
	let formFields = getFormFields();
	// console.log(`https://` + window.location.host + `${path}`);
	const response = await fetch(`https://` + window.location.host + `${path}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCsrfToken(),
		},
		body: JSON.stringify(formFields),
	});
	let responseData = await response.json();
	const handler = connexionStatusHandlers[response.status];
	if (handler)
    	handler(responseData);
	// else
	// 	console.log(`Unexpected status: ${response.status}`);
}

async function logout(){
	const response = await fetch('https://' + window.location.host + '/api/user/log_out/');
	window.history.pushState({}, "", '/');
	await updateContent();
	// fetchBody();
}

function getCsrfToken() {
    let csrfToken = document.cookie.match(/csrftoken=([\w-]+)/);
    return csrfToken ? csrfToken[1] : null;
}
function getFormFields() {
	var formData = new FormData(document.querySelector('form'));
	let obj = {};
	formData.forEach((value, key) => {
		obj[key] = value;
	})
	return obj;
}

function formErrorStyle(errorData) {
    let formFields = document.getElementsByClassName('form-control');
	for (const error in errorData) {
        let formField = formFields.namedItem(error); if (!formField) continue;
		let errMsgObj = formField.closest('label').querySelector('.form-error-msg'); if (!errMsgObj) continue;
		formField.classList.add('input-error');
		errMsgObj.textContent = errorData[error];
        errMsgObj.style.display = "block"
    }
}
