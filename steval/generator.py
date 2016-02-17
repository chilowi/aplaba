#! /usr/bin/env python3
"""
Offer some useful functions to generate input data
"""

DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

import range

def generate_random_sequence(length, alphabet = DEFAULT_ALPHABET):
	rand = lambda: random.randrange(0, length)
	return map(DEFAULT_ALPHABET[rand()], range(0, length))
	
def generate_random_string(length, alphabet = DEFAULT_ALPHABET):
	return "".join(generate_random_sequence(length, alphabet))
	

