# -*- coding: utf-8 -*-

from enigma import eTimer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.CanvasSource import CanvasSource   
from Components.Sources.StaticText import StaticText   
from Screens.Screen import Screen

import random
import skin

class Tile(object):

	shapes = {
		" ": [ "                " ],
		"I": [ "    IIII        ", " I   I   I   I  ", "    IIII        ", " I   I   I   I  " ],
		"J": [ " J   JJJ        ", "  J   J  JJ     ", "     JJJ   J    ", "  JJ  J   J     " ],
		"L": [ "  L LLL         ", "LL   L   L      ", "    LLL L       ", " L   L   LL     " ],
		"O": [ " OO  OO         ", " OO  OO         ", " OO  OO         ", " OO  OO         " ],
		"S": [ " SS SS          ", "S   SS   S      ", " SS SS          ", "S   SS   S      " ],
		"T": [ " TTT  T         ", "  T   TT  T     ", "  T  TTT        ", "   T  TT   T    " ],
		"Z": [ " ZZ   ZZ        ", "  Z  ZZ  Z      ", " ZZ   ZZ        ", "  Z  ZZ  Z      " ]
	}

	def __init__(self, shape):
		self.shape = self.shapes[shape]
		self.x = 0
		self.y = 0
		self.face = 0


class TetrisBoard(object):

	cellwidth = int(skin.parameters.get("tetris_cellwidth", (43,))[0]) 
	
	pieceColors = {
		" ": skin.colorNames.get("tetris_tile_empty", skin.parseColor("#00ffffff")).argb(),
		"I": skin.colorNames.get("tetris_tile_I",     skin.parseColor("#00f5a9d0")).argb(),
		"J": skin.colorNames.get("tetris_tile_J",     skin.parseColor("#00f78181")).argb(),
		"L": skin.colorNames.get("tetris_tile_L",     skin.parseColor("#00f3e2a9")).argb(),
		"O": skin.colorNames.get("tetris_tile_O",     skin.parseColor("#00e2a9f2")).argb(),
		"S": skin.colorNames.get("tetris_tile_S",     skin.parseColor("#00a9f5a2")).argb(),
		"T": skin.colorNames.get("tetris_tile_T",     skin.parseColor("#00bcf5a9")).argb(),
		"Z": skin.colorNames.get("tetris_tile_Z",     skin.parseColor("#00a9a9f5")).argb(),
	}
	
	levels = [ 1000, 800, 720, 630, 540, 470, 370, 300, 220, 150 ]
	
	def __init__(self, canvas):
		self.canvas = canvas
		self.canvas.fill(0,0,430,860, skin.colorNames.get("tetris_background", skin.parseColor("#33ffffff")).argb())
		self.setupBoard()
		self.drawBoard(self.board)
		self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.moveDown)
	
	def setupBoard(self):
		self.lines = 0
		self.level = 0
		self.points = 0
		self.timeout = self.levels[self.level]
		self.accelerate = False
		self.board = 		"WWWWWWWWWWWW"
		for i in range(0,20):
			self.board += 	"W          W"
		self.board += 		"WWWWWWWWWWWW"
	
	def drawBoard(self, board):
		pos = 0
		for c in board:
			if c != 'W':
				x = pos % 10
				y = pos // 10
				self.drawPiece(x, y, c)
				pos += 1
		self.canvas.flush()
	
	def drawPiece(self, x, y, piece):
		frameColor = skin.colorNames.get("tetris_frame", skin.parseColor("#00d9d9c5")).argb()
		color      = self.pieceColors[piece]
			
		x = x * self.cellwidth
		y = y * self.cellwidth
		
		self.canvas.fill(x,   y,   self.cellwidth,   self.cellwidth,   frameColor)
		self.canvas.fill(x+1, y+1, self.cellwidth-2, self.cellwidth-2, color)
	
	def spawn(self, tile, callback):
		self.onDown = callback
		self.accelerate = False
		self.tile = tile
		self.tile.x = 4
		self.tile.y = 1
		layer = self.buildLayer()
		if layer:
			self.drawBoard(layer)
			self.moveTimer.start(self.timeout, True)
		else:
			self.onDown(False)
	
	def rotateTile(self, dir):
		face = self.tile.face
		self.tile.face = (self.tile.face + dir) % 4
		layer = self.buildLayer()
		if layer:
			self.drawBoard(layer)
		else:
			self.tile.face = face
			
	def moveTile(self, dir):
		x = self.tile.x
		self.tile.x += dir
		layer = self.buildLayer()
		if layer:
			self.drawBoard(layer)
		else:
			self.tile.x = x
	
	def moveDown(self):
		self.tile.y += 1
		layer = self.buildLayer()
		if layer:
			self.drawBoard(layer)
			timeout = self.timeout
			if self.accelerate:
				timeout = min(self.timeout,100)
			self.moveTimer.start(timeout, True)
		else:
			self.tile.y -= 1
			self.mergeLayer()
			self.onDown(True)

	def eliminateLines(self):
		eliminated = 0
		for line in range(1,21):
			start = line * 12
			end   = start + 12
			segment = self.board[start:end]
			if not " " in segment:
				tmp = "WWWWWWWWWWWWW          W" + self.board[12:start] + self.board[end:]
				self.board = tmp
				self.lines += 1
				eliminated += 1
				if self.lines % 5 == 0:
					self.level += 1
					if len(self.levels) > self.level:
						self.timeout = self.levels[self.level]
		self.points += [0,100,300,500,800][eliminated] * (self.level+1)
	
	def buildLayer(self):
		shape = self.tile.shape[self.tile.face]
		layer = list(self.board)
		pos = self.tile.y * 12 + self.tile.x
		cpos = 0
		offset = 0
		for c in shape:
			if c != ' ':
				if layer[pos+offset] != ' ':
					return False
				layer[pos+offset] = c
			cpos += 1
			offset = (cpos % 4) + (cpos // 4) * 12
		return ''.join(layer)

	def mergeLayer(self):
		self.board = self.buildLayer()
		self.eliminateLines()
	
class PreviewBoard(TetrisBoard):

	def __init__(self, canvas):
		self.canvas = canvas
		self.canvas.fill(0,0,196,196, skin.colorNames.get("tetris_background", skin.parseColor("#33ffffff")).argb())
	
	def drawBoard(self, piece):
		pos = 0
		for c in piece:
			x = pos % 4
			y = pos // 4
			self.drawPiece(x, y, c)
			pos += 1
		self.canvas.flush()
		
class Board(Screen):

	skin = """
		<screen name="Tetris" position="0,0" size="1920,1080" title="Tetris" flags="wfNoBorder">
			<widget source="canvas" render="Canvas" position="50,140" size="430,860" />
			<widget source="preview" render="Canvas" position="600,300" size="196,196" />
			<widget name="state" position="600,140" size="500,80" font="Regular;70" foregroundColor="#00cc0000" />
			<widget name="previewtext" position="600,230" size="1000,50" font="Regular;40" />
			<widget name="points" position="600,760" size="1000,80" font="Regular;60" />
			<widget name="lines" position="600,840" size="1000,80" font="Regular;60" />
			<widget name="level" position="600,920" size="1000,80" font="Regular;60" />
			<widget name="key_red" position="225,1015" size="280,55" zPosition="1" font="Regular; 23" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#00b81c46" />
			<widget name="key_green" position="565,1015" size="280,55" zPosition="1" font="Regular; 23" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#10389416"  />
			<widget name="key_yellow" position="905,1015" size="280,55" zPosition="1" font="Regular; 23" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#109ca81b" />
			<widget name="key_blue" position="1245,1015" size="280,55" zPosition="1" font="Regular; 23" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#008888ff" />
		</screen>
	"""

	def __init__(self, session):
		
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "Tetris_v1"
		
		self["actions"] =  ActionMap(["TetrisActions"], {
			"cancel":	self.cancel,
			"up":		self.up,
			"down":		self.down,
			"left":		self.left,
			"right":	self.right,
			"ok":		self.ok,
			"red":		self.red,
			"green":	self.green,
			"yellow":	self.yellow,
			"blue":		self.blue,
		}, -1)
		
		self["canvas"] = CanvasSource()
		self["preview"] = CanvasSource()

		self["previewtext"] = Label("Nächster Block:")
		self["key_red"] = Label()
		self["key_green"] = Label("Spiel starten")
		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["state"] = Label()
		self["lines"] = Label()
		self["level"] = Label()
		self["points"] = Label()

		self.onLayoutFinish.append(self.setupBoard)

	def setupBoard(self):
		self.stopped = True
		self.board = TetrisBoard(self["canvas"])
		self.preview = PreviewBoard(self["preview"])
		self.tetrominos = [ "I", "J", "L", "O", "S", "T", "Z" ]
		random.shuffle(self.tetrominos)
		self.nexttile = self.tetrominos[0]
		self.updatePreview(" ")
	
	def updatePreview(self, tile):
		previewPiece = Tile(tile)
		self.preview.drawBoard(previewPiece.shape[0])

	def eventLoop(self, state):
		self["lines"].setText("Zeilen: %d" % self.board.lines)
		self["level"].setText("Level: %d" % (self.board.level+1))
		self["points"].setText("Punkte: %d" % (self.board.points))
		if not state:
			self.gameOver()
		else:
			tile = self.nexttile
			piece = Tile(tile)
			random.shuffle(self.tetrominos)
			self.nexttile = self.tetrominos[0]
			self.updatePreview(self.nexttile)
			self.board.spawn(piece, self.eventLoop)
	
	def gameOver(self):
		self.updatePreview(" ")
		self["state"].setText("Game Over")
		self.stopped = True
	
	def cancel(self):
		self.board.moveTimer.stop()
		self.close()

	def up(self):
		if not self.stopped:
			self.board.rotateTile(1)

	def down(self):
		if not self.stopped:
			self.board.rotateTile(-1)

	def left(self):
		if not self.stopped:
			self.board.moveTile(-1)

	def right(self):
		if not self.stopped:
			self.board.moveTile(1)

	def ok(self):
		if not self.stopped:
			self.board.accelerate = not self.board.accelerate

	def red(self):
		pass

	def green(self):
		if self.stopped:
			self["state"].setText("")
			self.stopped = False
			self.board.setupBoard()
			self.eventLoop(True)

	def yellow(self):
		pass

	def blue(self):
		pass

