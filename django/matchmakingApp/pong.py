import asyncio
import time
from dataclasses import dataclass, asdict
from math import sqrt, cos, sin, pi
 
@dataclass
class Paddle:
	width: int
	height: int
	speed: float

@dataclass
class Board:
	x: int
	y: int

@dataclass
class GameData:
	board: Board
	paddle: Paddle
	ballRadius: float
	initSpeed: int
	players: int
	names: list

# GLOBALE
FPS = 1 / 60
SPEED = 300 # px/s
WIN_CON = 11

# __________________
#|        P3        |
#|                  |
#|                  |
#|P1              P2|
#|                  |
#|                  |
#|________P4________|

class Pong:
	def __init__(self, players_keys, end_Function, players_nb, plrs, nicknames):
		self.AI = None
		self.p_nbr = 0
		self.game_const = GameData(
			board=Board(x=1000, y=1000),
			paddle=Paddle(width=12, height=100, speed=0),
			ballRadius=10,
			initSpeed=5,
			players=players_nb,
			names = nicknames,
		)
		if players_nb < 4:
			self.game_const.board.y = 750
		self._vector = [1, 1]
		self._speed = SPEED * FPS
		self._score = [0, 0]
		self._ball = [self.game_const.board.x / 2, self.game_const.board.y / 2]
		self._prevBall = self._ball
		self.p_keys = players_keys
		if players_nb == 1:
			self.p_nbr = 2
			self.game_const.players = 2
			self.game_const.names.append("AI")
			self.p_keys.append([{'ArrowUp': False, 'ArrowDown': False}])
			self.AI = PongAI(self, self.p_keys[1][0])
		else:
			self.p_nbr = players_nb
		self._paddle = {
			"p1" : [-1, -1],
			"p2" : [-1, -1],
			"p3" : [-1, -1],
			"p4" : [-1, -1],
			}
		self.launcher = 0
		self._paddle["p1"] = [1, self.game_const.board.y / 2 - self.game_const.paddle.height / 2]
		self._paddle["p2"] = [self.game_const.board.x - (self.game_const.paddle.width + 1), self.game_const.board.y / 2 - self.game_const.paddle.height / 2]
		if players_nb > 2:
			self._paddle["p3"] = [self.game_const.board.x / 2 - self.game_const.paddle.height / 2, 1]
			self._paddle["p4"] = [self.game_const.board.x / 2 - self.game_const.paddle.height / 2, self.game_const.board.y - (self.game_const.paddle.width + 1)]
			self._score.append(0)
			self._score.append(0)
		self.game_const.initSpeed = self._speed
		self.game_const.paddle.speed = sqrt(self._vector[0] ** 2 + self._vector[1] ** 2) * self._speed * 1.6
		self.endF = end_Function 
		self._players = plrs
  
	def update(self):
		self.move_ball()
		if self.AI:
			self.AI.updateAI()
		self.move_paddles()
	def get_game_constant(self):
		return asdict(self.game_const)
	def get_game_data(self):
		return {
			'ball': self._ball,
			'vector': self._vector,
			'speed': self._speed,
			'score': self._score,
			'paddle': self._paddle,
			}
  
	def move_paddles(self):
		paddleSpeed = self.game_const.paddle.speed
 
		for i in range(self.p_nbr):
			if i == 1 and self.AI and self.AI.AIPos >= self._paddle["p2"][1] + 10 and self.AI.AIPos <= self._paddle["p2"][1] + self.game_const.paddle.height - 10 and self._vector[0] > 0:
				continue
			elif self.p_keys[i][0]['ArrowUp']:
				self.check_paddle_movement(self._paddle["p" + str(i + 1)][i < 2], -1 * paddleSpeed, "p" + str(i + 1))
			elif self.p_keys[i][0]['ArrowDown']:
				self.check_paddle_movement(self._paddle["p" + str(i + 1)][i < 2], paddleSpeed, "p" + str(i + 1))		

	def check_paddle_movement(self, pos, move, player):
		#check if paddle reach the border of the board
		if player == "p1" or player == "p2":
			if (pos + move) >= 0 and pos + move + self.game_const.paddle.height <= self.game_const.board.y:
				self._paddle[player][1] += move
			elif (pos + move) < 0:
				self._paddle[player][1] = 0
			else:
				self._paddle[player][1] = self.game_const.board.y - self.game_const.paddle.height
		else:
			if (pos + move) >= 0 and pos + move + self.game_const.paddle.height <= self.game_const.board.x:
				self._paddle[player][0] += move
			elif (pos + move) < 0:
				self._paddle[player][0] = 0
			else:
				self._paddle[player][0] = self.game_const.board.x - self.game_const.paddle.height
   
	def move_ball(self):
		self._prevBall = self._ball
		self._ball[0] += (self._vector[0] * self._speed)
		self._ball[1] += (self._vector[1] * self._speed)
		self.check_collision()

	def check_collision(self):
		# check for wall colision up/down
		Const = self.game_const
		if self.p_nbr < 4 and (self._ball[1] + Const.ballRadius > Const.board.y \
			or self._ball[1] - Const.ballRadius < 0):
			self.colideWall()
		#check for paddle colision up/down
		elif self.p_nbr == 4 and (self._ball[1] + Const.ballRadius > Const.board.y - Const.paddle.width\
			or self._ball[1] - Const.ballRadius < Const.paddle.width):
			if not self.PlayerOut("p3" if self._vector[1] <= 0 else "p4"):
				if not self.colidePaddle("p3" if self._vector[1] <= 0 else "p4"):
					if self.OutOfBound():
						self.scoreAndResetBall()
		#check for paddle colision left/right, and also for score
		if self._ball[0] + Const.ballRadius >= Const.board.x - Const.paddle.width\
			or self._ball[0] - Const.ballRadius <= Const.paddle.width:
			if not self.PlayerOut("p1" if self._vector[0] <= 0 else "p2"):
				if not self.colidePaddle("p1" if self._vector[0] <= 0 else "p2"):
					if self.OutOfBound():
						self.scoreAndResetBall()

	def PlayerOut(self, pp):
		if self._score[int(pp[1]) - 1] == -1:
			if int(pp[1]) > 2:
				self.colideWall()
			else:
				self.colideVerticalWall()
			return True
		return False

	def colideWall(self):
		# change position of ball based on collision point and distance
		if self._ball[1] < self.game_const.ballRadius or self._ball[1] > self.game_const.board.y - self.game_const.ballRadius:
			lim = self.game_const.ballRadius
			if self._ball[1] > self.game_const.board.y - self.game_const.ballRadius:
				lim = self.game_const.board.y - self.game_const.ballRadius
			dif = lim - self._ball[1]
			self._ball[1] = lim + dif
		self._vector[1] *= -1

	def colideVerticalWall(self):
		if self._ball[0] < self.game_const.ballRadius or self._ball[0] > self.game_const.board.x - self.game_const.ballRadius:
			lim = self.game_const.ballRadius
			if self._ball[0] > self.game_const.board.x - self.game_const.ballRadius:
				lim = self.game_const.board.x - self.game_const.ballRadius
			dif = lim - self._ball[0]
			self._ball[0] = lim + dif
		self._vector[0] *= -1

	def colidePaddle(self, pp):
		paddleHeight = self.game_const.paddle.height
		gConst = self.game_const
		if self._ball[pp == "p1" or pp == "p2"] + gConst.ballRadius < self._paddle[pp][pp == "p1" or pp == "p2"] or \
   			self._ball[pp == "p1" or pp == "p2"] - gConst.ballRadius > self._paddle[pp][pp == "p1" or pp == "p2"] + gConst.paddle.height:
			return False
		self.adjustBallCollision(pp)
		if pp == "p1" or pp == "p2":
			paddleCenter = self._paddle[pp][1] + paddleHeight / 2
			hitPosition = self._ball[1] - paddleCenter
		else:
			paddleCenter = self._paddle[pp][0] + paddleHeight / 2
			hitPosition = self._ball[0] - paddleCenter
		maxBounceAngle = pi / 4 # 45 degrees
		bounceAngle = (hitPosition / (paddleHeight / 2)) * maxBounceAngle
		speed = sqrt(self._vector[0] ** 2 + self._vector[1] ** 2)
		if pp == "p1" or pp == "p2":
			self.colVerticalPaddle(pp, speed, bounceAngle)
		else:
			self.colHorizontalPaddle(pp, speed, bounceAngle)
		return True
	
	def colVerticalPaddle(self, pp, speed, bounceAngle):
		self._vector[0] = speed * cos(bounceAngle)
		self._vector[1] = speed * sin(bounceAngle)
		self.increaseSpeed(pp)
		if pp == "p1":
			self._vector[0] = abs(self._vector[0])
			self.launcher = 0
		elif pp == "p2":
			self._vector[0] = -abs(self._vector[0])
			self.launcher = 1

	def colHorizontalPaddle(self, pp, speed, bounceAngle):
		self._vector[1] = speed * cos(bounceAngle)
		self._vector[0] = speed * sin(bounceAngle)
		if pp == "p3":
			self._vector[1] = abs(self._vector[1])
			self.launcher = 2
		elif pp == "p4":
			self._vector[1] = -abs(self._vector[1])
			self.launcher = 3

	def adjustBallCollision(self, pp):
		if pp == "p1":
			self._ball[0] = self._paddle["p1"][0] + self.game_const.paddle.width + self.game_const.ballRadius
		elif pp == "p2":
			self._ball[0] = self._paddle["p2"][0] - self.game_const.ballRadius
		elif pp == "p3":
			self._ball[1] = self._paddle["p3"][1] + self.game_const.paddle.width + self.game_const.ballRadius
		elif pp == "p4":
			self._ball[1] = self._paddle["p4"][1] - self.game_const.ballRadius

	def OutOfBound(self):
		board = self.game_const.board
		if self._ball[0] <= 0 or self._ball[0] >= board.x - 0:
			return True
		if self._ball[1] <= 0 or self._ball[1] >= board.y - 0:
			return True
		return False
		 
	def increaseSpeed(self, pp):
		#When player moves the paddle at the same time the ball touch it, speed is increased
		# Only decreased back to init when scored but can be changed into decreased when paddle does not moves at same time
		for i in range(self.p_nbr):
			if pp == "p" + str(i+1):
				if self.p_keys[i][0]['ArrowUp'] or self.p_keys[i][0]['ArrowDown']:
					if self._speed < self.game_const.initSpeed * 3: 
						self._speed *= 1.1
  
	# with the implementation of a 4 player game instead of watching where the ball ended to score, it watches who send it and set the looser as the new sender
	def scoreAndResetBall(self):
		const = self.game_const
		if self._score[self.launcher] >= 0:
			self._score[self.launcher] += 1
		"""need to think about the pause/delay state in between the score and the service"""
		self._speed = const.initSpeed
		if (self._ball[0] <= 0 or self._ball[0] >= const.board.x):
			self._vector[0] *= -1  #send the service to the opposite way with the same impulse as before score (maybe rand val or fix val)
			if self._ball[0] <= 0:
				if self.launcher == 0:
					self._score[self.launcher] = max(self._score[self.launcher] - 2, 0)
				self.launcher = 0
			else:
				if self.launcher == 1:
					self._score[self.launcher] = max(self._score[self.launcher] - 2, 0)
				self.launcher = 1
		elif (self._ball[1] <= 0 or self._ball[1] >= const.board.y):
			self._vector[1] *= -1  #send the service to the opposite way with the same impulse as before score (maybe rand val or fix val)
			if self._ball[1] <= 0:
				if self.launcher == 2:
					self._score[self.launcher] = max(self._score[self.launcher] - 2, 0)
				self.launcher = 2
			else:
				if self.launcher == 3:
					self._score[self.launcher] = max(self._score[self.launcher] - 2, 0)
				self.launcher = 3
		self._ball = [const.board.x / 2, const.board.y / 2]
		self.checkEndGame()
  
	def checkEndGame(self):
		scoreDiff = 0
		for i in range(self.p_nbr):
			if self._score[i] >= WIN_CON:
				for j in range(self.p_nbr):
					if i != j and abs(self._score[i] - self._score[j]) < 2:
						scoreDiff += 1
				if not scoreDiff:
					self.endF()
			scoreDiff = 0

	def get_result(self):
		# result = {}
		# for i in range(self.p_nbr):
		# 	result[str(self._players[i])] = self._score[i]
		# return result
		result = {}
		i = 0
		for user in self._players:
			result[str(user)] = self._score[i]
			i += 1
		if self.AI:
			result['1'] = self._score[1]
		return result

	def get_winners(self):
		index_max = self._score.index(max(self._score))
		return [self._players[index_max]]

	def get_loosers(self):
		index_max = self._score.index(min(self._score))
		return [self._players[index_max]]

	def set_looser(self, looser_id):
		if looser_id in self._players:
			self._score[self._players.index(looser_id)] = -1

 
