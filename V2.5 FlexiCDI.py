import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

# Valeur session open ou close
opens = 0
admin = 0
openlistevar = 0

pw_minidoc = "MiniDoc2024"
pw_admin = "AdminCDI2024"
pw_root = "AdminRoot2024"

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
        messagebox.showerror("Erreur de chargement", f"Le fichier {filename} est mal formaté ou vide.")
        return []

# Fenêtre d'accueil
def authentication():
    global aut, opens, admin, Aroot
    opens = 0
    admin = 0
    Aroot = 0
    aut = tk.Tk()
    aut.title("Authentification")

    role_label = tk.Label(aut, text="Rôle:")
    role_label.grid(row=0, column=0, padx=10, pady=5)

    user_button = tk.Button(aut, text="Utilisateur", command=user_interface)
    user_button.grid(row=0, column=1, padx=10, pady=5)

    admin_button = tk.Button(aut, text="Administrateur", command=lambda: admin_interface(aut))
    admin_button.grid(row=0, column=3, padx=10, pady=5)
    
    admin_button = tk.Button(aut, text="Minidoc", command=lambda: minidoc_interface(aut))
    admin_button.grid(row=0, column=2, padx=10, pady=5)
    
    aut.mainloop()

# Fonction pour afficher les fichiers JSON disponibles et charger la liste sélectionnée
def load_list_ui():
    global root
    root = tk.Tk()
    root.title("Sélectionner une liste")

    files = [f for f in os.listdir() if f.endswith('.json')]

    for idx, file in enumerate(files):
        button = tk.Button(root, text=file, command=lambda f=file: load_selected_list(f))
        button.grid(row=idx, column=0, padx=10, pady=5)
    
    root.mainloop()

def load_selected_list(filename):
    global openliste, books, root, opens, openlistevar
    openliste = filename
    books = load_data(openliste)
    if books is not None:
        messagebox.showinfo("Liste chargée", f"La liste {openliste} a été chargée avec succès.")
        root.destroy()
        if openlistevar == 0:
            openlistevar = 1
            admin_ui()

# Gestion des emprunts
def fen_epr():
    global root
    root = tk.Tk()
    root.title("Gestionnaire de réservations")

    emp = tk.Button(root, text="Emprunter", command=emprun)
    emp.grid(row=0, column=1, padx=10, pady=5)
    
    rd = tk.Button(root, text="Rendre", command=rendre)
    rd.grid(row=0, column=2, padx=10, pady=5)
    
    root.mainloop()

# ajouter verif livre studente-name

def emprun():
    global book_number, openliste
    global root
    root.destroy()
    student_name = simpledialog.askstring("Emprunter un livre", "Entrez le nom de l'élève : ")
    if student_name is None:
        return
    
    for book in books:
        if book['numero'] == book_number:
            if book.get('emprunteur') is None:
                book['emprunteur'] = student_name
                save_data(openliste, books)
                messagebox.showinfo("Emprunt de livre", f"Le livre \"{book['titre']}\" a été emprunté avec succès par {student_name}.")
                reload()
                return
            else:
                messagebox.showwarning("Emprunt de livre", f"Le livre \"{book['titre']}\" est déjà emprunté.")
                return
    messagebox.showwarning("Emprunt de livre", "Le livre avec ce numéro n'a pas été trouvé.")

## Ajouter verif student-name 
def rendre():
    global book_number, openliste, root
    for book in books:
        if book['numero'] == book_number:
            if book.get('emprunteur') is not None:
                book.pop('emprunteur')
                save_data(openliste, books)
                messagebox.showinfo("Retour de livre", f"Le livre \"{book['titre']}\" a été retourné avec succès.")
                reload()
                root.destroy()
                return
            else:
                messagebox.showwarning("Retour de livre", f"Le livre \"{book['titre']}\" n'est pas emprunté.")
                root.destroy()
                return
    messagebox.showwarning("Retour de livre", "Le livre avec ce numéro n'a pas été trouvé.")
    root.destroy()

