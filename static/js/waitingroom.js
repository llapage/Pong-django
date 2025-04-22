function give_up2(event){
	if (event.target && event.target.matches('button.give_up2')){
		socket.send(JSON.stringify({type: 'give_up'}));
		document.removeEventListener("click", give_up2);
	}
}
