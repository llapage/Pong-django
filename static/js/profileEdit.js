//Avoid redeclaration by checking if already defined in global scope
if (!window.user_modifiables) {
    //django/userManagementApp/views.py
    //static/html/profile.html
    window.user_modifiables = ["username", "email", "nickname", "password", "password confirmation"];
    window.user_constants = ["id", "wins", "losses", "ratio"];
    window.user_variables = [...window.user_modifiables, ...window.user_constants];
}

var img_delete_request = false;
var img_upload_request = false;
var selectedImageFile = null;

document.querySelector("button.switchDisplay").addEventListener("click", switchDisplay);
document.querySelector("button.switchEdit").addEventListener("click", switchToEdit);
document.querySelector("button.save").addEventListener("click", saveProfile)

document.querySelector("input.uploadProfilePic").addEventListener("change", preUpload);
document.querySelector("button.deleteProfilePic").addEventListener("click", preDelete);

function switchToEdit() {
    setFormFields();
    switchDisplay();
}

function switchDisplay() {
    document.getElementById('profile-display').hidden = !document.getElementById('profile-display').closest(".row.g-2").hidden;
    document.getElementById('profile-edit').hidden = !document.getElementById('profile-edit').hidden;
    document.getElementById('profile-edit-btn').hidden = !document.getElementById('profile-edit').hidden;
    document.getElementById('profilePicInput').value='';
    selectedImageFile = null;
    if (img_delete_request || img_upload_request)
        setProfilePic(document.getElementById('id').innerHTML);
    img_delete_request = false;
    img_upload_request = false;
}

function setFormFields() {
    let displayElems = document.getElementsByClassName('display');
    let formFields =  document.getElementsByClassName('form-control');
    for (const key of user_modifiables) {
        let dispElem = displayElems.namedItem(key);
        let formField = formFields.namedItem(key);
        if (dispElem && formField) {
            formField.value = dispElem.textContent
            removeFormErrorStyle(formField);
        }
    }
}

async function saveProfile() {
    if (img_upload_request) {
        await uploadProfilePic();
    }
    else if (img_delete_request) {
        await deleteProfilePic();
    }
    //dynamic json of modified data
    let updatedData = {};
    let formFields = document.getElementsByClassName('form-control');
    let displayElems = document.getElementsByClassName('display');
    for (const key of user_modifiables) {
        let formField = formFields.namedItem(key);
        let dispElem = displayElems.namedItem(key);
        if ((formField && !dispElem && formField.value != "")
            || (formField && dispElem && formField.value != dispElem.textContent)) {
            updatedData[key] = formField.value;
        }
    }
    const response = await fetch('/api/user/profileUpdate/', {
        method: 'POST',
        headers:  {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(updatedData),
    });
    const data = await response.json();
    if (response.status == 200) {
        if (updatedData['password'] != undefined) {
            window.location.href = response.url;
            updateContent();
            return;
        }
        updateHtml(data);
        switchDisplay();
    } else {
        formErrorStyle(data);
    }
}

async function deleteProfilePic() {
    img_delete_request = false;
    const response = await fetch('/api/user/setProfilePic/', {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        },
    });
    if (!response.ok) {
        // console.error('Error deleting profile picture');
        return;
    }
    // setDefaultPic();
}

async function uploadProfilePic() {
    img_upload_request = false;

    if (!selectedImageFile) return;

    const formData = new FormData();
    formData.append('image', selectedImageFile);
    
    const response = await fetch('/api/user/setProfilePic/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        },
        body: formData
    });
    if (!response.ok) {
        // console.error('Error uploading profile picture');
        document.getElementById('profilePic').src = '/media/profile_pictures/default_cute.png';
        return;
    }
    const data = await response.json();
    document.getElementById('profilePic').src = data.profile_picture_url;
    selectedImageFile = null;
}

function preUpload() {
    var preview = document.getElementById('profilePic');
    var file    = document.getElementById('profilePicInput').files[0];
    if (file) {
        selectedImageFile = file;
        file_type = file.name.split('.');
        file_type = file_type[file_type.length - 1];
        if (file_type != "gif" && file_type != "jpg" && file_type != "jpeg" && file_type != "png") {
            let hlp = document.getElementById('imgHelpBlock');
            hlp.classList.add('image-type-info')
            return ;
        }
        var reader  = new FileReader();
        reader.onloadend = function () {
          preview.src = reader.result;
        }
        reader.readAsDataURL(file);
        img_upload_request = true;
        img_delete_request = false;
    } else {
        // If dialog was canceled, keep any previously selected file
        if (selectedImageFile) {
            // Re-create the FileList with the previously selected file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(selectedImageFile);
            fileInput.files = dataTransfer.files;
        }
    }
}

function setDefaultPic() {
    document.getElementById('profilePic').src = "/media/profile_pictures/default_cute.png";
}

function preDelete() {
    img_delete_request = true;
    img_upload_request = false;
    setDefaultPic();
}