# Gestion de la liste de livres
def fenetre_livres_gestion():
    global root, admin, book_number
    root = tk.Tk()
    root.title("Gestionnaire liste de livre du CDI")

    ajm = tk.Button(root, text="Ajout de livre", command=add_book_manually)
    ajm.grid(row=1, column=1, padx=10, pady=5)

    spm = tk.Button(root, text="Suppression de livre", command=remove_book_from_json)
    spm.grid(row=2, column=1, padx=10, pady=5)
    
    if admin == 1:
        aja = tk.Button(root, text="Ajouter une liste bloc note de livre", command=add_books_from_file)
        aja.grid(row=3, column=1, padx=10, pady=5)
        
    rml = tk.Button(root, text="Consulter le catalogue de livre", command=show_list)
    rml.grid(row=4, column=1, padx=10, pady=5)
    
    rml = tk.Button(root, text="Gestions des catalogues de livres (les fichier json)", command=load_files)
    rml.grid(row=5, column=1, padx=10, pady=5)
        
    root.mainloop()

def add_book_manually():
    global openliste
    author = simpledialog.askstring("Ajouter un livre", "Entrez l'auteur du livre : ")
    if author is None:
        return
    
    title = simpledialog.askstring("Ajouter un livre", "Entrez le titre du livre : ")
    if title is None:
        return

    number = simpledialog.askstring("Ajouter un livre", "Entrez le numéro du livre : ")
    if number is None:
        return
        
    for book in books:
        if book['numero'] == number:
            messagebox.showwarning("Gestions des livres", "Un livre avec ce numéro existe déjà")
            return
    
    books.append({"auteur": author, "titre": title, "numero": number})
    save_data(openliste, books)
    messagebox.showinfo("Gestions des livres", "Ajout avec succès")
    root.destroy()

def add_books_from_file():
    global openliste
    file_path = simpledialog.askstring("Ajouter des livres", "Entrez le chemin du fichier texte contenant les livres : ")
    with open(file_path, 'r') as f:
        for line in f:
            author, title, number = line.strip().split(',')
            books.append({"auteur": author, "titre": title, "numero": number})

    save_data(openliste, books)
    messagebox.showinfo("Gestions des livres", "Ajouts finis : penser à reload")

def remove_book_from_json():
    global openliste, root
    book_number = simpledialog.askstring("Gestionnaire de livre", "Entrez le numéro du livre : ")
    for book in books:
        if book['numero'] == book_number:
            if 'emprunteur' in book:
                messagebox.showwarning("Livre emprunté", "Ce livre est actuellement emprunté. Vous ne pouvez pas le supprimer.")
                return False

            confirmation = messagebox.askquestion("Confirmation", f"Êtes-vous sûr de vouloir supprimer le livre \"{book['titre']}\" ?")
            if confirmation == 'yes':
                books.remove(book)
                save_data(openliste, books)
                messagebox.showinfo("Suppression de livre", f"Le livre \"{book['titre']}\" a été supprimé avec succès.")
                root.destroy()
                reload()
                return True
            else:
                root.destroy()
                return False

    messagebox.showwarning("Livre non trouvé", "Le livre avec ce numéro n'a pas été trouvé dans la liste.")
    return False

def show_list():
    global root
    root.destroy()
    reservations = [f"Livre: {book['titre']}, Numéro: {book['numero']}, Emprunteur: {book.get('emprunteur', 'Aucun')}" for book in books]
    messagebox.showinfo("Réservations", "\n".join(reservations))

def reload():
    global openliste, books
    books = load_data(openliste)

def load_files():
    global root
    root.destroy()
    root = tk.Tk()
    root.title("Gestion des catalogues de livres (fichiers JSON)")

    load_liste_button = tk.Button(root, text="Charger une liste existante", command=load_liste)
    load_liste_button.grid(row=1, column=1, padx=10, pady=5)
    
    rml = tk.Button(root, text="Créer une liste de livres", command=addlist)
    rml.grid(row=2, column=1, padx=10, pady=5)

def borrow_or_return_book():
    global book_number
    book_number = simpledialog.askstring("Emprunter/Retourner un livre", "Entrez le numéro du livre : ")
    if book_number is None:
            return
    for book in books:
        if book['numero'] == book_number:
            fen_epr()
            return
    messagebox.showwarning("Retour de livre", "Le livre avec ce numéro n'a pas été trouvé.")

