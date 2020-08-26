# -*- coding: utf-8 -*-

from enigma import gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eTimer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.CanvasSource import CanvasSource   
from Components.Sources.StaticText import StaticText   
from Screens.Screen import Screen

import random

def argb(a,r,g,b):
	return (a<<24)|(r<<16)|(g<<8)|b

class Tile(object):

	shapes = {
		"I": [ "    IIII        ", " I   I   I   I  ", "    IIII        ", " I   I   I   I  " ],
		"J": [ " J   JJJ        ", "  J   J  JJ     ", "     JJJ   J    ", "  JJ  J   J     " ],
		"L": [ "  L LLL         ", "LL   L   L      ", "    LLL L       ", " L   L   LL     " ],
		"O": [ " OO  OO         ", " OO  OO         ", " OO  OO         ", " OO  OO         " ],
		"S": [ " SS SS          ", "S   SS   S      ", " SS SS          ", "S   SS   S      " ],
		"T": [ " TTT  T         ", " T   TT  T      ", "      T  TTT    ", "   T  TT   T    " ],
		"Z": [ " ZZ   ZZ        ", "  Z  ZZ  Z      ", " ZZ   ZZ        ", "  Z  ZZ  Z      " ]
	}

	def __init__(self, shape):
		self.shape = self.shapes[shape]
		self.x = 0
		self.y = 0
		self.face = 0


class TetrisBoard(object):

	cellwidth = 49
	
	pieceColors = {
		" ": argb(0, 0xff, 0xff, 0xff),
		"I": argb(0, 0x00, 0x00, 0xff),
		"J": argb(0, 0xff, 0x00, 0x00),
		"L": argb(0, 0xff, 0xd7, 0x00),
		"O": argb(0, 0x40, 0x88, 0x40),
		"S": argb(0, 0xff, 0x00, 0xff),
		"T": argb(0, 0x00, 0xff, 0x00),
		"Z": argb(0, 0xff, 0xa5, 0x00),
	}
	
	def __init__(self, canvas):
		self.canvas = canvas
		self.canvas.fill(0,0,490,980, argb(33,255,255,255))
		self.setupBoard()
		self.drawBoard(self.board)
		self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.moveDown)
	
	def setupBoard(self):
		self.timeout = 1000
		self.lines = 0
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
		frameColor = argb(0x00, 0xd9, 0xd9, 0xc5)
		color      = self.pieceColors[piece]
			
		x = x * self.cellwidth
		y = y * self.cellwidth
		
		self.canvas.fill(x,   y,   self.cellwidth,   self.cellwidth,   frameColor)
		self.canvas.fill(x+1, y+1, self.cellwidth-2, self.cellwidth-2, color)
	
	def insertTile(self, tile, callback):
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
		for line in range(1,21):
			start = line * 12
			end   = start + 12
			segment = self.board[start:end]
			if not " " in segment:
				tmp = "WWWWWWWWWWWWW          W" + self.board[12:start] + self.board[end:]
				self.board = tmp
				self.lines += 1
				if self.lines % 5 == 0 and self.timeout > 200:
					self.timeout = self.timeout - 200
	
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
	
		
class Board(Screen):

	skin = """
		<screen name="Tetris" position="0,0" size="1920,1080" title="Tetris" flags="wfNoBorder">
			<widget source="Canvas" render="Canvas" position="50,20" size="490,980" />
			<widget name="state" position="600,20" size="500,100" font="Regular;80" foregroundColor="#00cc0000" />
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
		self.skinName = "Tetris_v0"
		
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
		
		self["Canvas"] = CanvasSource()
		
		self["key_red"] = Label()
		self["key_green"] = Label("Spiel starten")
		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["state"] = Label()
		self["lines"] = Label()
		self["level"] = Label()

		self.onLayoutFinish.append(self.setupBoard)

	def setupBoard(self):
		self.board = TetrisBoard(self["Canvas"])
		self.tetrominos = [ "I", "J", "L", "O", "S", "T", "Z" ]
		self.stopped = True
	
	def eventLoop(self, state):
		self["lines"].setText("%d eliminierte Zeilen" % self.board.lines)
		self["level"].setText("Level %d" % int(6 - self.board.timeout // 200))
		if not state:
			self.gameOver()
		else:
			random.shuffle(self.tetrominos)
			tile = self.tetrominos[0]
			piece = Tile(tile)
			self.board.insertTile(piece, self.eventLoop)
	
	def gameOver(self):
		self.stopped = True
		self["state"].setText("Game Over")
	
	def cancel(self):
		self.board.moveTimer.stop()
		self.close()

	def up(self):
		self.board.rotateTile(1)

	def down(self):
		self.board.rotateTile(-1)

	def left(self):
		self.board.moveTile(-1)

	def right(self):
		self.board.moveTile(1)

	def ok(self):
		self.board.accelerate = True

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

