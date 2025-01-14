import json
import os
import shutil
import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QInputDialog, QDialog, QFormLayout, QMenu, QMenuBar, QAction, QComboBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

# Fonction pour enregistrer les données dans un fichier JSON
def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Fonction pour charger les données depuis un fichier JSON
def load_data(filename):
    try:
        if os.path.getsize(filename) == 0:
            return []
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        QMessageBox.critical(None, "Erreur de chargement", f"Le fichier {filename} est mal formaté ou vide.")
        return []

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Authentification')
        layout = QVBoxLayout()

        self.user_combo = QComboBox()
        self.user_combo.addItems(['Minidoc', 'Administrateur'])
        layout.addWidget(QLabel('Rôle:'))
        layout.addWidget(self.user_combo)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Mot de passe:'))
        layout.addWidget(self.password_input)

        self.login_button = QPushButton('Se connecter')
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def authenticate(self):
        role = self.user_combo.currentText()
        password = self.password_input.text()
        
        if role == 'Administrateur' and password == 'AdminCDI2025':
            self.main_window = MainWindow(admin=True)
            self.main_window.show()
            self.main_window.load_list()  # Charger une liste après authentification
            self.close()
        elif role == 'Minidoc' and password == 'MiniDoc2025':
            self.main_window = MainWindow(admin=True, root=True)
            self.main_window.show()
            self.main_window.load_list()  # Charger une liste après authentification
            self.close()
        else:
            QMessageBox.warning(self, 'Erreur', 'Mot de passe incorrect')

