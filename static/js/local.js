

async function match(p1, p2){
	await setLocalPong(p1, p2);
	document.querySelector("div.card-header").hidden = false;
	if (localData.scores[0] < localData.scores[1])
		p1 = p2;
	return (p1);
}

async function tournament_manager(users){
	while (users.length > 1){
		winners = [];
		for (let i = users.length; i > 0; i -= 2){
			await winners.push(await match(users.pop(), users.pop()));
			if (localData.stop)
				break;
		}
		users = winners;
	}
	window.history.pushState({}, "", '/home');
	await updateContent();
	// await fetchBody();
}

document.querySelector('button#Playername-Submit').onclick = function(e) {
	e.preventDefault();

	const form = document.querySelector('form#playerForm');
	const formDataArray = Array.from(new FormData(form));
	const valuesArray = formDataArray.map(([key, value]) => value);
	const playerValues = valuesArray.map(value => value.trim());

	const uniqueValues = new Set(playerValues);

    if (playerValues.includes(""))
		alertNonModal('Tous les champs doivent être remplis !');
    else if (uniqueValues.size !== playerValues.length)
        alertNonModal("Les noms doivent être uniques !");
    else
        tournament_manager(playerValues);
};
