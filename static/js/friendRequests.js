
async function insertFriendRequests() {
    const response = await fetch("api/social/inFriendRequests/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error fetching incoming friend requests');
        return ;
    }
    const data = await response.json();

    let html = "<div class='row header'><p>Friend requests</p></div>"
    let i = 0;
    for (const requestId of Object.keys(data)) {
        let reqObj = data[requestId]
        let row = `<div class="row request-row g-1" data-request-id="${requestId}" data-request-sender="${data[requestId]}">
            <div class="col-8">
                <a href="/profile/${reqObj['userId']}">
                    ${reqObj['username']}
                </a> sent you a friend request
            </div>
            <div class="col-4 d-flex align-items-center">
                <button class="btn btn-outline-primary accept-btn">Accept</button>
                <button class="btn btn-outline-secondary reject-btn">Reject</button>
            </div>
        </div>`
        html += row;
        i++;
    }
    if (i) {
        document.querySelector("div#friendRequests").innerHTML = html;
    
        document.querySelector('div#friendRequests').addEventListener('click', async (event) => {
            const row = event.target.closest('.request-row');
            const requestId = row.dataset.requestId;
            // const senderUsername = row.dataset.requestSender;
            
            if (event.target.matches('.accept-btn')) {
                let status = await acceptFriendRequest(requestId);
                if (status == 200) {
                    event.target.closest('.request-row').remove();
                }
            }
    
            if (event.target.matches('.reject-btn')) {
                let status = await rejectFriendRequest(requestId);
                if (status == 200) {
                    event.target.closest('.request-row').remove();
                }
            }
        })

    }
}

async function sendFriendRequest(to_user) {
    const response = await fetch(`/api/social/invite/${to_user}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    let data = await response.json();
    if (response.status != 200) {
        // console.error('Error sending friend request');
        return -1;
    }
    return data['request_id'];
}

async function acceptFriendRequest(requestId) {
    const response = await fetch(`/api/social/accept/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error accepting friend request');
    }
    return response.status;
}

async function rejectFriendRequest(requestId) {
    const response = await fetch(`/api/social/reject/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error rejecting friend request');
    }
    return response.status;
}

async function removeFriend(to_user) {
    const response = await fetch(`/api/social/remove/${to_user}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error removing friend');
    }
    return response.status;
}

async function blockUser(to_user) {
    const response = await fetch(`/api/social/block/${to_user}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error blocking user');
    }
    return response.status;
}

async function unblockUser(to_user) {
    const response = await fetch(`/api/social/unblock/${to_user}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // console.error('Error unblocking user');
    }
    return response.status;
}