class PongAI:
	def __init__(self, pong, AIKey):
		self._pong = pong
		self._key = AIKey
		self.lastUpdate = int(time.time() * 1000)
		self.gameConst = pong.game_const
		self.AIPos = 0
	
	def updateAI(self):
		now = int(time.time() * 1000)
		if now - self.lastUpdate < 1000:
			return
		self.lastUpdate = now
		self.calculateNextPos()
 
	def calculateNextPos(self):
		ball = self._pong._ball.copy()
		vector = self._pong._vector.copy()
		vector[0] *= self._pong._speed
		vector[1] *= self._pong._speed
		paddle = self._pong._paddle["p2"].copy()
		if self.malusCondition(ball, vector):
			ball = self.simplePath(ball)
		else:
			ball = self.calculatedPath(ball, vector)
			self.AIPos = ball[1]
			if ball[1] < paddle[1] + 10:
				self._key['ArrowUp'] = True
				self._key['ArrowDown'] = False 
			elif ball[1] > paddle[1] + self.gameConst.paddle.height - 10:
				self._key['ArrowUp'] = False
				self._key['ArrowDown'] = True
			else:
				self._key['ArrowUp'] = False
				self._key['ArrowDown'] = False
  
	def simplePath(self, ball):
		ball[1] = self._pong._ball[1]
		return ball
	def calculatedPath(self, ball, vector):
		const = self.gameConst
		while vector[0] > 0 and ball[0] > const.paddle.width and ball[0] < const.board.x - const.paddle.width:
			if ball[0] + vector[0] > const.paddle.width:
				ball[0] += vector[0]
			else:
				ball[0] = self.adjustPos(ball[0], vector[0], const.paddle.width)
				vector[0] *= -1
			if ball[1] + vector[1] < 0 and ball[1] + vector[1] < const.board.y:
				if ball[1] + vector[1] < 0:
					ball[1] = self.adjustPos(ball[1], vector[1], 0)
				else:
					ball[1] = self.adjustPos(ball[1], vector[1], const.board.y)
				vector[1] *= -1
			else:
				ball[1] += vector[1]
		return ball
 
	def adjustPos(self, ball, speed, lim):
		tmp = 0
		dif = 0

		tmp = ball + speed
		dif = lim - tmp
		ball = lim + dif
		return ball
	 
	def malusCondition(self, ball, vector):
		speedDiff = self._pong._speed // self.gameConst.initSpeed
		if (speedDiff < 2 and vector[0] > 0 and ball[0] >= self.gameConst.board.x / 2):
			return False
		elif (speedDiff < 3 and vector[0] > 0 and ball[0] >= self.gameConst.board.x / 3):
			return False
		elif (speedDiff and vector[0] > 0):
			return False
		return True
