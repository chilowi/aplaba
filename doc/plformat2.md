= Proposition d'évolution du format pl =

Voici quelques idées pour l'évolution du format PL afin d'introduire plus de flexibilité dans son utilisation.

== Dictionnaire ==

Le fichier doit définir un dictionnaire de clé/valeur en utilisant la syntaxe ``clé=valeur`` ou ``clé==valeur==`` si la valeur est sur plusieurs lignes.

Il serait utile de séparer les clés spéciales (que l'on pourrait introduire par un caractère spécifique comme @) des clés ajoutées par l'utilisateur pour paramétrer le fonctionnement de l'exercice.

== Héritage ==

Il est possible d'hériter d'un dictionnaire provenant d'un autre fichier PL en utilisant la clé ``@template`` avec pour valeur le chemin vers le fichier hérité (absolu sur le repository GIT ou relatif).

== Tags ==

Il est possible d'ajouter des tags avec des clés préfixées par //tag_// (on peut indiquer plusieurs tags dans une même entrée séparés par des virgules. Les tags correspondent aux notions de l'ontologie. Ils sont également utilisés par le wiki de discussion des sujets.

== Expressions substituables ==

Pour permettre la génération d'exercices programmatiquement, nous pourrions introduire des expressions évaluables à l'intérieur des valeurs du dictionnaire.

Proposition de syntaxe : ``$nomVariable`` ou ``${expression}`` (correspond à la syntaxe proposée par défaut par [string.template https://docs.python.org/3/library/string.html#template-strings] en Python). Pour déspécialiser le caractère $, on le double.

Le principe de fonctionnement est le suivant :
* On parse le fichier PL
* On ajoute dans le dictionnaire //vars// les entrées du dictionnaire hérité
* On ajoute les entrées du dictionnaire courant (qui peuvent masquer les entrées du dictionnaire hérité)
* On exécute du code Python ajouté par le rédacteur (dont la spécification est facultative) : ce code a pour objectif d'effectuer si nécessaire d'autres modifications sur le dictionnaire //vars//
* On réalise ensuite la substitution des valeurs de vars en utilisant ``string.template```. 
	* Pour une valeur de type ``$nomVariable`` on substitue par ``vars["nomVariable"]``.
	* Pour une expression Python ``${expr}``, on réalise un exec de l'expression pour récupérer la valeur évaluée. Cela implique également que cette étape de génération doit être réalisée dans un environnement sécurisé. Si une valeur ne contient que ``${expr}`` celle-ci n'est pas convertie en str, la valeur est conservée telle quelle (cela permet d'avoir dans le dictionnaire des fonctions, classes... Python).
	
Pour simplifier, on suppose que les valeurs sont substituées dans l'ordre de leur déclaration (on pourrait également faire un tri topologique avec un graphe de dépendance mais cela serait beaucoup plus compliqué, surtout pour les expressions Python où il est difficile de déterminer les dépendances sur d'autres entrées). Donc il faut veiller à utiliser un ``OrderedDict`` pour stocker les entrées.

Quel comportement adopter pour les entrées inexistantes ou les expressions invalides ?
	* Soit retourner None
	* Soit lever une exception (dans ce cas l'exercice ne peut être généré). Cette dernière approche doit être probablement privilégiée.
	
Pour illustrer cela, voici un petit exemple d'exercice.

D'abord un template pour demander de calculer quelque chose sur une liste :

```
@title=Calcul de $listPropertyName d'une liste
text==
Ecrire une fonction qui prend en paramètre une liste et qui retourne $listProperty de cette liste.
==
test==
@test_function(params=generate_random_lists(int))
def test(l):
	vars["listPropertyExpr"](l)
==
```

Et voici maintenant un fichier pour calculer la somme des éléments de la liste :

```
@template=listProperty.pl
@listPropertyName=la somme des éléments
@listPropertyExpr=${sum}
```

Maintenant si l'on veut demander de calculer la moyenne des éléments de la liste, c'est un peu plus compliqué puisqu'il n'y a pas de fonction //moyenne// préexistantes dans les fonctions builtins Python. Il suffit alors d'indiquer du code dans pregenerate qui sera préchargé lors de la génération du dictionnaire :

```
@template=listProperty.pl
@listPropertyName=la moyenne des éléments
@pregenerate==
def avg(l):
	return sum(l) // len
==
@listPropertyExpr=${avg}
```

Pour généraliser, on peut dire que le sujet est créé par un générateur que l'on peut indiquer avec la clé ``@generator``. Il s'agit du chemin (paquetage + nom de fonction) vers un callable prenant en paramètre le dictionnaire et retournant un dictionnaire éventuellement modifié. On pourrait donc écrire des generators qui se comportent différemment par rapport à ce qui a été décrit ici (qui est le generator par défaut avec un certain mode de substitution d'expressions).

La question qui se pose également concerne la liaison avec une vue HTML permettant de fournir une réponse. La vue par defaut la plus simple consiste à fournir un //textarea// où rentrer une réponse. Il faudra sans doute proposer quelque chose un composant plus sophistiqué avec un peu de JavaScript pour faciliter l'édition de texte, proposer éventuellement du //syntax highlighting//...

Il faut également considérer le cas où la réponse peut être entrée sous la forme de boutons radio ou cases à cocher. On peut même imaginer un mode hybride avec plusieurs types de réponses...

Voici par exemple un exercice pour réviser une table de multiplication avec une proposition de listes de réponses :

```
@generator=pl.quizz.quizz_generator
@pregenerate==
import random
vars["operand1"] = random.nextInt(2,12)
vars["operand2"] = random.nextInt(2,12)
vars["expectedResult"] = vars["operand1"] * vars["operand2"]
k = min(random.nextInt(0,9), vars["expectedResult"] - 1)
for i in range(0, 10):
	vars["proposition_{}".format(i)] = vars["expectedResult"] - k + i
@text==
Combient font $operand1 fois $operand2 ?
==
```

Nous avons défini dans //@pregenerate// programmatiquement les entrées du dictionnaire. Les différentes entrées //proposition_X// indiquent 10 propositions qui peuvent être représentées avec un groupe de boutons radio.

== Évaluateur ==

Le format ne doit pas être limité à des évaluations de code Python. Il faut également pouvoir supporter d'autres langages, voire des quizz à choix multiples ou à réponse ouverte en langue naturelle.

Il faut donc que l'on puisse disposer de plusieurs types de grader. L'idée serait d'utiliser la clé ``@grader`` pour indiquer le grader à utiliser qui serait le nom d'une callable Python préfixée par son paquetage. Il y aurait un paquetage Python préinstallé sur le container d'exécution avec les graders les plus courants. Il serait bien aussi que les rédacteurs des exercices puissent installer ce paquetage sur leur machine pour tester en local leurs exercices avant de les soumettre.

Pour des besoins personnalisés d'évaluation, on pourrai utiliser un grader spécifique de son cru. Pour cela, on pourrait importer un répertoire avec les sources de son grader présent dans le repository courant avec :
```
@import=/path/to/the/repository/with/my/grader
```

Remarque : l'import peut également fonctionner pour la génération d'énoncé (on copie dans le container le répertoire avant la génération et avant le test avec le grader).

Le grader est un callable qui prend deux arguments :
* Le dictionnaire avec les entrées de l'énoncé
* La réponse de l'étudiant. Cette réponse peut être un str ou alors un dictionnaire (utile par exemple pour un QCM).

Le grader répond par un dictionnaire avec des entrées diverses.
Remarque : il serait intéresser d'avoir un module stockant dans des fichiers ou une BDD toutes les réponses d'étudiant.

