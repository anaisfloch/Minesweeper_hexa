# -*- coding: utf-8 -*-

import math
from PyQt5 import QtCore, QtGui, QtWidgets
from grille_hexa import Grille, CaseBombe, CaseVide


class HexaBoard(QtWidgets.QWidget):
    """Plateau d'hexagones sans espaces entre les cases.
    """
    case_cliquee = QtCore.pyqtSignal(int, int, int)  # ligne, colonne, bouton souris
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grille_obj = None
        self.radius = 30.0
        self.margin = 12.0
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)

    def set_grille(self, grille):
        self.grille_obj = grille
        self.update_size()
        self.update()

    def centre(self, ligne, colonne):
        # calcul du centre de l'hexagone pour mise en quinconce 
        x = self.margin + self.radius + colonne * 1.5 * self.radius
        y = (self.margin + math.sqrt(3) * self.radius / 2 + ligne * math.sqrt(3) * self.radius + (colonne % 2) * math.sqrt(3) * self.radius / 2)
        return QtCore.QPointF(x, y)

    def hexagones(self, ligne, colonne):
        # calcul des coordonnées des sommets
        centre = self.centre(ligne, colonne)
        points = []
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            points.append(QtCore.QPointF(centre.x() + self.radius * math.cos(rad), centre.y() + self.radius * math.sin(rad)))
        return QtGui.QPolygonF(points)

    def update_size(self):
        if self.grille_obj is None:
            return
        rows, cols = self.grille_obj.taille
        width = self.margin * 2 + self.radius * 2 + max(0, cols - 1) * 1.5 * self.radius
        height = (self.margin * 2 + math.sqrt(3) * self.radius + max(0, rows - 1) * math.sqrt(3) * self.radius + math.sqrt(3) * self.radius / 2)
        self.setMinimumSize(math.ceil(width), math.ceil(height))
        self.resize(math.ceil(width), math.ceil(height))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(),QtGui.QColor("#263238"))
        painter.setFont(QtGui.QFont("Arial", 13, QtGui.QFont.Bold))
        if self.grille_obj is None:
            return

        # plus il y a de bombes voisines, plus la couleur est inquiétante
        couleurs_chiffres = {1: "#1565C0", 2: "#2E7D32", 3: "#C62828", 4: "#6A1B9A", 5: "#AD1457", 6: "#00838F"}
        for r in range(self.grille_obj.taille[0]):
            for c in range(self.grille_obj.taille[1]):
                case = self.grille_obj.grille[r][c]
                poly = self.hexagones(r, c)
                if case.drapeau:
                    fond = QtGui.QColor("#FFCDD2")
                elif case.decouverte:
                    fond = QtGui.QColor("#E8F5E9")
                else:
                    fond = QtGui.QColor("#B0BEC5")
                painter.setBrush(fond)
                painter.setPen(QtGui.QPen(QtGui.QColor("#37474F"), 1.2))
                painter.drawPolygon(poly)

                texte = ""
                couleur_texte = QtGui.QColor("#263238")
                if case.drapeau:
                    texte = "⚐"
                    couleur_texte = QtGui.QColor("#C62828")
                elif case.decouverte and isinstance(case, CaseBombe):
                    texte = "☠"
                    couleur_texte = QtGui.QColor("#B71C1C")
                elif case.decouverte and isinstance(case, CaseVide) and case.nbr_bombes_voisines > 0:
                    texte = str(case.nbr_bombes_voisines)
                    couleur_texte = QtGui.QColor(couleurs_chiffres.get(case.nbr_bombes_voisines, "#263238"))

                if texte:
                    painter.setPen(couleur_texte)
                    painter.drawText(poly.boundingRect(), QtCore.Qt.AlignCenter, texte)

    def mousePressEvent(self, event):
        if self.grille_obj is None:
            return
        # pointage compliqué pcq cases trop petites
        for r in range(self.grille_obj.taille[0]):
            for c in range(self.grille_obj.taille[1]):
                if self.hexagones(r, c).containsPoint(event.localPos(), QtCore.Qt.OddEvenFill):
                    if event.button() == QtCore.Qt.LeftButton:
                        self.case_cliquee.emit(r, c, 1)
                    elif event.button() == QtCore.Qt.RightButton:
                        self.case_cliquee.emit(r, c, 2)
                    return