def show_book_info():
    book_number = simpledialog.askstring("Voir les informations d'un livre", "Entrez le numéro du livre : ")

    for book in books:
        if book_number is None:
            return
        if book['numero'] == book_number:
            messagebox.showinfo("Informations du livre", f"Auteur: {book['auteur']}\nTitre: {book['titre']}\nNuméro: {book['numero']}\nEmprunteur: {book.get('emprunteur', 'Aucun')}")
            return
        
    messagebox.showwarning("Informations du livre", "Le livre avec ce numéro n'a pas été trouvé.")

def show_reservations():
    reservations = [f"Livre: {book['titre']}, Numéro: {book['numero']}, Emprunteur: {book['emprunteur']}" for book in books if 'emprunteur' in book and book['emprunteur']]
    if reservations:
        messagebox.showinfo("Réservations", "\n".join(reservations))
    else:
        messagebox.showinfo("Réservations", "Aucun livre n'est actuellement emprunté.")

def load_liste():
    global openliste, root
    root.destroy()
    load_list_ui()

def addlist():
    global openliste
    openliste = simpledialog.askstring("Gestionnaire de listes", "Entrez le nom de la liste : ")
    step2addliste(openliste)

def step2addliste(filename):
    global books, root
    try:
        with open(filename, 'r') as f:
            books = json.load(f)
            root.destroy()
    except FileNotFoundError:
        books = []
        root.destroy()
        save_data(filename, books)

# Fonctions des sessions
def admin_interface(aut):
    global root, opens, admin
    password = simpledialog.askstring("Authentification", "Entrez le mot de passe : ")
    if password == pw_admin:
        opens = 1
        admin = 1
        aut.destroy()
        load_list_ui()
    elif password == pw_root:
        opens = 1
        admin = 1
        aut.destroy()
        load_list_ui()
    elif password is None:
        return
    else:
        messagebox.showerror("Authentification", "Mot de passe incorrect.")

def minidoc_interface(aut):
    global root, opens, admin
    password = simpledialog.askstring("Authentification", "Entrez le mot de passe : ")
    if password == pw_minidoc:
        opens = 1
        admin = 0
        aut.destroy()
        load_list_ui()
    elif password is None:
        return
    else:
        messagebox.showerror("Authentification", "Mot de passe incorrect.")

# Interfaces
def admin_ui():
    global root, opens, admin
    admin = 1
    opens = 1
    root = tk.Tk()
    root.title("Interface Administrateur")

    borrow_button = tk.Button(root, text="Gestionnaire d'emprunts", command=borrow_or_return_book)
    borrow_button.pack(pady=10)

    add_manual_button = tk.Button(root, text="Gestionnaire liste de livre", command=fenetre_livres_gestion)
    add_manual_button.pack(pady=10)

    show_info_button = tk.Button(root, text="Voir les informations d'un livre", command=show_book_info)
    show_info_button.pack(pady=10)
    
    show_reservations_button = tk.Button(root, text="Afficher les emprunts", command=show_reservations)
    show_reservations_button.pack(pady=10)
    
    reload_button = tk.Button(root, text="Reload les listes", command=reload)
    reload_button.pack(pady=10)
    
    root.mainloop()

def minidoc_ui():
    global root, opens, admin
    opens = 1
    admin = 0
    
    root = tk.Tk()
    root.title("Interface Minidoc")

    borrow_button = tk.Button(root, text="Gestionnaire d'emprunts", command=borrow_or_return_book)
    borrow_button.pack(pady=10)

    add_manual_button = tk.Button(root, text="Gestionnaire de livre", command=fenetre_livres_gestion)
    add_manual_button.pack(pady=10)

    show_reservations_button = tk.Button(root, text="Afficher les emprunts", command=show_reservations)
    show_reservations_button.pack(pady=10)
    
    show_info_button = tk.Button(root, text="Voir les informations d'un livre", command=show_book_info)
    show_info_button.pack(pady=10)
    
    reload_button = tk.Button(root, text="Reload les listes", command=reload)
    reload_button.pack(pady=10)

    root.mainloop()

def user_interface():
    global aut, root, opens, admin
    opens = 0
    admin = 0
    aut.destroy()
    root = tk.Tk()
    root.title("Interface Utilisateur")

    borrow_button = tk.Button(root, text="Gestionnaire d'emprunts", command=borrow_or_return_book)
    borrow_button.pack(pady=10)

    show_info_button = tk.Button(root, text="Voir les informations d'un livre", command=show_book_info)
    show_info_button.pack(pady=10)
    
    root.mainloop()

# Début du programme
authentication()
