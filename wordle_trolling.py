"""
This program is to help people with linguistic difficulties
to play games such as wordle. It is not intended to be used
for mischief. 

HAHAHAHAAHAH just kiding! This is just to piss off
Fredrik Hagström!!!!
"""

import os
from urllib import request
import itertools

if not os.path.isfile('count_1w.txt'):
    request.urlretrieve(
        "https://norvig.com/ngrams/count_1w.txt",
        "count_1w.txt")

def get_letter_counts(word):
    result = dict()
    for c in word:
        result[c] = result.get(c, 0) + 1
    return result


with open('count_1w.txt') as file:
    five_letter_words = list(itertools.islice((
        (word, get_letter_counts(word)) for word, _ in (line.strip().split('\t') for line in file)
        if len(word) == 5), 10000))

def get_hints(target_word, letter_counts, guess):
    green_counts = dict()
    for position, guess_letter in enumerate(guess):
        if target_word[position] == guess_letter:
            green_counts[guess_letter] = green_counts.get(guess_letter, 0) + 1

    available_for_yellow = {letter: count - green_counts.get(letter, 0) for letter, count in letter_counts.items()}

    for position, guess_letter in enumerate(guess):
        if guess_letter in target_word:
            if target_word[position] == guess_letter:
                yield 'g', position, guess_letter
            else:
                if available_for_yellow[guess_letter] > 0:
                    available_for_yellow[guess_letter] -= 1
                    yield 'y', position, guess_letter
                else:
                    yield '.', position, guess_letter
        else:
            yield '.', position, guess_letter

def next_guesses(word_list, hints):
    counted_hint_letters = dict()
    print(hints)

    for hint_type, position, letter in hints:
        counted_hint_letters[letter] = counted_hint_letters.get(letter, 0) + 1

    for word, letter_counts in word_list:
        in_list = True

        for hint_type, position, letter in hints:

            if hint_type == 'g' and word[position] != letter:
                in_list = False

            if hint_type == 'y' and (word[position] == letter
                                     or letter_counts.get(letter, 0) < counted_hint_letters[letter]):
                in_list = False

            if hint_type == '.' and letter_counts.get(letter, 0) > counted_hint_letters.get(letter, 0):
                in_list = False

        if in_list:
            yield word, letter_counts

def play(target_word, best_guess_f):
    word_list = five_letter_words
    target_word_letter_counts = get_letter_counts(target_word)

    for turn_count in itertools.count(1):
        next_guess = best_guess_f(word_list)

        hints = list(get_hints(target_word, target_word_letter_counts, next_guess))
        
        yield turn_count, next_guess, hints

        if all(hint_type == 'g' for hint_type, _, _ in hints):
            return

        word_list = list(next_guesses(word_list, hints))

def most_popular(guesses):
    return guesses[0][0]

def by_letter_and_position_frequency(guesses):
    by_position_and_letter = dict()
    for word, _ in guesses:
        for position, letter in enumerate(word):
            by_position_and_letter[(position, letter)] = by_position_and_letter.get((position, letter), 0) + 1

    return max(((word, sum(by_position_and_letter.get((position, letter), 0)
                           for position, letter in enumerate(word)))
                for word, _ in guesses), key = lambda t: t[1])[0]

def play_as_guesser(best_guess_f):
    word_list = five_letter_words
    initial_guess = True
    while True:
        if initial_guess:
            word = input("Guess the first word: ")
            initial_guess = False
        else:
            word = best_guess_f(word_list)
        for i in range(len(word_list) - 1):
            if word_list[i][0] == word:
                del word_list[i]
                
        print("Try:", word)
        hint_str = input("Type result as string of hints (g for green, y for yellow, . for grey): ")
        if hint_str == 'ggggg':
            break
        hints = [(h, i, word[i]) for i, h in enumerate(hint_str)]
        word_list = list(next_guesses(word_list, hints))

play_as_guesser(by_letter_and_position_frequency)