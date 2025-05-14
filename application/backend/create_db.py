import sqlite3

# Connexion à la base de données (elle sera créée si elle n'existe pas)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Création de la table users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user')),  -- rôle limité à admin ou user
        bloc BOOLEAN NOT NULL DEFAULT 0,
        tokenAuth TEXT,
        tokenAuthExpires DATE,
        is_verified BOOLEAN NOT NULL DEFAULT 0  -- Ajout du champ pour savoir si l’email a été vérifié
    )
''')

# Valider et fermer la connexion
conn.commit()
conn.close()

print("Table users créée avec succès.")
