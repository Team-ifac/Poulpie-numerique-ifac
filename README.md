# Ressourcerie IFAC – guide rapide

Ce projet fournit une ressourcerie pédagogique complète en Python/SQLite (sans dépendances externes) avec authentification, rôles ADMIN/USER, catalogue filtrable et interface d’administration.

## Prérequis
- Python 3.10+ installé
- Aucune installation de dépendances n’est nécessaire (tout est dans `app.py`).

## Lancer le site en local
1. Depuis la racine du dépôt, exécutez :
   ```bash
   python app.py
   ```
   (optionnel) vous pouvez changer le port avec `PORT=8000 python app.py`.
2. Ouvrez le navigateur sur [http://localhost:5000](http://localhost:5000) ou le port choisi.
3. La base `data.sqlite` est créée automatiquement avec 12 ressources d’exemple (4 PUBLIC, 8 INTERNAL_IFAC) et 8 thématiques.

## Comptes et rôles
- L’inscription est libre via le bouton **Inscription**.
- Le premier compte créé devient ADMIN automatiquement et peut accéder à l’onglet **Admin**.
- Les ressources « Interne IFAC » ne sont visibles qu’après connexion.

## Fonctions principales
- Catalogue avec recherche + filtres (thématique, type, âge, durée, visibilité si connecté).
- Détail ressource avec téléchargement du PDF.
- Favoris dans **Ma bibliothèque** (utilisateur connecté).
- Espace Admin : CRUD ressources (upload vignette/PDF), thématiques, gestion des rôles utilisateurs.

## Stockage des fichiers
- Vignettes et PDF téléversés sont enregistrés dans `public/uploads/` (créé au démarrage si absent).
- Les fichiers d’exemple déjà présents sont dans `public/files/`.

## Arrêter le serveur
Appuyez sur `Ctrl + C` dans le terminal ayant lancé `python app.py`.

## Dépannage rapide
- Si le port est occupé, choisissez-en un autre : `PORT=8001 python app.py`.
- Pour repartir de zéro, supprimez `data.sqlite` et relancez `python app.py` (les données de démo sont regénérées).
