// import { CreateCanvas, Game, drawBall, drawPaddle, drawScores } from './PongFunctions.js'

let socket = null;
let isKeyDown = false;
let keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
let keys_input = {ArrowUp: false, ArrowDown: false, ArrowLeft: false, ArrowRight: false};
let lastGameState = null;
let currentGameState = null;
let lastUpdateTime = performance.now();

document.body.addEventListener('click', async function(event) {
	if (event.target){
		if (event.target.matches('button.match')){
			const ret = await authANDupdateUI();
			if (ret)
				await socketConnexion(`matchmaking/${event.target.id}`);
		}
	}
});

function game(data_json) {
	document.querySelector("div.card-header").hidden = true
	document.removeEventListener("click", handleQuit);
	setPong(data_json['constant']);
}
function start(data_json) {
	document.addEventListener("keydown", handleKeyDown);
	document.addEventListener("keyup", handleKeyUp);
	document.addEventListener("click", give_up);
}
async function end(data_json) {
	document.querySelector("div.card-header").hidden = false
	document.removeEventListener("click", give_up);
	document.removeEventListener("keydown", handleKeyDown);
	document.removeEventListener("keyup", handleKeyUp);
	let highscore = -1;
	let winner = null;
	Object.entries(data_json['result']).forEach(([key, value]) => {
				if (value > highscore){
			highscore = value;
			winner = key;
		}
	});
	if (!data_json['users'])
		alertNonModal(`Partie finie. Resultat :${data_json['result']}`);
	else
		alertNonModal(`Partie finie. Resultat :${data_json['users'][winner]} Won!!!`);
	window.history.pushState({}, "", '/home');
	await updateContent();
	// fetchBody();
}
function countdown(data_json) {
	if (!data_json.time)
		return;
	Game.ctx.fillStyle = "#401010";
	Game.ctx.fillRect(0, 0, Game.canvas.width, Game.canvas.height);
	drawMidLine();
	if (Game.players == 4)
		drawMidLineHor()
	for (let i = 0; i < Game.players; i++){
		switch(i){
			case 0:
				drawPaddle(1, Game.canvas.height / 2 - 50, 1);
				break;
			case 1:
				drawPaddle(Game.canvas.width - 10, Game.canvas.height / 2 - 50, 1);
				break;
			case 2:
				drawPaddle(Game.canvas.width / 2 - 50, 1, 0);
				break;
			case 3:	
				drawPaddle(Game.canvas.width / 2 - 50, Game.canvas.height - 10, 0);
				break;
		}
	}
	drawBall(Game.canvas.width / 2 - 10, Game.canvas.height / 2 - 10);
	drawCount(data_json.time, Game.canvas.width / 2, Game.canvas.height / 2, 64);
}
function drawCount(time, x, y, size){
	Game.ctx.font = `${size}px 'Press Start 2P', monospace`;
	Game.ctx.fillStyle = "#404040";
	Game.ctx.textAlign = "center";
	Game.ctx.textBaseline = "middle"; 
	Game.ctx.fillStyle = "#404040";
	Game.ctx.fillText(time, x, y);
	Game.ctx.strokeStyle = "white";
	Game.ctx.lineWidth = 2;
	Game.ctx.strokeText(time, x, y);
}

function data(data_json) {
	currentGameState = data_json['pong'];
	lastGameState = currentGameState;
	lastUpdateTime = performance.now();
	requestAnimationFrame(renderPong);
}
async function temporary_end(data_json) {
	document.removeEventListener("click", give_up);
	document.removeEventListener("keydown", handleKeyDown);
	document.removeEventListener("keyup", handleKeyUp);
	alertNonModal(`Partie finie. Resultat : ${data_json['result']}`);
	window.history.pushState({}, "", '/waiting_room');
	if (window.location.pathname == "/waiting_room"){
		document.addEventListener("click", give_up2);
	}
	// await updateContent();
	fetchBody();
}
async function waiting_room(data_json) {
	document.querySelector("div.card-header").hidden = true
	window.history.pushState({}, "", '/waiting_room');
	await updateContent();
	// fetchBody();
}

const actions = {
	'game':game,
	'start':start,
	'end': end,
	'countdown':countdown,
	'data':data,
	'temporary_end': temporary_end,
	'waiting_room': waiting_room,
}

async function socketConnexion(path) {
	socket = new WebSocket(`wss://` + window.location.host + `/ws/${path}/`);
	socket.onopen = () => {
		window.addEventListener('beforeunload', handleUnload)
		document.addEventListener("click", handleQuit);
	};
	socket.onmessage = (e) => {
		const data_json = JSON.parse(e.data)['event'];
		const key = data_json['event']
		if (key && actions[key])
			actions[key](data_json)
	};
	socket.onclose = () => {
		document.removeEventListener("click", handleQuit);
		window.removeEventListener("beforeunload", handleUnload);
	};
}



async function authANDupdateUI() {
	const connect = await auth();
	if (!connect){
		window.history.pushState({}, "", '/login');
		await updateContent();
		alertNonModal('You have to be logged in to access this resource.');
		return false;
	}
	document.querySelectorAll('div.ui').forEach(element => {
		element.hidden = !element.hidden;
	});
	return true;
}
function give_up(event){
	if (event.target && event.target.matches('button.give_up')){
		socket.send(JSON.stringify({type: 'give_up'}));
	}
}
function handleQuit(event){
	if (event.target && event.target.matches('button.close')){
		socket.send(JSON.stringify({type: 'quit'}));
		document.querySelectorAll('div.ui').forEach(element => {
			element.hidden = !element.hidden;
		});
	}
}
function handleUnload(event) {
	socket.send(JSON.stringify({type: 'quit'}));
}

function handleKeyDown(event) {
	if (keys.includes(event.key) && !keys_input[event.key]){
		socket.send(JSON.stringify({type: 'input', bool: event.type, key: event.key}));
		keys_input[event.key] = true;
	}
}
function handleKeyUp(event) {
	if (keys.includes(event.key)) {
		socket.send(JSON.stringify({type: 'input', bool: event.type, key: event.key}));
		keys_input[event.key] = false;
	}
}
