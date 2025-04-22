const localData = {
	InitSpeed: [5, 5],
	keys: { w: false, s: false, ArrowUp: false, ArrowDown: false },
	paddles: null,
	scores: null,
	ball: null,
	vector: null,
	paddleSpeed: null,
	running: null,
	players: null,
	stop: null
}

//PONG SETUP
async function setLocalPong(p1, p2) {
	document.querySelector("div.card-header").hidden = true;
	window.history.pushState({}, '', '/pongLocal');
	const response = await fetch('/static/html/pongLocal.html');
	const html = await response.text();
	document.querySelector("div#app").innerHTML = html;
	Game.paddleSize = { width: 10, height: 100 };
	Game.ballRadius = 10;
	Game.players = 2;
	CreateCanvas(1000, 750);
	setLocalData();
	if (p1 && p2) {
		setNames([p1, p2]);
		localData.players = [p1, p2];
	}
	document.querySelector('button.start').innerText = "Start";
	document.addEventListener("click", startStopButton)
	document.addEventListener("keydown", (e) => {
		if (e.key in localData.keys)
			localData.keys[e.key] = true;
	});

	document.addEventListener("keyup", (e) => {
		if (e.key in localData.keys)
			localData.keys[e.key] = false;
	});
	return new Promise((resolve) => {
		renderPongLocal(resolve); // <-- pass resolver to loop
	});
}

async function startStopButton(event) {
	if (event.target && event.target.matches('button.start')) {
		if (document.querySelector('button.start').innerText == "Start") {
			localData.vector = [localData.InitSpeed[0], localData.InitSpeed[1]];
			document.querySelector('button.start').innerText = "Stop";
		}
		else {
			localData.running = false;
			localData.stop = true;
			window.history.pushState({}, "", '/home');
			await updateContent();
			// fetchBody();
		}
	}
}

function setLocalData() {
	localData.paddles = { "p1": [1, Game.canvas.height / 2 - 50], "p2": [Game.canvas.width - 11, Game.canvas.height / 2 - 50] }
	localData.scores = [0, 0];
	localData.ball = [Game.canvas.width / 2, Game.canvas.height / 2]
	localData.vector = [0, 0];
	localData.paddleSpeed = Math.sqrt((5 ** 2 + 5 ** 2) * 1.6)
	localData.running = true;
	localData.stop = false;
}

//PONG DISPLAY
function renderPongLocal(resolveGameEnd) {
	Game.ctx.fillStyle = "#401010";
	Game.ctx.fillRect(0, 0, Game.canvas.width, Game.canvas.height);
	drawMidLine();
	for (let i = 0; i < Game.players; i++) {
		drawPaddle(localData.paddles["p" + (i + 1)][0], localData.paddles["p" + (i + 1)][1], i < 2)
	}
	drawBall(localData.ball[0], localData.ball[1]);
	drawScoresL();
	moveBall();

	movePaddles();
	if (checkEndGame(resolveGameEnd)) {
		return;
	}
	if (!localData.running)
		return;
	requestAnimationFrame(() => renderPongLocal(resolveGameEnd));
}

function drawScoresL() {
	Game.ctx.font = "24px Arial";
	Game.ctx.fillStyle = "white";
	Game.ctx.fillText(localData.scores[0], Game.canvas.width / 4, 30);
	Game.ctx.fillText(localData.scores[1], (Game.canvas.width * 3) / 4, 30);
}

//PONG GAME LOGIC
function movePaddles() {
	paddleSpeed = localData.paddleSpeed;

	if (localData.keys.w)
		checkPadMove(localData.paddles["p1"][1], -1 * paddleSpeed, "p1");
	else if (localData.keys.s)
		checkPadMove(localData.paddles["p1"][1], paddleSpeed, "p1");
	if (localData.keys.ArrowUp)
		checkPadMove(localData.paddles["p2"][1], -1 * paddleSpeed, "p2");
	else if (localData.keys.ArrowDown)
		checkPadMove(localData.paddles["p2"][1], paddleSpeed, "p2");

}

function checkPadMove(pos, move, player) {
	if ((pos + move) >= 0 && pos + move + Game.paddleSize.height <= Game.canvas.height)
		localData.paddles[player][1] += move;
	else if ((pos + move) < 0)
		localData.paddles[player][1] = 0;
	else
		localData.paddles[player][1] = Game.canvas.height - Game.paddleSize.height;
}

function moveBall() {
	localData.ball[0] += localData.vector[0];
	localData.ball[1] += localData.vector[1];
	checkColl();
}

