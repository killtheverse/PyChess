import sys
import chess
import chess.svg
import chess.engine
from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import (QBrush, QColor)
from PySide2.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QDialog,
                               QGridLayout, QStyleFactory, QPushButton, QWidget, QGraphicsObject,
                               QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit)
from PySide2.QtSvg import (QGraphicsSvgItem, QSvgRenderer, QSvgWidget)



class MainWindow(QWidget):
    """
        Main UI Window
    """
    def __init__(self, parent=None):
        """
        Initialize the chess board.
        """
        super().__init__(parent)
        self.setWindowTitle("PyChess")
        self.resize(1280, 720)
        self.svgWidget = QSvgWidget(parent=self)
        self.svgWidget.setGeometry(10, 10, 700, 700)
        self.boardSize = min(self.svgWidget.width(), self.svgWidget.height())
        self.margin = 0.05 * self.boardSize 
        self.squareSize = (self.boardSize - 2*self.margin)/8
        self.board = chess.Board()
        self.pieceToMove = [None, None]
        self.drawBoard()
        self.enginePath = "Use double \ instead of \ when on Windows system."
        self.time = 0.1

        self.maxtimelabel = QLabel("Max. time per move(in s):")
        self.engineLabel = QLabel("Enter path to engine:")
        self.engineButton = QPushButton("Find move")
        self.moveButton = QPushButton("Make move")
        self.undoButton = QPushButton("Undo move")
        self.undoButton.setMaximumWidth(175)
        self.pathField = QLineEdit()
        self.engineTime = QLineEdit()
        self.engineResult = QLineEdit()
        self.pathField.setText("Use double \ instead of \ when on Windows system.")

        self.main_layout = QHBoxLayout()
        self.tool_layout = QGridLayout()
        
        self.tool_layout.addWidget(self.engineLabel, 0, 0)
        self.tool_layout.addWidget(self.pathField, 0, 1) 
        self.tool_layout.addWidget(self.maxtimelabel, 1, 0)
        self.tool_layout.addWidget(self.engineTime, 1, 1)
        self.tool_layout.addWidget(self.engineButton, 2, 0)
        self.tool_layout.addWidget(self.engineResult, 2, 1)
        self.tool_layout.addWidget(self.moveButton, 3, 0)
        self.tool_layout.addWidget(self.undoButton, 3, 1)



        self.main_layout.addWidget(self.svgWidget, 55)
        self.main_layout.addLayout(self.tool_layout, 45)        
        self.setLayout(self.main_layout)

        self.engineButton.clicked.connect(self.find_move)
        self.moveButton.clicked.connect(self.make_move)

    @Slot(QWidget)
    def mousePressEvent(self, event):
        """
        Handles the left mouse click and enables moving the chess pieces by first clicking on the chess
        piece and then on the target square. 
        """
        if event.x() <= self.boardSize and event.y() <= self.boardSize:
            if self.margin<event.x()<self.boardSize-self.margin and self.margin<event.y()<self.boardSize-self.margin:
                if event.buttons()==Qt.LeftButton:
                    file = int((event.x() - self.margin) / self.squareSize)
                    rank = 7 - int((event.y() - self.margin) / self.squareSize)
                    square = chess.square(file, rank)
                    piece = self.board.piece_at(square)
                    coordinates = "{}{}".format(chr(file + 97), str(rank + 1))
                    if self.pieceToMove[0] is not None:
                        move = chess.Move.from_uci("{}{}".format(self.pieceToMove[1], coordinates))
                        if move in self.board.legal_moves:
                            self.board.push(move)
                        piece = None
                        coordinates = None
                    self.pieceToMove = [piece, coordinates]
                    self.drawBoard()

    
    def drawBoard(self):
        """
        Draw a chess board for the starting position and then redraw it for every move.
        """
        self.svgBoard = self.board._repr_svg_().encode("UTF-8")
        self.svgDrawBoard = self.svgWidget.load(self.svgBoard)  
        return self.svgDrawBoard


    def find_move(self):
        """
        Calculate the best move according to Stockfish
        """
        self.enginePath = self.pathField.text()
        self.time = float(self.engineTime.text())
        engine = chess.engine.SimpleEngine.popen_uci(self.enginePath)
        result = engine.play(self.board, chess.engine.Limit(time=self.time))
        self.engineResult.setText(str(result.move))
        engine.quit()
        return result.move
    
    def make_move(self):
        """
        Finds and plays the best move
        """
        move = self.find_move()
        self.board.push(move)
        self.drawBoard()

    def undo_move(self):
        """
        Undo the last move played on the board
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())