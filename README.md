# Ccomptes

Une interface simple pour rechercher et consulter les rapports de la Cour des comptes.

# Déploiement sur un serveur

## Préparation
Installation des différents paquets:
```
apt-get update
apt-get upgrade
apt-get install nginx git python-pip mongodb
pip install --upgrade pip
```

## Installation depuis Github
Installer de ccomptes depuis Github dans le dossier `deploy`:
```
mkdir ~/deploy && cd ~/deploy
git clone https://github.com/eig-2017/api-ccomptes.git
cd api-ccomptes/
python setup.py install
```

## Elasticsearch
Installer Java :
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
java -version
```

Installer Elasticsearch :
```
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.6/elasticsearch-2.4.6.deb
sudo dpkg -i elasticsearch-2.4.6.deb
```

Installer le plugin `analysis-icu` :
```
/usr/share/elasticsearch/bin/plugin install analysis-icu
```

Lancer Elasticsearch :
```
sudo systemctl enable elasticsearch.service
sudo systemctl start elasticsearch
```


## Prépartion des données et lancement du serveur
Charger les données depuis `data.csv`:
```
ccomptes load data.csv
```

Compiler les fichiers statiques:
```
ccomptes static
```

Indexer dans Elasticsearch:
```
sudo ccomptes reindex
```

Lancer le serveur:
```
sudo ccomptes runserver
```

TODO : passer à une configuration uwsgi + nginx


## Modifier les données
Générer le fichier data.csv avec grâce aux fichiers HTML dans `data` :
```
pip install -r requirements/create-csv.pip
python create-csv.py
```

Mettre à jour la base mongodb et Elasticsearch :
```
mongo ccomptes --eval "db.dropDatabase()"
ccomptes load data.csv
sudo ccomptes reindex
```


#Note
Fork du projet [Cada d'Etalab](https://github.com/etalab/cada)