class MainWindow(QWidget):
    def __init__(self, admin=False, root=False):
        super().__init__()
        self.admin = admin
        self.root = root
        self.books = []
        self.openliste = ''
        self.init_ui()
        self.create_auto_backup()

    def init_ui(self):
        self.setWindowTitle('FlexiCDI V3.2')
        layout = QVBoxLayout()

        # Menu Bar
        self.menu_bar = QMenuBar(self)

        self.book_menu = QMenu('Livres', self)
        self.add_book_action = QAction('Ajouter un livre', self)
        self.delete_book_action = QAction('Supprimer un livre', self)
        self.edit_book_action = QAction('Modifier les informations d\'un livre', self)
        self.add_book_action.triggered.connect(self.add_book)
        self.delete_book_action.triggered.connect(self.delete_book)
        self.edit_book_action.triggered.connect(self.edit_book)
        self.book_menu.addAction(self.add_book_action)
        self.book_menu.addAction(self.delete_book_action)
        self.book_menu.addAction(self.edit_book_action)

        self.loan_menu = QMenu('Emprunt', self)
        self.borrow_book_action = QAction('Emprunter un livre', self)
        self.return_book_action = QAction('Rendre un livre', self)
        self.borrow_book_action.triggered.connect(self.borrow_book)
        self.return_book_action.triggered.connect(self.return_book)
        self.loan_menu.addAction(self.borrow_book_action)
        self.loan_menu.addAction(self.return_book_action)

        self.list_menu = QMenu('Listes', self)
        self.load_list_action = QAction('Charger une liste de livres', self)
        self.create_list_action = QAction('Créer une liste de livres', self)
        self.load_list_action.triggered.connect(self.load_list)
        self.create_list_action.triggered.connect(self.create_list)
        self.list_menu.addAction(self.load_list_action)
        self.list_menu.addAction(self.create_list_action)

        self.backup_menu = QMenu('Sauvegarde', self)
        self.create_backup_action = QAction('Créer une sauvegarde', self)
        self.rollback_action = QAction('Restaurer une sauvegarde', self)
        self.create_backup_action.triggered.connect(self.create_backup)
        self.rollback_action.triggered.connect(self.rollback)
        self.backup_menu.addAction(self.create_backup_action)
        self.backup_menu.addAction(self.rollback_action)

        self.help_menu = QMenu('Aide', self)
        self.tutorial_action = QAction('Comment utiliser le logiciel', self)
        self.tutorial_action.triggered.connect(self.show_tutorial)
        self.help_menu.addAction(self.tutorial_action)

        self.menu_bar.addMenu(self.book_menu)
        self.menu_bar.addMenu(self.loan_menu)
        self.menu_bar.addMenu(self.list_menu)
        self.menu_bar.addMenu(self.backup_menu)
        self.menu_bar.addMenu(self.help_menu)
        layout.setMenuBar(self.menu_bar)

        # Raccourcis claviers
        self.add_book_action.setShortcut(QKeySequence("Ctrl+N"))
        self.delete_book_action.setShortcut(QKeySequence("Ctrl+D"))
        self.edit_book_action.setShortcut(QKeySequence("Ctrl+M"))
        self.borrow_book_action.setShortcut(QKeySequence("Ctrl+E"))
        self.return_book_action.setShortcut(QKeySequence("Ctrl+R"))
        self.tutorial_action.setShortcut(QKeySequence("Ctrl+H"))

        # Search Field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher des livres (par auteur, titre ou numéro)...")
        self.search_field.textChanged.connect(self.filter_books)
        layout.addWidget(self.search_field)
        
        # Book Table
        self.book_table = QTableWidget(0, 4)
        self.book_table.setHorizontalHeaderLabels(['Numéro', 'Titre', 'Auteur', 'Emprunteur'])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.book_table)

        # Open List Label
        self.open_list_label = QLabel("Liste ouverte : Aucun")
        layout.addWidget(self.open_list_label)

        self.setLayout(layout)

    def update_book_table(self):
        self.book_table.setRowCount(len(self.books))
        for row, book in enumerate(self.books):
            self.book_table.setItem(row, 0, QTableWidgetItem(book['numero']))
            self.book_table.setItem(row, 1, QTableWidgetItem(book['titre']))
            self.book_table.setItem(row, 2, QTableWidgetItem(book['auteur']))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.get('emprunteur', 'Aucun')))
        if not self.books:
            self.book_table.setRowCount(1)
            self.book_table.setItem(0, 0, QTableWidgetItem(""))
            self.book_table.setItem(0, 1, QTableWidgetItem("Pas de livres trouvés"))
            self.book_table.setItem(0, 2, QTableWidgetItem(""))
            self.book_table.setItem(0, 3, QTableWidgetItem(""))

    def load_books(self):
        self.books = load_data(self.openliste)
        self.update_book_table()

    def add_book(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Ajouter un livre')
        layout = QFormLayout()
        author_input = QLineEdit()
        title_input = QLineEdit()
        number_input = QLineEdit()
        layout.addRow('Auteur:', author_input)
        layout.addRow('Titre:', title_input)
        layout.addRow('Numéro:', number_input)
        save_button = QPushButton('Sauvegarder')
        save_button.clicked.connect(lambda: self.save_new_book(dialog, author_input, title_input, number_input))
        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def save_new_book(self, dialog, author_input, title_input, number_input):
        author = author_input.text()
        title = title_input.text()
        number = number_input.text()
        for book in self.books:
            if book['numero'] == number:
                QMessageBox.warning(self, 'Erreur', 'Un livre avec ce numéro existe déjà')
                return
        self.books.append({"auteur": author, "titre": title, "numero": number})
        save_data(self.openliste, self.books)
        self.update_book_table()
        dialog.close()

    def delete_book(self):
        current_row = self.book_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, 'Erreur', 'Veuillez sélectionner un livre à supprimer.')
            return
        number = self.book_table.item(current_row, 0).text()
        for book in self.books:
            if book['numero'] == number:
                if 'emprunteur' in book:
                    QMessageBox.warning(self, 'Erreur', 'Ce livre est actuellement emprunté. Vous ne pouvez pas le supprimer.')
                    return
                confirmation = QMessageBox.question(self, 'Confirmation', f'Êtes-vous sûr de vouloir supprimer le livre "{book["titre"]}" ?')
                if confirmation == QMessageBox.Yes:
                    self.books.remove(book)
                    save_data(self.openliste, self.books)
                    self.update_book_table()
                    QMessageBox.information(self, 'Succès', f'Le livre "{book["titre"]}" a été supprimé avec succès.')
                return
        QMessageBox.warning(self, 'Erreur', 'Le livre avec ce numéro n\'a pas été trouvé.')

    def edit_book(self):
        current_row = self.book_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, 'Erreur', 'Veuillez sélectionner un livre à modifier.')
            return
        number = self.book_table.item(current_row, 0).text()
        for book in self.books:
            if book['numero'] == number:
                dialog = QDialog(self)
                dialog.setWindowTitle('Modifier un livre')
                layout = QFormLayout()
                author_input = QLineEdit(book['auteur'])
                title_input = QLineEdit(book['titre'])
                layout.addRow('Auteur:', author_input)
                layout.addRow('Titre:', title_input)
                save_button = QPushButton('Sauvegarder')
                save_button.clicked.connect(lambda: self.save_edited_book(dialog, book, author_input, title_input))
                layout.addWidget(save_button)
                dialog.setLayout(layout)
                dialog.exec_()
                return
        QMessageBox.warning(self, 'Erreur', 'Le livre avec ce numéro n\'a pas été trouvé.')

    def save_edited_book(self, dialog, book, author_input, title_input):
        book['auteur'] = author_input.text()
        book['titre'] = title_input.text()
        save_data(self.openliste, self.books)
        self.update_book_table()
        dialog.close()

    def borrow_book(self):
        current_row = self.book_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, 'Erreur', 'Veuillez sélectionner un livre à emprunter.')
            return
        number = self.book_table.item(current_row, 0).text()
        for book in self.books:
            if book['numero'] == number:
                if 'emprunteur' in book:
                    QMessageBox.warning(self, 'Erreur', 'Ce livre est déjà emprunté.')
                    return
                borrower, ok = QInputDialog.getText(self, 'Emprunter un livre', 'Entrez le nom de l\'emprunteur :')
                if not ok or not borrower:
                    return
                book['emprunteur'] = borrower
                save_data(self.openliste, self.books)
                self.update_book_table()
                QMessageBox.information(self, 'Succès', f'Le livre "{book["titre"]}" a été emprunté par {borrower}.')
                return
        QMessageBox.warning(self, 'Erreur', 'Le livre avec ce numéro n\'a pas été trouvé.')

    def return_book(self):
        current_row = self.book_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, 'Erreur', 'Veuillez sélectionner un livre à rendre.')
            return
        number = self.book_table.item(current_row, 0).text()
        for book in self.books:
            if book['numero'] == number:
                if 'emprunteur' not in book:
                    QMessageBox.warning(self, 'Erreur', 'Ce livre n\'est pas actuellement emprunté.')
                    return
                confirmation = QMessageBox.question(self, 'Confirmation', f'Êtes-vous sûr de vouloir rendre le livre "{book["titre"]}" ?')
                if confirmation == QMessageBox.Yes:
                    book.pop('emprunteur')
                    save_data(self.openliste, self.books)
                    self.update_book_table()
                    QMessageBox.information(self, 'Succès', f'Le livre "{book["titre"]}" a été rendu.')
                return
        QMessageBox.warning(self, 'Erreur', 'Le livre avec ce numéro n\'a pas été trouvé.')

    def load_list(self):
        options = [f for f in os.listdir() if f.endswith('.json')]
        if not options:
            QMessageBox.warning(self, 'Erreur', 'Aucune liste de livres trouvée.')
            return
        filename, ok = QInputDialog.getItem(self, 'Charger une liste', 'Sélectionnez une liste :', options, 0, False)
        if not ok or not filename:
            return
        self.openliste = filename
        self.load_books()
        self.open_list_label.setText(f"Liste ouverte : {filename}")
        QMessageBox.information(self, 'Succès', f'La liste {filename} a été chargée.')

    def create_list(self):
        filename, ok = QInputDialog.getText(self, 'Créer une liste', 'Entrez le nom de la nouvelle liste :')
        if not ok or not filename:
            return
        if not filename.endswith('.json'):
            filename += '.json'
        save_data(filename, [])
        self.openliste = filename
        self.books = []
        self.update_book_table()
        self.open_list_label.setText(f"Liste ouverte : {filename}")
        QMessageBox.information(self, 'Succès', f'La nouvelle liste {filename} a été créée et chargée.')

    def filter_books(self):
        search_text = self.search_field.text().lower()
        filtered_books = [book for book in self.books if search_text in book['auteur'].lower() or search_text in book['titre'].lower() or search_text in book['numero'].lower()]
        self.book_table.setRowCount(len(filtered_books))
        for row, book in enumerate(filtered_books):
            self.book_table.setItem(row, 0, QTableWidgetItem(book['numero']))
            self.book_table.setItem(row, 1, QTableWidgetItem(book['titre']))
            self.book_table.setItem(row, 2, QTableWidgetItem(book['auteur']))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.get('emprunteur', 'Aucun')))
        if not filtered_books:
            self.book_table.setRowCount(1)
            self.book_table.setItem(0, 0, QTableWidgetItem(""))
            self.book_table.setItem(0, 1, QTableWidgetItem("Pas de livres trouvés"))
            self.book_table.setItem(0, 2, QTableWidgetItem(""))
            self.book_table.setItem(0, 3, QTableWidgetItem(""))

    def show_tutorial(self):
        tutorial_text = (
            "Bienvenue dans FlexiCDI\n"
            "Pour utiliser ce logiciel, voici quelques étapes rapides :\n"
            "1. Authentifiez-vous avec votre rôle et mot de passe.\n"
            "2. Chargez une liste de livres existante ou créez une nouvelle liste.\n"
            "3. Utilisez le menu 'Livres' pour ajouter, supprimer ou modifier un livre.\n"
            "   - Lors de l'ajout, saisissez l'auteur, le titre et le numéro du livre.\n"
            "   - Pour supprimer ou modifier, sélectionnez un livre dans la table puis confirmez l'action.\n"
            "4. Utilisez le menu 'Emprunt' pour emprunter ou rendre un livre.\n"
            "   - Sélectionnez un livre, puis saisissez le nom de l'emprunteur lors de l'emprunt.\n"
            "5. Utilisez la barre de recherche pour filtrer les livres par auteur, titre ou numéro.\n"
            "6. Vous pouvez voir la liste actuellement chargée en bas de la fenêtre.\n"
            "7. Raccourcis clavier :\n"
            "   - Ctrl+N : Ajouter un livre\n"
            "   - Ctrl+D : Supprimer le livre sélectionné\n"
            "   - Ctrl+M : Modifier un livre\n"
            "   - Ctrl+E : Emprunter un livre\n"
            "   - Ctrl+R : Rendre un livre\n"
            "   - Ctrl+H : Aide\n\n"
            "8. Une save auto se fait a chaque démarage. Le fichier débute par Auto-.../n"
            "Bonne utilisation du logiciel !"
        )
        QMessageBox.information(self, 'Comment utiliser le logiciel', tutorial_text)

    def create_backup(self):
        source_dir = os.getcwd()  # Répertoire actuel
        target_dir = os.path.join(source_dir, "saves_files")  # Répertoire des sauvegardes
        
        # Vérifier si le répertoire des sauvegardes existe, sinon le créer
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        current_time = datetime.now().strftime("%Y-%m-%d_%H_%M")
        next_folder_path = os.path.join(target_dir, current_time)
        
        # Vérifier si un dossier avec le même nom existe déjà
        if os.path.exists(next_folder_path):
            QMessageBox.warning(self, 'Erreur', f'Un dossier de sauvegarde avec le nom {current_time} existe déjà.')
            return
        
        os.makedirs(next_folder_path)
        
        for filename in os.listdir(source_dir):
            if filename.endswith('.json'):
                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(next_folder_path, filename)
                
                # Copier le fichier JSON vers le nouveau dossier avec horodatage
                shutil.copy(source_path, target_path)
        
        QMessageBox.information(self, 'Succès', f'Tous les fichiers JSON ont été copiés dans le dossier {next_folder_path}.')


    def get_next_folder_number(self, target_dir):
        existing_folders = [name for name in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, name)) and name.isdigit()]
        if existing_folders:
            return max(existing_folders) + 1
        return 1

    def rollback(self):
        source_dir = os.getcwd()  # Répertoire actuel
        target_dir = os.path.join(source_dir, "saves_files")  # Répertoire des sauvegardes

        # Créer une sauvegarde des fichiers JSON actuels avant le rollback
        current_time = self.create_backup()

        options = [f for f in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, f)) and f != current_time]
        if not options:
            QMessageBox.warning(self, 'Erreur', 'Aucune sauvegarde trouvée.')
            return
        folder_name, ok = QInputDialog.getItem(self, 'Restaurer une sauvegarde', 'Sélectionnez une sauvegarde :', options, 0, False)
        if not ok or not folder_name:
            return
        backup_folder_path = os.path.join(target_dir, folder_name)
        
        # Vérifier si le dossier de sauvegarde existe
        if not os.path.exists(backup_folder_path):
            QMessageBox.warning(self, 'Erreur', f'Le dossier de sauvegarde {folder_name} n\'existe pas.')
            return
        
        for filename in os.listdir(backup_folder_path):
            source_path = os.path.join(backup_folder_path, filename)
            target_path = os.path.join(source_dir, filename)
            
            # Copier le fichier JSON depuis le dossier de sauvegarde vers la racine
            shutil.copy(source_path, target_path)

        QMessageBox.information(self, 'Succès', f'Les fichiers JSON ont été restaurés à partir de la sauvegarde {backup_folder_path}.')
        self.load_books()  # Recharger les livres après le rollback

        
        for filename in os.listdir(backup_folder_path):
            source_path = os.path.join(backup_folder_path, filename)
            target_path = os.path.join(source_dir, filename)
            
            # Copier le fichier JSON depuis le dossier de sauvegarde vers la racine
            shutil.copy(source_path, target_path)

        #QMessageBox.information(self, 'Succès', f'Les fichiers JSON ont été restaurés à partir de la sauvegarde {backup_folder_path}.')
        self.load_books()  # Recharger les livres après le rollback

        
        for filename in os.listdir(backup_folder_path):
            source_path = os.path.join(backup_folder_path, filename)
            target_path = os.path.join(source_dir, filename)
            
            # Copier le fichier JSON depuis le dossier de sauvegarde vers la racine
            shutil.copy(source_path, target_path)

        #QMessageBox.information(self, 'Succès', f'Les fichiers JSON ont été restaurés à partir de la sauvegarde {backup_folder_path}.')
        self.load_books()  # Recharger les livres après le rollback
        
    def create_auto_backup(self):
        source_dir = os.getcwd()  # Répertoire actuel
        target_dir = os.path.join(source_dir, "saves_files")  # Répertoire des sauvegardes
        
        # Vérifier si le répertoire des sauvegardes existe, sinon le créer
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        current_time = datetime.now().strftime("Auto-%Y-%m-%d_%H_%M")
        next_folder_path = os.path.join(target_dir, current_time)
        
        # Vérifier si un dossier avec le même nom existe déjà
        if os.path.exists(next_folder_path):
            return  # Annuler si une sauvegarde avec ce nom existe déjà
        
        os.makedirs(next_folder_path)
        
        for filename in os.listdir(source_dir):
            if filename.endswith('.json'):
                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(next_folder_path, filename)
                
                # Copier le fichier JSON vers le nouveau dossier avec horodatage
                shutil.copy(source_path, target_path)
        
        #QMessageBox.information(self, 'Succès', f'Sauvegarde automatique effectuée dans le dossier {next_folder_path}.')
        return current_time  # Retourner le nom du dossier de sauvegarde




def main():
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
