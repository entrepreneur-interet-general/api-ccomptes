# Partie 1 : récupération des données
![architecture1](https://github.com/eig-2017/api-ccomptes/blob/master/doc/architecture1.svg)

**1. Le script `scrap-docjf.py` :**

* Se connecte à la base de données documentaire DocJF.
* Télécharge les rapports en formats `.docx` dans le dossier `data`. Le format `.docx` est le seul accepté par le script ; les fichiers en `.pdf` ne sont pas téléchargés. Le dossier `data` est créer s'il n'existe pas.
* Génère un fichier appelé `metadonnes.csv` qui contient des informations sur les rapports téléchargés. Ces informations proviennent des fiches descriptives de DocJF. 

Spécifications du fichier `metadonnes.csv` :

* Colonnes et types :

| Clé Flora | Date du document | Nombre de fichier sauvegardé | Titre | Type document | Juridiction | Entité Productrice (TODO: remove) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `int` | `date` (dd/mm/yyyy) | `int` | `string` | `string` | `string` | `string`|

* Encodage : `ISO-8859-1` (quand le script est lancé depuis Windows).
* Séparateur : `;`


**2. Le script `convert-docx.py` :**

* Ouvre tous les fichiers en format `.docx` présents dans le dossier `data`.
* Transforme le format `.docx` en format `.html`.
* Enregistre les fichiers en format `.html` dans le même dossier.

**3. Le script `create-csv.py` :**

* Ouvre tous les fichiers en format `.html` dans le dossier `data` et ouvre le fichier `metadonnes.csv`.
* Modifie les fichiers `.html` en enlevant notamment la partie `<head>`.
* Crée une version simplifié du rapport qui sera utilisée pour l'indexage appelé `Texte index`. Pour créer cette version, le `.html` est purgé de toutes les balises (`<div>`, `<table>`, `<p>`, etc.), purgé d'une liste de mots vides (`le`, `la`, `du`, etc.) et seuls les 30000 premiers caractères sont conservés (si on tente d'indexer le rapport entier, on a [cette erreur](https://stackoverflow.com/questions/24019868/utf8-encoding-is-longer-than-the-max-length-32766)). Cette version simplifié sera utilisé pour indexer les rapports dans Elasticsearch, afin de respectant les limites en terme de taille de donnée.
* Génère un fichier appelé `data.csv` qui contient l'ensemble des rapports en `html`, l'ensemble des rapports simplifiés et d'autres métadonnées.

Spécifications du fichier `data.csv` :

* Colonnes et types :

| Numéro de dossier | Juridiction | Type | Année | Publication | Objet | Thème et sous thème | Mots clés | Rapport | Texte index | 
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `int` | `string` | `string` | `data` (yyyy) | `data` (dd/mm/yyyy) | `string` | `string`| `string`| `string`| `string`|

* Encodage : `utf-8`.
* Séparateur : `,`


# Partie 2 : lancement de l'API
![architecture2](https://github.com/eig-2017/api-ccomptes/blob/master/doc/architecture2.svg)

**4. La commande `ccomptes load "data.csv"` :**

* Charge les données stockées dans le fichier `data.csv`.
* Stock les données dans une base de données `mongoDB`.
* Si le chargement est effectif, les lignes suivantes sont imprimées :
```
Loading data.csv
..........................
Processed n rows
```

**5. La commande `ccomptes reindex` :**

* Indexe les données contenues dans la base de données `mongoDB` dans le moteur de recherche `Elasticsearch`.
* Si l'indexation est effective, les lignes suivantes sont imprimées :
```
Deleting index ccomptes
..........................
Indexed 26 reports
```

**6. La commande `ccomptes runserver` :**

* Lance le serveur de développement de Flask.
* Si le lancement est effectif, les lignes suivantes sont imprimées :
```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: ***-***-***
```

# Autre

* Pour effacer la base de données `mongoDB` : `mongo ccomptes --eval "db.dropDatabase()"`
