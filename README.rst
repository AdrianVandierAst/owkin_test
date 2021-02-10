Test Owkin Adrian Vandier Ast
================================

Le but est de réaliser une API qui permet une analyse et une execution asynchrone d'un dockerfile en environment sécurisé.
Le projet sera en python et utilisera poetry pour la gestion des dépendances et du virtualenv.

Nous allons utiliser flask et celery pour l'api et les jobs asynchrones parcequ'ils sont simples et flexibles. En première approche, c'est suffisant.
L'api se basera sur des jobs donc il ne sera pas utile d'utiliser un serveur asynchrone (asyncio/Fastapi), un serveur web classique en WSGI est suffisant.

Il n'y a que le statut du job ainsi qu'un résultat à conserver donc une base de données relationelle n'est pas utile.
Nous utiliserons un redis comme broker et comme backend pour les résultats.
Un passage à rabbitmq ou autre backend spécialisé dans les queues pourra se faire si les performances deviennent un critère et qu'on doit scaler.

On écrira le contenu du dockerfile dans le contenu de la task celery. Ils seraient plus propre d'enregistrer de manière séparé le dockerfile (dans une autre instance de redis par exemple) afin de pouvoir le chiffrer facilement.
L'infra se composera d'au moins un serveur Web, d'un worker celery et du serveur redis.

Le worker celery pourra être placé sur une machine où on peut facilement gêrer la sécurité. Le seul accès nécessaire est un accès au serveur redis et un accès à un environment docker sécurisé.

L'api sera en REST pour que ce soit simple d'utilisation. Nous n'utiliserons pas de package python dédié pour ça, les routes et réponses sont très simples, un simple marshmallow pour gérer la sérialisation/déserialisation sera suffisant.

L'api et le worker sont stateless donc duplicables. Le point central de frein pour la scalabilité de la solution sera les serveurs de backend pour celery (redis fera l'affaire pour le moment).
Ce projet ne gérera pas la partie authentification et limitation des appels. On part du principe qu'un serveur dédié à authentifier les appels et à les limiter si besoin se trouvera en frontal.

Les tests automatisés de cette partie seront réalisé avec pytest et un environment de developpement basé sur des dockerfile et un docker-compose.
Les tests seront des tests d'intégration basés sur des appels d'api. Les tests unitaires pour ce genre de projet sont plus encombrant que pratique.

Une partie importante du projet est l'analyse des vulnérabilités d'un dockerfile et le run du container pour récupérer un résultat.
Cette partie pourrait être réalisé en parallèle dans le cadre d'un travail d'équipe. Une première étape serait de faire un état de l'art pour savoir comment réaliser proprement cet objectif.

Une recherche rapide sur internet (https://www.grottedubarbu.fr/docker-scan-vuln-container/) nous donne quelques outils. Nous allons utiliser trivy en mode containerisé pour faire l'analyse dans un premier temps.
Le dockerfile pour trivy sera récupéré depuis le répo dockerhub. Il faudrait s'assurer que l'image est à jour au niveau de se base de vulnérabilités et que l'image est bien la bonne pour éviter qu'il y ait des vulnérabilités dans notre outil de detection de vulnérabilités...
Le lancement de trivy ainsi que le build et le run du dockerfile seront réalisé avec docker-py pour commander l'infra docker depuis python.
Il faudra faire attention aux collisions de nom pour tout ce qui est créé en local. Il faudra également éviter que les différents runs des image docker utilisent le même dossier data pour la même raison.

La structure du projet:
-----------------------
Le projet se base sur poetry, il y a donc un pyproject.toml et un poetry.lock.

Le dossier infra contient les définitions des fichiers utiles pour générer l'infra (des placeholders pour le moment).
Ce n'est pas que pour ce projet, je trouve ça utile que la définition de l'infra soit proche du code car les deux sont fortements liés. Et avec tout ce qui existe pour faire de l'infra-as-code, ce n'est pas un soucis.

Le dossier owkin_test est le dossier contenant le code du projet.
app.py correspond à la création de l'app flask et la définition des routes pour l'api.
tasks.py contient le code pour la tâche asynchrone.
Le reste est de la glue pour faire fonctionner tout ça ensemble. La structure est extrêmement basique, elle mériterait de l'amélioration pour être plus facilement extensible.
Mais ce serait à faire au moment où ce projet commencerait à avoir plus de route et de service pour éviter le travail inutile et pour le faire en connaissance de cause.

Le dossier test comprend les tests avec le formalisme de pytest et un docker-compose utile pour simplifier le lancement de l'infra de test.

Ce qu'il reste à faire:
------------------------
- Écrire des dockerfile basique pour l'api et le worker afin de pouvoir lancer les tests.
- Finaliser le docker-compose pour qu'il utilise les bonnes images. Potentiellement, ajouter la possibilité de builder automatiquement les images depuis le docker-compose pour simplifier d'autant le lancement des tests.
- Lancer les tests et corriger ce qui est mal codé
- Finir d'écrire la fonction analyse_trivy_results.
- Écrire plus de cas de tests: dockerfile mal formé, dockerfile avec vulnérabilité, dockerfile qui ne créé pas bien le perf.json, etc...
- Mettre en place une gestion de conf un peu plus correcte: utiliser python-dotenv. Le mieux reste d'avoir le moins de configuration possible et que le maximum de chose soit créé à la volée. Il y a au minimum le backend/broker redis à configurer.
- Mettre en place la gestion HTTP nécessaire pour respecter les standards de sécurité actuels (flask-cors fait bien le travail).
- Ajouter un peu de CI: lancement de black et des tests dans une pipeline git.
- Préparer des dockerfiles pour la production (en fonction de l'infra cible, écrire des fichier kubernetes). Utiliser un autre serveur HTTP que celui de base dans flask.
- Ajouter des logs à chaque appels de l'api ainsi qu'à chaque execution de jobs.
- Ajouter une propagation d'un correlation-Id entre les appels à l'api et les jobs afin de pouvoir identifier facilement le cheminement dans les logs.
- Il faut déterminer si on a le droit de conserver les dockerfile. Si jamais il y a un bug, il nous permettrait de plus facilement reproduire le problème.
- Pour que la mise en production se passe bien, il faudra penser à connecter le monitoring de l'infra et la récupération des logs.
- Réfléchir plus longuement à la sécurité du système: donne-t-on trop de droit à un container, la suppresion du network suffit il à avoir un env docker sécurisé, la base de vulnérabilité de triby est elle à jour quand on procède comme on l'a fait,
    a-t-on une image trivy en laquelle on peut avoir confiance, le build d'une image utilisant un dockerfile non maitrisé est il une faille de sécurité et comment valider le contenu du dockerfile avant ce build.
- Ajouter une gestion d'erreur et de sérialisation/déserialisation des objets de l'api et des réponses des tasks plus propre.
- Ajouter une lib pour la génération automatique de la documentation openapi (flasgger par exemple).
- Ajouter un vrai README de description du projet et des différentes commandes pour lancer les tests, etc.
