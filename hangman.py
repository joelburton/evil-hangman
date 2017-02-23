"""Evil Hangman.

Hangman, except avoid choosing a real word and, on a letter guess, reduce
the set of possible words to the set that gives the player as little
advantage as possible.

Interestingly, it gets much easier with longer words --- most people can
win with words of ~11 length and 10 tries, but even with computer-generated
optimal play, it's impossible to win with words of <6 length and 10 tries.

Joel Burton <joel@joelburton.com>
"""

import sys
import collections
import random

if sys.version_info.major == 2:
    # be compatible with both Python 2 and Python 3
    input = raw_input


def debug(*items):
    """Optionally print debug messages."""

    if "--debug" in sys.argv:
        print("\n" + " ".join(str(s) for s in items) + "\n")


def prompt_int(prompt, default):
    """Prompt user for an integer answer."""

    while True:
        n = input(prompt) or default

        try:
            return int(n)

        except ValueError:
            print("you seem unclear on what numbers are!")


def get_words(words_file_path):
    """Get list of words."""

    with open(words_file_path) as words:
        words = [w.strip() for w in words]

    min_len = min(len(w) for w in words)
    max_len = max(len(w) for w in words)
    suggest = min(max_len, 5)

    prompt = "what length word do you want (%s-%s) [%s] > " % (min_len, max_len, suggest)
    word_len = prompt_int(prompt, default=suggest)

    return [w.lower() for w in words if w.isalpha() and len(w) == word_len]


def update_words(legal_words, ltr):
    """Update list of candidate words.

    This is the core of the "evil" part --- it looks at the possible words and
    the letter the user guessed and updates the list of possible words so as to
    main the largest number of possible words.

    A good introduction to this algorithm is at
    http://www.keithschwarz.com/cs106l/spring2010/handouts/020_Assignment_1_Evil_Hangman.pdf

    Inputs:

    - words: list of candidate words that are still legal
    - ltr: letter the user has guessed

    Returns:

    - legal_words: new list of candidate words that are still legal
    """

    # group words in dict by 'family' (key is tuple-of-indices-where-letter-appears)
    # for example, if words=[FOO OFF MOO ORE CAT DOG] & ltr=O, our families will be:
    #   { (1,2): [FOO MOO], (0): [OFF ORE], (1): [DOG], (): [CAT] }

    families = collections.defaultdict(list)

    for word in legal_words:
        idxs = [i for i, c in enumerate(word) if ltr == c]
        families[tuple(idxs)].append(word)

    debug("families:", families)

    # find #-words of families with longest-list-of-words (in our example above, 2)
    longest_fam_len = max(len(f_words) for f_words in families.values())

    debug("longest_fam_len:", longest_fam_len)

    # find all families w/ that word length ( (1,2):[FOO MOO] and (0):[OFF ORE] )
    longest_fams = [(f_idxs, f_words)
                    for f_idxs, f_words
                    in families.items()
                    if len(f_words) == longest_fam_len]

    debug("longest_fams:", longest_fams)

    # choose family that uses chosen letter the fewest # of times ([OFF ORE])
    fams_with_fewest_match = sorted(longest_fams, key=lambda f: len(f[0]))

    debug("fams_with_fewest_match:", fams_with_fewest_match)

    fam_with_fewest_match = random.choice(fams_with_fewest_match)

    debug("fam_with_fewest_match:", fam_with_fewest_match)

    _, legal_words = fam_with_fewest_match

    # now legal_words is list of words that are still legal
    # print("still legal words:", legal_words)

    return legal_words


def play(words_file_path):
    """Play evil hangman."""

    words = get_words(words_file_path)

    nguesses_left = prompt_int("how many guesses do you want [10] > ", default=10)

    guessed_letters = set()

    while True:

        # cheat: tell us what letters would be best to choose
        # print("best letters to choose & counts", collections.Counter(
        #     c for w in words for c in set(w) - guessed_letters).most_common(3))

        ltr = input("\nguess a letter (%d guesses left) > " % nguesses_left).lower()

        if len(ltr) != 1:
            print("zomg, calm down --- only one letter at a time!")
            continue

        if ltr in guessed_letters:
            print("pay attention --- you already guessed that!")
            continue

        guessed_letters.add(ltr)

        words = update_words(words, ltr)

        # to make the next parts easier to read, let's just arbitrarily pick the first
        # word from our still-legal words. we're not committing to it; just using it
        # so we can check for letter-in-legal-words and to draw-the-success-so-far line.
        #
        # (note that it's not possible for words to be empty --- if it were, that would
        # mean the player would have already won)
        word = words[0]

        if ltr in word:
            print("correct")
            if not set(word) - guessed_letters:  # are there no missing letters?
                print("\n\n *** you rock *** \n")
                break

        else:
            print("wrong")
            nguesses_left -= 1
            if nguesses_left == 0:
                print("\n\n *** you suck *** \n")
                break

        print(" ".join(c if c in guessed_letters else "_" for c in word))
        print("guessed: %s" % " ".join(sorted(guessed_letters)))

    print("word was: %s" % word)


if __name__ == '__main__':
    print("\n *** Welcome to Happy Easy Fun-Time Hangman! *** \n")

    harder = "--harder" in sys.argv

    if not harder:
        print("To make things easy, I use only the most common English words! \n")
        print("For a much bigger word list, run this with the --harder option! \n")

    play("/usr/share/dict/words" if harder else "words.txt")