async function insertFriendRows() {
    const friends = await fetchFriends();
    const onlineFriends = await fetchOnlineFriends();

    let containerHTML = `
    <div class='row header mb-2'>
        <p class="mb-0">Friends</p>
    </div>
    <div class="overflow-auto bg-light rounded p-2 mb-4" style="max-height: 400px;">
        <div id="friendsListContent">
            <!-- Friends cards will be inserted here -->
        </div>
    </div>`;

    let listHTML = ""
    let i = 0;
    for (const userId of Object.keys(await friends)) {
        let statusBadge = await onlineFriends[userId]
            ? '<span class="badge bg-success ms-2">Online</span>'
            : '<span class="badge bg-secondary ms-2">Offline</span>';
        let row = `
        <div class="row friend-row g-1 mb-2 p-2 border-bottom" data-user-id="${userId}" data-user-name="${friends[userId]}">
            <div class="col-7 d-flex align-items-center">
                <a href="/profile/${userId}">
                    Player ${userId}#${friends[userId]}
                </a>
                ${statusBadge}
            </div>
             <div class="col-md-5 d-flex align-items-center gap-1">
                <button class="btn btn-sm btn-outline-primary remove-friend">Remove friend</button>
                <button class="btn btn-sm btn-outline-secondary btn-outline-danger block-friend">Block user</button>
            </div>
        </div>`
        listHTML += row;
        i++;
    }
    document.querySelector(`div#profileFriendsList`).innerHTML = containerHTML;
    if (i) {
        document.querySelector(`div#friendsListContent`).innerHTML = listHTML;
        document.querySelector('div#profileFriendsList').addEventListener('click', async (event) => {
            const row = event.target.closest('.friend-row');
            if (!row) return;
            const userId = row.getAttribute('data-user-id');
            const userName = row.getAttribute('data-user-name');
            
            if (event.target.matches('.remove-friend')) {
                const confirmRemove = confirm(`Remove friend ${userId}?`);
                if (confirmRemove) {
                    let response = await removeFriend(userId);
                    if (await response == 200) {
                        row.remove();
                    }
                }
            }
            if (event.target.matches('.block-friend')) {
                const confirmRemove = confirm(`Block friend ${userId}?`);
                if (confirmRemove) {
                    let response = await blockUser(userId);
                    if (await response == 200) {
                        row.remove();
                    }
                }
            }
            if (document.querySelectorAll('.friend-row').length === 0) {
                document.getElementById('friendsListContent').innerHTML = '<div class="text-center py-3">No friends added yet.</div>';
            }
        });
    } else {
        document.getElementById('friendsListContent').innerHTML = '<div class="text-center py-3">No friends added yet.</div>';
    }
}

//TEMPORARY?
async function insertBlockedUserRows() {
    const foes = await fetchBlockedUsers();

    let containerHTML = `
    <div class='row header mb-2'>
        <p class="mb-0">Blocked users</p>
    </div>
    <div class="overflow-auto bg-light rounded p-2 mb-4" style="max-height: 400px;">
        <div id="blockedListContent">
            <!-- Blocked cards will be inserted here -->
        </div>
    </div>`;


    let listHTML = ""
    let i = 0;
    for (const userId of Object.keys(await foes)) {
        let row = `
        <div class="row blocked-user-row g-1" data-user-id="${userId}" data-user-name="${foes[userId]}">
            <div class="col-6 d-flex align-items-center">
                <a href="/profile/${userId}">
                    Player ${userId}#${foes[userId]}
                </a>
            </div>
             <div class="col d-flex align-items-center">
                <button class="btn btn-outline-secondary btn-outline-danger unblock-user">Unblock 🐦‍🔥</button>
            </div>
        </div>`
        listHTML += row;
        i++;
    }
    document.querySelector(`div#blockedUsersList`).innerHTML = containerHTML;
    document.querySelector(`div#blockedListContent`).innerHTML = listHTML;
    if (i) {
    
        document.querySelector('div#blockedUsersList').addEventListener('click', async (event) => {
            const row = event.target.closest('.blocked-user-row');
            const userId = row.dataset.userId;
            const userName = row.dataset.userName;
    
            if (event.target.matches('.unblock-user')) {
                const confirmRemove = confirm(`Unblock user ${userId}?`);
                if (confirmRemove) {
                    let response = await unblockUser(userId);
                    if (await response == 200) {
                        row.remove();
                    }
                    // else
                    //     console.log(`Failed to unblock user ${userId}`);
                }
            }
            if (document.querySelectorAll('.blocked-user-row').length === 0) {
                document.getElementById('blockedListContent').innerHTML = '<div class="text-center py-3">No blocked users yet.</div>';
            }
        });
    } else {
        document.getElementById('blockedListContent').innerHTML = '<div class="text-center py-3">No blocked users yet.</div>';
    }
}


async function loadPersonalProfile() {
    insertFriendRequests();
    insertFriendRows();
    insertBlockedUserRows();
}

loadPersonalProfile();
