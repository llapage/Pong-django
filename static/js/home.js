async function insertPlayerRows() {
	const data = await fetchOnlineStrangers();
	let containerHTML = `
		<div class='col header mb-2'>
			<p class="mb-0">Other online users</p>
		</div>
		<div class="row overflow-auto bg-light rounded mb-4" style="max-height: 400px;">
			<div id="onlineUsersRows">
				<!-- Friends cards will be inserted here -->
			</div>
		</div>`;
	let listHTML = ""
	let i = 0;
	for (const userId of Object.keys(data)) {
		let row = `<div class="row player">
			<div class="row d-flex justify-content-left g-1 mb-2 text-start">
				<a href="/profile/${userId}">
					Player ${userId}#${data[userId]}
					<span class='badge bg-success ms-2'>Online</span>
				</a>
			</div>
			</div>`
		listHTML += row;
		i++;
	}
	document.querySelector("div#onlineUsersList").innerHTML = containerHTML;
	if (i) {
		document.querySelector("div#onlineUsersRows").innerHTML = listHTML
	} else {
		document.querySelector("div#onlineUsersRows").innerHTML = '<div class="text-center py-3">No other online players.</div>'
	}

}

async function insertFriendRows() {
	const friends = await fetchFriends();
	const onlineFriends = await fetchOnlineFriends();
	let containerHTML = `
		<div class='col header mb-2'>
			<p class="mb-0">Friends</p>
		</div>
		<div class="row overflow-auto bg-light rounded mb-4" style="max-height: 400px;">
			<div id="homeFriendsRows">
				<!-- Friends cards will be inserted here -->
			</div>
		</div>`;
	let listHTML = ""
	let i = 0;
	for (const userId of Object.keys(friends)) {
		let statusBadge = await onlineFriends[userId]
			? '<span class="badge bg-success ms-2">Online</span>'
			: '<span class="badge bg-secondary ms-2">Offline</span>';
		let row = `
		<div class="row player friend">
			<div class="col-8 d-flex align-items-center">
				<a href="/profile/${userId}">
					Player ${userId}#${friends[userId]}
				</a>
				${statusBadge}
			</div>
			<div class="col-4 d-flex align-items-center">
			<button class="btn btn-outline-secondary chat-btn" data-player-id="${userId}">Chat</button>
			</div>
			</div>`
			listHTML += row;
			i++;
	}
	document.querySelector("div#friendsList").innerHTML = containerHTML;
	if (i){
		document.querySelector("div#homeFriendsRows").innerHTML = listHTML
		const chatInviteButton = document.querySelectorAll('.chat-btn');
		chatInviteButton.forEach(button => {
			button.addEventListener('click', async (event) => {
				const userId = event.target.getAttribute('data-player-id');
				if (userId) {
					window.history.pushState({}, "", '/chat/' + userId);
					await updateContent();
					// await fetchBody();
				}
			});
		});
	}
	else
        document.querySelector("div#homeFriendsRows").innerHTML = '<div class="text-center py-3">No friends.</div>';
}

insertFriendRows();
insertPlayerRows();