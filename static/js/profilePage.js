//Avoid redeclaration by checking if already defined in global scope
if (!window.user_modifiables) {
    //django/userManagementApp/views.py
    //static/html/profile.html
    window.user_modifiables = ["username", "email", "nickname", "password", "password confirmation"];
    window.user_constants = ["id", "wins", "losses", "ratio"];
    window.user_variables = [...window.user_modifiables, ...window.user_constants];
}

function updateHtml(data) {
    let displayElems = document.getElementsByClassName('display');
    for (const key of user_variables) {
        let dispElem = displayElems.namedItem(key);
        if (dispElem) {dispElem.textContent = data[key] ? data[key] : dispElem.textContent;}
    }
}

async function fetchProfile() {
    var url = Object.keys(window.routeParams).length ?
        `/api/user/profile/${window.routeParams.userId.toString()}/`
        : '/api/user/profile/';
    const response = await fetch(url);
    if (!response.ok) {
        return -1;
    }
    const data = await response.json();
    updateHtml(data);
    if (data && data.id)
        setProfilePic(data.id);
    return 0;
}

async function fetchProfilePicUrl(userId) {
    const response = await fetch(`/api/user/getProfilePic/${userId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'Cache-Control': 'no-store'
        }
    });
    return response;
}

async function setProfilePic(userId) {
    const response = await fetchProfilePicUrl(userId);
    if (response.ok) {
        const data = await response.json();
        img = document.getElementById('profilePic')
        if (data.profile_picture_url != null) {
            img.src = data.profile_picture_url;
        }
        else {
            img.src = '/media/profile_pictures/default_cute.png'
        }
    }
}

async function fetchGames(targetUserId) {
    let url = targetUserId == undefined ? "/api/gameStats/getGames/" : `/api/gameStats/getGames/${targetUserId.toString()}/`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error(response);
        // console.error('Error fetching game stats');
        return;
    }
    const data = await response.json();
    return data;
}

async function saveFakeGame() { //dbg
    const response = await fetch('api/gameStats/saveFakeGame/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error faking it');
        return;
    }
    const data = await response.json();
    return data;
}

async function insertGameHistoryRows() {
    const urlId = window.routeParams.userId;
    const htmlID = document.getElementById('id');
    const data = await fetchGames(urlId);
    if (data['warning'] != undefined)
        return;
    let profile_id = urlId == undefined ? htmlID ? htmlID.innerHTML : -1 : urlId.toString();

    let containerHTML = `
    <div class='row header mb-2'>
        <p class="mb-0">Games History</p>
    </div>
    <div class="overflow-auto bg-light rounded p-2 mb-4" style="max-height: 400px;">
        <div id="gameHistoryContent">
            <!-- Game cards will be inserted here -->
        </div>
    </div>`;

    document.querySelector("div#gameHistoryList").innerHTML = containerHTML;

    //turn json to array of gameObj, gameId becoming a parameter
    let gameEntries = Object.entries(data).map(([gameId, gameObj]) => {
        return { gameId, ...gameObj };
    });
    gameEntries.sort((a, b) => {
    const idA = parseInt(a.gameId);
    const idB = parseInt(b.gameId);
    return idB - idA;
    });
      
      
    let historyHTML = "";
    for (const gameEntry of gameEntries) {
    const gameObj = gameEntry;
    let requester_id = gameObj.request;
    let vs_list = [];
    let score = [];
    for (let p of gameObj.players) {
        if (p.id != requester_id) {
            vs_list.push(`<a href="/profile/${p.id}">${p.nickname}</a>`);
            score.push(p.score != -1 ? p.score.toString() : "deserted");
        }
        else { //if p.id == id
            vs_list.push(`<b>YOU</b>`);
            score.push(`<b>${p.score != -1 ? p.score.toString() : "deserted"}</b>`);
        }
    }
    let win_loss_badge = gameObj.winner == profile_id
        ? '<span class="badge bg-success">WIN</span>'
        : '<span class="badge bg-secondary">LOSS</span>'
    let row = `
    <div class="col mb-2">
        <div class="card stats-card ${gameObj.winner == profile_id ? 'win' : 'loss'}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="card-title">${vs_list.join(' vs')}</h5>
                    ${win_loss_badge}
                </div>
                <p class="card-text">${gameObj.datetime} • ${gameObj.game_type}</p>
                <div class="d-flex justify-content-between">
                    <small class="text-muted">Score: ${score.join('-')}</small>
                </div>
            </div>
        </div>
    </div>`
    historyHTML += row;
    }
    document.querySelector("div#gameHistoryContent").innerHTML = historyHTML;
}


async function insertSocialButton() {
    let userId = window.routeParams.userId
    if (userId == undefined || userId == 1 || userId == 2) //if we're looking at our own profile or AI or SU
        return ;
    userId = userId.toString();
    const response = await fetch(`/api/social/socialStatus/${userId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    });
    if (!response.ok)
        return ;
    const data = await response.json();
    document.querySelector("div#social_buttons").innerHTML = `<div class="col d-flex align-items-center p-3 border">
                <button class="btn btn-outline-primary friend"></button>
                <button class="btn btn-outline-secondary btn-outline-danger foe"></button>
            </div>`;
    const friend_btn = document.querySelector("div#social_buttons").getElementsByClassName('friend')[0];
    const foe_btn = document.querySelector("div#social_buttons").getElementsByClassName('foe')[0];
    if (data['is_blocked'] == true) {
        foe_btn.innerHTML =  "Unblock user";
        foe_btn.classList.add('unblock-user');
        friend_btn.style.display='None';
    } else {
        foe_btn.innerHTML =  "Block user";
        foe_btn.classList.add('block-user');
        friend_btn.style.display='';
    }
    if (data['blocked_me'] == true) {
        friend_btn.style.display='None';
    } else if (data['is_friend'] == true) {
        friend_btn.innerHTML =  "Remove friend";
        friend_btn.classList.add('remove-friend');
    } else if (data['is_inviting'] != -1) {
        friend_btn.innerHTML = "Accept friend request";
        friend_btn.classList.add('accept-invite');
        foe_btn.innerHTML = "Reject invite";
        foe_btn.classList.remove('block-user')
        foe_btn.classList.add('remove-in-request');
    } else if (data['was_invited'] != -1) {
        friend_btn.innerHTML = "Cancel friend invite";
        friend_btn.classList.add('remove-out-request');
    } else {
        friend_btn.innerHTML =  "Send friend request";
        friend_btn.classList.add('friend-invite');
    }
    let sent_invite_id = -1;
    document.querySelector('div#social_buttons').addEventListener('click', async (event) => {
        if (event.target.matches('.friend-invite')) {
            sent_invite_id = await sendFriendRequest(userId);
            if (sent_invite_id != -1) {
                friend_btn.innerHTML = "Cancel friend invite";
                friend_btn.classList.remove('friend-invite');
                friend_btn.classList.add('remove-out-request');
            } else {
                insertSocialButton();
            }
        }
        else if (event.target.matches('.remove-out-request')) {
            if (sent_invite_id != -1 || data['was_invited'] != -1) {
                let response = await rejectFriendRequest(sent_invite_id == -1 ? data['was_invited'] : sent_invite_id);
                if (response == 200) {
                    friend_btn.innerHTML = 'Send friend request';
                    friend_btn.classList.remove('remove-out-invite');
                    friend_btn.classList.add('friend-invite');
                } else {
                    insertSocialButton();
                }
            }
        }
        else if (event.target.matches('.accept-invite')) {
            let response = await acceptFriendRequest(data['is_inviting']);
            if (response == 200) {
                friend_btn.innerHTML = 'Remove friend';
                friend_btn.classList.remove('accept-invite');
                friend_btn.classList.add('remove-friend');
                foe_btn.innerHTML = 'Block user';
                foe_btn.classList.remove('remove-in-request');
                foe_btn.classList.add('block-user');
            } else {
                insertSocialButton();
            }
        }
        else if (event.target.matches('.remove-in-request')) {
            let response = await rejectFriendRequest(data['is_inviting']);
            if (response == 200) {
                friend_btn.innerHTML = 'Send friend request';
                friend_btn.classList.remove('accept-invite');
                friend_btn.classList.add('friend-invite');
                foe_btn.innerHTML = 'Block user';
                foe_btn.classList.remove('remove-in-request');
                foe_btn.classList.add('block-user');
            } else {
                insertSocialButton();
            }
        }
        else if (event.target.matches('.remove-friend')) {
            const confirmRemove = confirm(`Remove user from your friends list?`);
            if (confirmRemove) {
                let response = await removeFriend(userId);
                if (response == 200) {
                    friend_btn.classList.remove('remove-friend');
                    friend_btn.classList.add('friend-invite');
                    friend_btn.innerHTML = 'Send friend request';
                } else {
                    insertSocialButton();
                }
            }
        }
        else if (event.target.matches('.unblock-user')) {
            const confirmRemove = confirm(`Unblock user?`);
            if (confirmRemove) {
                let response = await unblockUser(userId);
                if (response == 200) {
                    foe_btn.classList.remove('unblock-user');
                    foe_btn.classList.add('block-user');
                    foe_btn.innerHTML = 'block user';
                    friend_btn.classList.add('friend-invite')
                    friend_btn.innerHTML='Send friend request';
                    if (data["blocked_me"] == false) {
                        friend_btn.style.display='';
                    }
                } else {
                    insertSocialButton();
                }
            }
        }
        else if (event.target.matches('.block-user')) {
            const confirmRemove = confirm(`Block user?`);
            if (confirmRemove) {
                let response = await blockUser(userId);
                if (response == 200) {
                    foe_btn.classList.remove('block-user');
                    foe_btn.classList.add('unblock-user');
                    foe_btn.innerHTML = 'unblock user';
                    friend_btn.style.display='None';
                    friend_btn.classList.remove('remove-friend');
                    friend_btn.classList.remove('friend-invite');
                    friend_btn.classList.remove('remove-out-request');
                    friend_btn.classList.remove('accept-invite');
                } else {
                    insertSocialButton();
                }
            }
        }
    });
}

async function loadPage() {
    if (await fetchProfile() == 0) {
        insertSocialButton();
        insertGameHistoryRows();
    } else {
        window.location.href = "/home";
        await updateContent();
        
    }
}

loadPage();