class Window(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Démineur hexagonal")
        self.resize(1000, 760)
        self.grille_obj = None
        self.partie_terminee = False
        self._message_en_cours = False

        self.title_label = QtWidgets.QLabel("Démineur hexagonal")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.difficulty_box_choice = QtWidgets.QComboBox()
        self.difficulty_box_choice.addItems(["Facile (8 × 8)", "Moyen (16 × 16)", "Difficile (16 × 30)"])
        self.button_validate_difficulty = QtWidgets.QPushButton("Nouvelle partie")
        self.button_validate_difficulty.clicked.connect(self.start_game)
        self.flags_label = QtWidgets.QLabel("Bombes restantes : 10")
        self.timer_label = QtWidgets.QLabel("Temps : 00: 00")
        self.temps_ecoule = 0
        self.timer_start = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualiser_timer)
        self.status_label = QtWidgets.QLabel("Choisis une difficulté puis lance une partie.")
        
        self.board = HexaBoard()
        self.board.case_cliquee.connect(self.handle_click)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.board)
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("""
        QDialog {
        background-color: #263238;
        }

        QLabel {
        color: #ECEFF1;
        font-size: 14px;
        padding: 5px;
        }

        QPushButton {
        background-color: #26A69A;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 9px 16px;
        font-weight: bold;
        }

        QPushButton:hover {
        background-color: #4DB6AC;
        }

        QComboBox {
        background-color: #455A64;
        color: white;
        border-radius: 6px;
        padding: 6px;
        }
        
        QScrollArea {
        border: none;
        background-color: #263238;
        }""")

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("Difficulté :"))
        header.addWidget(self.difficulty_box_choice)
        header.addWidget(self.button_validate_difficulty)
        header.addStretch(1)
        header.addWidget(self.flags_label)
        header.addWidget(self.timer_label)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addLayout(header)
        layout.addWidget(self.status_label)
        layout.addWidget(self.scroll, 1)

        self.start_game()

    def start_game(self):
        self.timer.stop()
        self.timer_start = False
        self.temps_ecoule = 0
        self.timer_label.setText("Temps : 00: 00")
        difficulte = self.difficulty_box_choice.currentIndex()
        self.partie_terminee = False
        self.grille_obj = Grille(difficulte)
        self.board.set_grille(self.grille_obj)
        self.flags_label.setText(f"Bombes restantes : {self.grille_obj.bombe}")
        self.status_label.setText("Clic gauche : révéler ; clic droit : drapeau")
        self.scroll.horizontalScrollBar().setValue(0)
        self.scroll.verticalScrollBar().setValue(0)
        
                
    def handle_click(self, ligne, colonne, bouton_souris):
        if self.partie_terminee or self.grille_obj is None:
            return
        case = self.grille_obj.grille[ligne][colonne]

        if bouton_souris == 2:
            if not case.decouverte:
                case.ajouter_drapeau()
                bomb_restantes = (self.grille_obj.bombe - self.grille_obj.compter_drapeaux())
                self.flags_label.setText(f"Bombes restantes : {bomb_restantes}")
                self.board.update()
            return

        if case.drapeau or case.decouverte:
            return
        self.start_timer()
        self.grille_obj.securite_premier_clic(ligne, colonne)
        case = self.grille_obj.grille[ligne][colonne]
        
        if isinstance(case, CaseBombe):
            case.decouvrir()
            self.reveal_all()
            self.partie_terminee = True
            self.timer.stop()
            self.status_label.setText("Partie terminée : tu as déclenché une bombe.")
            self.board.update()
            self.message("Défaite", "BOUM PERDU")
            return
        
        case.decouvrir()
        self.board.update()
        if self.check_victoire():
            self.reveal_all()
            self.partie_terminee = True
            self.timer.stop()
            self.status_label.setText("GG Well played Toutes les cases sans bombe sont découvertes.")
            self.board.update()
            self.message("Victoiry Royal", f"Tu as gagné en {self.temps_ecoule} secondes")
                    
    def check_victoire(self):
        for ligne in self.grille_obj.grille:
            for case in ligne:
                if isinstance(case, CaseVide) and not case.decouverte:
                    return False
        return True 
        
    def reveal_all(self):
        for ligne in self.grille_obj.grille:
            for case in ligne:
                case.decouverte = True
        self.board.update()        
        
    def message(self, titre, texte):
        if self._message_en_cours:
            return
        self._message_en_cours = True
        message = QtWidgets.QMessageBox(self)
        message.setWindowTitle(titre)
        message.setText(texte)
        message.setIcon(QtWidgets.QMessageBox.Information)
        rejouer = message.addButton("Rejouer", QtWidgets.QMessageBox.AcceptRole)
        quitter = message.addButton("Quitter", QtWidgets.QMessageBox.RejectRole)
        message.exec_()
        bouton_clique = message.clickedButton()
        self._message_en_cours = False

        if bouton_clique == rejouer:
            QtCore.QTimer.singleShot(0, self.start_game)
        elif bouton_clique == quitter:
            self.close()
            
    def actualiser_timer(self):
        self.temps_ecoule += 1 
        m = self.temps_ecoule // 60
        s = self.temps_ecoule % 60
        self.timer_label.setText(f"Temps : {m}:{s}")
        
    def start_timer(self):
        if not self.timer_start:
            self.timer_start = True
            self.timer.start(1000)
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
    
        