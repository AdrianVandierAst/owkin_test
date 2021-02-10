Test Owkin Adrian Vandier Ast

Le but est de réaliser une API qui permet une analyse et une execution asynchrone d'un dockerfile en environment sécurisé.
Nous allons utiliser flask et celery pour l'api et les jobs asynchrones parcequ'ils sont simple et flexible. En première approche, c'est suffisant.
L'api se basera sur des jobs donc il ne sera pas utile d'utiliser un serveur asynchrone, un serveur web classique en WSGI est suffisant.
Il n'y a que le statut du job ainsi qu'un résultat à conserver donc une base de données relationelle n'est pas utile.
Nous utiliserons un redis comme backend de queue et comme backend pour les résultats.
Un passage à rabbitmq ou autre backend spécialisé dans les queues pourra se faire si les performances deviennent un critère et qu'on doit scaler.
On écrira le contenu du dockerfile dans le contenu de la task celery. Ils seraient plus propre d'enregistrer de manière séparé le dockerfile (dans une autre instance de redis par exemple) afin de pouvoir le chiffrer facilement.
L'infra se composera d'au moins un serveur Web, d'un worker celery et du serveur redis.
Le worker celery pourra être placé sur une machine où on peut facilement la sécurité. Le seul accès nécessaire est un accès au serveur redis et un accès à un environment docker sécurisé.
L'api sera en REST pour que ce soit simple d'utilisation. Nous n'utiliserons pas de package python dédié pour ça, les routes et réponses sont très simples, un simple marshmallow pour gérer la sérialisation/déserialisation sera suffisant.
L'api et le worker sont stateless donc duplicables. Le point central de frein pour la scalabilité de la solution sera les serveurs de backend pour celery (redis fera l'affaire pour le moment).
Ce projet ne gérera pas la partie authentification et limitations des appels. On part du principe qu'un serveur dédié à authentifier les appels et à les limiter si besoin se trouvera en frontal.

Les tests automatisés de cette partie seront réalisé avec pytest et un environment de developpement basé sur des dockerfile et un docker-compose.

Une partie importante du projet est l'analyse des vulnérabilités d'un dockerfile et le run du container pour récupérer un résultat.
Cette partie pourrait être réalisé en parralèle dans le cadre d'un travail d'équipe. Une première étape serait de faire un état de l'art pour savoir comment réaliser proprement cet objectif.
Une recherche rapide sur internet (https://www.grottedubarbu.fr/docker-scan-vuln-container/) nous donne quelques outils. Nous allons utiliser trivy en mode containerisé pour faire l'analyse dans un premier temps.
Le dockerfile pour trivy sera récupéré depuis le répo dockerhub. Il faudrait s'assurer que l'image est à jour au niveau de se base de vulnérabilités et que l'image est bien la bonne pour éviter qu'il y ait des vulnérabilités dans notre outil de detection de vulnérabilités...
Le lancement de trivy ainsi que le build et le run du dockerfile seront réalisé avec docker-py pour commander l'infra docker depuis python.
Il faudra faire attention aux collisions de nom pour tou ce qui est créé en local. Il faudra également éviter que les différents run des image docker utilise le même dossier data pour la même raison.


Monitoring de la solution:
Ajouter des logs à chaque appels de l'api ainsi qu'à chaque execution de jobs.
Ajouter une propagation d'un correlation-Id entre les appels à l'api et les jobs afin de pouvoir identifier facilement le cheminement dans les logs.
Il faut déterminer si on a le droit de conserver les dockerfile. Si jamais il y a un bug, il nous permettrait de plus facilement reproduire le problème.
Pour que la mise en production se passe bien, il faudra penser à connecter le monitoring de l'infra et la récupération des logs.
