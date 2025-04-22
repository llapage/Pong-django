
async function fetchOnlinePlayers() {
    const response = await fetch('api/social/getOnlinePlayers/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // // console.error('Error fetching online players');
        return ;
    }
    const data = await response.json();
    return data;
}

async function fetchOnlineStrangers() {
    const response = await fetch('api/social/getOnlineStrangers/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // // console.error('Error fetching online players');
        return ;
    }
    const data = await response.json();
    return data;
}

async function fetchOnlineFriends() {
    const response = await fetch('api/social/getOnlineFriends/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // // console.error('Error fetching online friends');
        return ;
    }
    const data = await response.json();
    return data;
} 


async function fetchFriends() {
    const response = await fetch('api/social/getFriends/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // // console.error('Error fetching friends');
        return ;
    }
    const data = await response.json();
    return data;
} 


async function fetchBlockedUsers() {
    const response = await fetch('api/social/getBlockedUsers/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    if (!response.ok) {
        // // console.error('Error fetching blocked users');
        return ;
    }
    const data = await response.json();
    return data;
} 