function checkColl() {
	let player = "p2";
	if (localData.vector[0] <= 0)
		player = "p1";
	if (localData.ball[1] + Game.ballRadius > Game.canvas.height || localData.ball[1] - Game.ballRadius < 0)
		wallCollision();

	if (localData.ball[0] + Game.ballRadius >= Game.canvas.width - Game.paddleSize.width
		|| localData.ball[0] - Game.ballRadius <= Game.paddleSize.width) {
		if (!paddleCollision(player))
			if (outOfBound())
				scoreAndResetBall();
	}
}

function wallCollision() {
	if (localData.ball[1] < Game.ballRadius || localData.ball[1] > Game.canvas.height - Game.ballRadius) {
		lim = Game.ballRadius;
		if (localData.ball[1] > Game.canvas.height - Game.ballRadius)
			lim = Game.canvas.height - Game.ballRadius;
		dif = lim - localData.ball[1];
		localData.ball[1] = lim + dif;
	}
	localData.vector[1] *= -1;
}

function paddleCollision(pp) {
	paddleHeight = Game.paddleSize.height;
	if (localData.ball[1] + Game.ballRadius < localData.paddles[pp][1] ||
		localData.ball[1] - Game.ballRadius > localData.paddles[pp][1] + Game.paddleSize.height)
		return false;
	adjustBallCollision(pp);
	paddleCenter = localData.paddles[pp][1] + paddleHeight / 2;
	hitPosition = localData.ball[1] - paddleCenter;
	maxBounceAngle = Math.PI / 4;
	bounceAngle = (hitPosition / (paddleHeight / 2)) * maxBounceAngle;
	speed = Math.sqrt(localData.vector[0] ** 2 + localData.vector[1] ** 2);
	colVerticalPaddle(pp, speed, bounceAngle);
	return true;
}

function colVerticalPaddle(pp, speed, bounceAngle) {
	localData.vector[0] = speed * Math.cos(bounceAngle);
	localData.vector[1] = speed * Math.sin(bounceAngle);
	increaseSpeed(pp);
	if (pp == "p1")
		localData.vector[0] = Math.abs(localData.vector[0]);
	else
		localData.vector[0] = -Math.abs(localData.vector[0]);
}

function adjustBallCollision(pp) {
	if (pp == "p1")
		localData.ball[0] = localData.paddles["p1"][0] + Game.paddleSize.width + Game.ballRadius
	else
		localData.ball[0] = localData.paddles["p2"][0] - Game.ballRadius
}

function outOfBound() {
	board = Game.canvas
	if (localData.ball[0] <= 0 || localData.ball[0] >= board.width - 0) {
		return true;
	}
	if (localData.ball[1] <= 0 || localData.ball[1] >= board.height - 0) {
		return true;
	}
	return false;
}

function increaseSpeed(pp) {
	if (pp == "p1" && (localData.keys.w || localData.keys.s))
		if (Math.sqrt(localData.vector[0] ** 2 + localData.vector[1] ** 2) < 25) {
			localData.vector[0] *= 1.1;
			localData.vector[1] *= 1.1;
		}
		else if (pp == "p2" && (localData.keys.ArrowUp || localData.keys.ArrowDown))
			if (Math.sqrt(localData.vector[0] ** 2 + localData.vector[1] ** 2) < 25) {
				localData.vector[0] *= 1.1;
				localData.vector[1] *= 1.1;
			}
}
function scoreAndResetBall() {
	localData.vector = [localData.InitSpeed[0], Math.random() * localData.InitSpeed[1]];
	if (Math.random() < 0.5)
		localData.vector[1] *= -1;
	if (Math.abs(localData.vector[1]) < 5)
		localData.vector[0] += (1 + Math.abs(localData.vector[1]) % 3)
	if (localData.ball[0] <= 0 || localData.ball[0] >= Game.canvas.width) {
		if (localData.ball[0] <= 0) {
			localData.scores[1]++;
		}
		else {
			localData.scores[0]++;
			localData.vector[0] *= -1;
		}
	}
	localData.ball = [Game.canvas.width / 2, Game.canvas.height / 2];
}
function checkEndGame(resolve) {
	const win = 11;
	if (((localData.scores[0] >= win || localData.scores[1] >= win) && Math.abs(localData.scores[0] - localData.scores[1]) > 1) || !localData.running) {
		localData.vector[0] = 0; localData.vector[1] = 0;
		if (localData.scores[0] >= win)
			alertNonModal(`${localData.players[0]} Won!`);
		else if (localData.scores[1] >= win)
			alertNonModal(`${localData.players[1]} Won!`);
		else
			alertNonModal("Game Interrupted!");
		if (resolve) {
			resolve();
		}
		return true;
	}
	return false;
}
