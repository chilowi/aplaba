template=template.pl
title=Tri récursif
author=chilowi
taboo=sort,sorted
text==
Écrivez une fonction nommée //tidy// qui trie une liste d'éléments par n'importe quel moyen.

Attention, vous n'avez pas le droit d'utiliser la méthode sort ou la fonction globale sorted. Il faut donc implanter soi-même un algorithme de tri.
On impose une contrainte supplémentaire : l'usage de boucles while ou for est interdit. Il faut ainsi utiliser systématiquement la récursion et //filter//.
==
soluce==
# An answer using a quicksort
def tidy(x):
	if len(x) == 0: 
		return []
	elif len(x) == 1:
		return x
	else:
		pivot = x[len(x)/2] # arbitrary pivot
		a = filter(lambda e: e <= pivot, x)
		b = filter(lambda e: e > pivot, x)
		return tidy(a) + tidy(b)
==
tester==
import executor
args = [ generate_random_sequence(alphabet, x) for x in range(0, 128) ]
executor.ExecutionEnvironments().test_results("tidy", *args)
==
	

