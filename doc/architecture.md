
1. Le script `scrapdocjf.py` :

* Se connecte à la base de données documentaire DocJF.
* Télécharge les rapports en formats `.docx` dans le dossier `data`. Le format `.docx` est le seul accepté par le script ; les fichiers en `.pdf` ne sont pas téléchargés. Le dossier `data` est créer s'il n'existe pas.
* Génère un fichier appelé `metadonnes.csv` qui contient des informations sur les rapports téléchargés. Ces informations proviennent des fiches descriptives de DocJF. Les colonnes du fichier `metadonnes.csv` sont : info1 | info2 | info3. Le format attendu dans chaque colonne est : info1 : `string` | info2 : `string` | info3 : `int`. L'encodage utilisé est `ISO-8859-1` quand le script est lancé depuis Windows.

2. Le script `word_converter.py` :
* Ouvre tous les fichiers en format `.docx` présents dans le dossier `data`.
* Transforme le format `.docx` en format `.html`.
* Enregistre les fichiers en format `.html` dans le même dossier.

3. Le script `create-csv.py` :
* Ouvre tous les fichiers en format `.html` dans le dossier `data` et ouvre le fichier `metadonnes.csv`.
* Modifie les fichiers `.html` en enlevant notamment la partie `<head>`.
* Crée une version simplifié du rapport qui sera utilisée pour l'indexage appelé `Texte index`. Pour créer cette version, le `.html` est purgé de toutes les balises (`<div>`, `<table>`, `<p>`, etc.), purgé d'une liste de mots vides (`le`, `la`, `du`, etc.) et seuls les 30000 premiers caractères sont conservé. Cette version simplifié sera utilisé pour indexer les rapports dans Elasticsearch, afin de respectant les limites en terme de taille de donnée.
* Génère un fichier appelé `data.csv` qui contient l'ensemble des rapports en `html`, l'ensemble des rapports simplifiés et d'autres métadonnées. Les colonnes du fichier `data.csv` sont : info1 | info2 | info3. Le format attendu dans chaque colonne est : info1 : `string` | info2 : `string` | info3 : `int`. L'encodage utilisé est `utf-8`.
