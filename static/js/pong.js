const Game = {
	canvas: null,
	ctx: null,
	paddleSize: null,
	ballRadius: null,
	players: null,
}

// GAME LOGIC //
function drawPaddle(x, y, vert) {
	let width;
	let height;
	if (vert){
		width = Game.paddleSize.width
		height = Game.paddleSize.height
	}
	else{
		width = Game.paddleSize.height
		height = Game.paddleSize.width
	}
	Game.ctx.fillStyle = "white";
	Game.ctx.fillRect(x, y, width, height);
	Game.ctx.strokeStyle = "#F1E0F0";
	Game.ctx.lineWidth = 1;
	Game.ctx.strokeRect(x, y, width, height); // Draw the border
}

function drawWall(player) {
	let start;
	let size;
	switch (player){
		case 0:
			start = [0,0];
			size = [5, Game.canvas.height];
			break;
		case 1:
			start = [Game.canvas.width - 10, 0];
			size = [5, Game.canvas.height]
			break;
		case 2:
			start = [0,0];
			size = [Game.canvas.width, 5];
			break;
		case 3:
			start = [0, Game.canvas.height - 10];
			size = [Game.canvas.width, 5];
			break;
		}
	Game.ctx.fillStyle = "white";
	Game.ctx.fillRect(start[0], start[1], size[0], size[1]);
	Game.ctx.strokeStyle = "red";
	Game.ctx.lineWidth = 1;
	Game.ctx.strokeRect(start[0], start[1], size[0], size[1]); // Draw the border
}

// Draw Ball
function drawBall(x, y) {
	Game.ctx.beginPath();
	Game.ctx.arc(x, y, Game.ballRadius, 0, Math.PI * 2);
	Game.ctx.fillStyle = "white";
	Game.ctx.fill();
	Game.ctx.closePath();
}

// Draw Scores
function drawScores(scores, playerNbr) {
	for (let i = 0; i < playerNbr; i++){
		if (document.getElementById("score-" + (i + 1)))
			document.getElementById("score-" + (i + 1)).innerText = scores[i];
	}
}

// GAME FRONT DESIGN //
function CreateCanvas(width, height) {
	Game.canvas = document.querySelector("canvas#pong");
	Game.canvas.width = width;
	Game.canvas.height = height;
	Game.ctx = Game.canvas.getContext("2d");
}

function drawMidLine(){
	for (let i = 0; i < Game.canvas.height; i += 50){
		Game.ctx.fillStyle = "#F1E0F0";
		Game.ctx.fillRect(Game.canvas.width / 2 - 4, i, 8, 25);
		Game.ctx.strokeStyle = "white";
		Game.ctx.lineWidth = 1;
		Game.ctx.strokeRect(Game.canvas.width / 2 - 4, i, 8, 25); // Draw the border
	}
}

function drawMidLineHor(){
	for (let i = 0; i < Game.canvas.width; i += 50){
		Game.ctx.fillStyle = "#F1E0F0";
		Game.ctx.fillRect(i, Game.canvas.height / 2 - 4, 25, 8);
		Game.ctx.strokeStyle = "white";
		Game.ctx.lineWidth = 1;
		Game.ctx.strokeRect(i, Game.canvas.height / 2 - 4, 25, 8); // Draw the border
	}
}

function renderPong() {
	
	if (Game.ctx && lastGameState){
		Game.ctx.fillStyle = "#401010";
		Game.ctx.fillRect(0, 0, Game.canvas.width, Game.canvas.height);
		drawMidLine();
		if (Game.players == 4)
			drawMidLineHor()
		for (let i = 0; i < Game.players; i++){
			if (lastGameState.score[i] == -1)
				drawWall(i)
			else
				drawPaddle(lastGameState.paddle["p" + (i + 1)][0], lastGameState.paddle["p" + (i + 1)][1], i < 2)
		}
		drawBall(lastGameState.ball[0], lastGameState.ball[1]);
		drawScores(lastGameState.score, Game.players);
		lastUpdateTime = performance.now();
	}
}

async function setPong(gameConstant) {
	window.history.pushState({}, '', '/pong');
	const response = await fetch('/static/html/pong.html');
	const html = await response.text();
	document.querySelector("div#app").innerHTML = html;
	Game.paddleSize = { width: gameConstant.paddle.width, height: gameConstant.paddle.height };
	Game.ballRadius = gameConstant.ballRadius;
	Game.players = gameConstant.players;
	CreateCanvas(gameConstant.board.x, gameConstant.board.y);
	setNames(gameConstant.names);
	adjustPlayerPositions();
}

function setNames(names){
	for (let i = 0; i < Game.players; i++){
		switch (i){
			case 0:
				if (names[i])
					document.querySelector("#player-left .player-name").innerText = names[i];
				break;
			case 1:
				if (names[i])
					document.querySelector("#player-right .player-name").innerText = names[i];
				break;
			case 2:
				if (names[i])
					document.querySelector("#player-top .player-name").innerText = names[i];
				break;
			case 3:
				if (names[i])
					document.querySelector("#player-bottom .player-name").innerText = names[i];
				break;
		}
	}
}

function adjustPlayerPositions() {
    let canvas = document.getElementById("pong");
	if (window.location.pathname != "/pong")
		return;
    if (!canvas)
        return;

    let canvasRect = canvas.getBoundingClientRect();

	if (Game.players == 4){
    	document.getElementById("player-top").style.top = `${canvasRect.top - 40}px`;
    	document.getElementById("player-bottom").style.top = `${canvasRect.bottom + 10}px`;
	}
	else{
		document.getElementById("player-top").hidden = true;
    	document.getElementById("player-bottom").hidden = true;
	}
    document.getElementById("player-left").style.top = `${canvasRect.top + canvasRect.height / 2}px`;
    document.getElementById("player-right").style.top = `${canvasRect.top + canvasRect.height / 2}px`;
}

// Adjust positions when the page loads and resizes
window.addEventListener("load", adjustPlayerPositions);
window.addEventListener("resize", adjustPlayerPositions);
