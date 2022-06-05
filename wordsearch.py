"""N-dimensional word search implementation."""

import random
import string
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, List, Tuple

import numpy as np


class WordSearchError(RuntimeError):
    """Base error class."""


class WordLengthError(WordSearchError):
    """Error with word length."""

    def __init__(self, word: str):
        if len(word) <= 1:
            msg = f'{word!r} is too short'
        else:
            msg = f'{word!r} is too long'
        super().__init__(msg)


class WordDensityError(WordSearchError):
    """Target word density reached."""

    def __init__(self):
        super().__init__('word density target reached, unable to add more')


class WordCountError(WordSearchError):
    """Target word density reached."""

    def __init__(self):
        super().__init__('word count target reached, unable to add more')


class NoMoreRetriesError(WordSearchError):
    """Target word density reached."""

    def __init__(self, word: str):
        super().__init__(f'failed to add {word}')


@dataclass
class Difficulty:
    """Difficulty settings for the word search.

    Attributes:
        level: How many directions to allow per word solution.
            A level of 1 for example will only allow horizontal/vertical.
            A level of 2 will include diagonals.
        backwards: If words can be added in reverse.
        max_words: Maximum number of words to allow.
        copy_letter_chance: Chance of choosing a new letter over an existing one.
        density_target_words: What percentage of space should be taken by words.
            Once this target is reached, the generation will stop.
            A higher value will result in a harder wordsearch.
        density_target_variations: What percentage of space should be taken by variations.
            Once this target is reached, the generation will stop.
    """
    level: int = 2
    backwards: bool = True
    max_words: int = 1
    copy_letter_chance: float = 0.15
    density_target_words: float = 0.7
    density_target_variations: float = 0.5

    def generate_direction(self, dimensions: int) -> Tuple[int]:
        """Choose a new direction based on the number of dimensions."""
        direction = [0] * dimensions
        choice = list(range(dimensions))
        for _ in range(self.level):
            idx = random.choice(choice)
            choice.remove(idx)
            direction[idx] = random.randint(-1, 1) if self.backwards else 1
        return tuple(direction)


class WordSearch(object):
    """N-dimensional wordsearch."""

    def __init__(self, size: Union[int, List[int]], dimensions: int = 2,
                 difficulty: Optional[Union[int, Difficulty]] = None) -> None:
        """Initialise the data.

        Parameters:
            size: Size of the word search grid.
            difficulty: Difficulty of the word search.
            dimensions: Number of word search dimensions.
        """
        self.dimensions = dimensions
        if isinstance(size, int):
            self.shape = [size] * dimensions
        else:
            self.shape = size

        if difficulty is None:
            self.difficulty = Difficulty()
        elif isinstance(difficulty, int):
            self.difficulty = Difficulty()
            self.difficulty.level = difficulty
        else:
            self.difficulty = difficulty

        self._data_words = np.zeros(self.shape, dtype=str)
        self._data_variations = np.zeros(self.shape, dtype=str)
        self._data_fill = np.zeros(self.shape, dtype=str).ravel()
        self.solutions: Dict[str, Tuple[Tuple[int], Tuple[int]]] = {}

        self._req_update_variation = self._req_update_fill = True

    def __str__(self):
        """Return the numpy string."""
        return self.data.__str__()

    @property
    def data(self):
        """Get the raw data as a numpy array.
        This will generate any extra data as needed.
        """
        # Regenerate the extra data
        if self._req_update_fill:
            self._generate_fill()
        if self._req_update_variation:
            self._generate_variations()

        output = self._data_words

        # Add variations
        where = np.where(output == '')
        output[where] = self._data_variations[where]

        # Add fill
        where = np.where(output == '')
        output[where] = self._data_fill.reshape(self.shape)[where]

        return output

    @property
    def words(self) -> List[str]:
        """Get a list of all words in the wordsearch."""
        return list(self.solutions)

    def _add_word(self, word: str, check_count: bool = False, check_density: bool = False,
                  retry_attempts: int = 10, placement_attempts: int = 25, direction_attempts: int = 5
                  ) -> Optional[Tuple[Tuple[int], Tuple[int]]]:
        """Insert a word into the wordsearch.

        Parameters:
            word: Word to add.
            check_density: If the word density should be checked.
                If True, then an error will be raised if too high.
            retry_attempts: How many times to attempt adding the worandom.
            placement_attempts: Find a starting point (per retry).
            direction_attempts: Find a direction from the starting point (per retry).

        Returns:
            The starting point and direction as tuples of ints.

        Raises:
            WordLengthError: If the word is too long or short.
            WordDensityError: If the word density is too high.
            NoMoreRetriesError: If the word failed to be added.
        """
        # Check there are not too many words
        if check_count and len(self.solutions) >= self.difficulty.max_words:
            raise WordCountError

        # Check the word is not too short or long
        if len(word) < 3 or all(len(word) > size for size in self.shape):
            return WordLengthError(word)

        # Check word density is not too high
        if check_density:
            target_size = self._data_words.size * self.difficulty.density_target_words
            if np.sum(self._data_words != '') > target_size:
                raise WordDensityError

        for _ in range(retry_attempts):
            # Find a space where the word can start
            for _ in range(placement_attempts):
                start = tuple(random.randint(0, size - 1) for size in self.shape)
                if self._data_words[start] in ('', word[0]):
                    break
            else:
                raise NoMoreRetriesError(word)

            # Find a direction that allows the word to be added
            attempted_directions = {(0,) * self.dimensions}
            for _ in range(direction_attempts):
                direction = self.difficulty.generate_direction(self.dimensions)

                # Don't repeat previous attempts
                if direction in attempted_directions:
                    continue
                attempted_directions.add(direction)

                # Check the end point is still within bounds
                if not all(-1 <= a + b * len(word) < c + 1 for a, b, c in zip(start, direction, self.shape)):
                    continue

                # Check the current direction words
                location = start
                for char in word:
                    if self._data_words[location] not in ('', char):
                        break
                    location = tuple(map(sum, zip(location, direction)))

                # Update the data
                else:
                    location = start
                    for char in word:
                        self._data_words[location] = char
                        location = tuple(map(sum, zip(location, direction)))
                    self.solutions[word] = start, direction
                    self._req_update_fill = self._req_update_variation = True
                    return start, direction

        raise NoMoreRetriesError(word)

    def add_word(self, word: str, **kwargs: Any) -> None:
        """Add a single word."""
        kwargs.setdefault('check_density', False)
        kwargs.setdefault('check_count', False)
        with suppress(NoMoreRetriesError):
            self._add_word(word, **kwargs)

    def add_words(self, words: List[str], **kwargs: Any) -> None:
        """Add multiple words at once."""
        kwargs.setdefault('check_density', False)
        kwargs.setdefault('check_count', False)
        for word in words:
            with suppress(WordLengthError):
                self.add_word(word, **kwargs)

    def load_word_file(self, path: str = 'wordsEn.txt', **kwargs) -> None:
        """Load words from a file.

        Parameters:
            path: Path to a text file containing words.
        """
        with open(path, 'r') as f:
            words = [line.strip() for line in f]
        random.shuffle(words)

        kwargs.setdefault('check_density', True)
        kwargs.setdefault('check_count', True)
        with suppress(WordDensityError, WordCountError):
            self.add_words(words, **kwargs)

    def _generate_fill(self) -> None:
        """Generate random letter data.

        This has a chance to duplicate existing letters instead of
        selecting entirely new ones.
        """
        letter_choices = tuple(self._data_words[np.where(self._data_words != '')])
        for i in range(self._data_fill.size):
            if letter_choices and random.uniform(0, 1) > self.difficulty.copy_letter_chance:
                self._data_fill[i] = random.choice(letter_choices)
            else:
                self._data_fill[i] = random.choice(string.ascii_lowercase)
        self._req_update_fill = False

    def _generate_variations(self):
        """Generate word variations.

        This is to throw off the player by adding what looks like the
        full word at a quick glance.
        """
        words = list(self.solutions)
        letter_choices = tuple(self._data_words[np.where(self._data_words != '')])

        self._data_variations[:] = ''
        while np.sum(self._data_variations != '') < self._data_variations.size * self.difficulty.density_target_variations:
            word = random.choice(words)
            chrs = list(word)

            # Replace random letters in word
            # eg. word = ward, wore, wond, qerd
            for _ in range(random.randint(0, len(chrs) // 2)):
                if letter_choices and random.uniform(0, 1) > self.difficulty.copy_letter_chance:
                    chrs[random.randint(0, len(chrs) - 1)] = random.choice(letter_choices)
                else:
                    chrs[random.randint(0, len(chrs) - 1)] = random.choice(string.ascii_lowercase)

            # Remove random letters from the word
            # eg. word = wrd, wod
            for _ in range(random.randint(0, len(chrs) // 2)):
                del chrs[random.randint(0, len(chrs) - 1)]

            # Add the word to the variations data
            direction = self.difficulty.generate_direction(self.dimensions)
            location = tuple(random.randint(0, size - 1) for size in self.shape)
            for char in chrs:
                if not all(-1 <= a + b < c + 1 for a, b, c in zip(location, direction, self.shape)):
                    break
                self._data_variations[location] = char
                location = tuple(map(sum, zip(location, direction)))

        self._req_update_variation = False

    def display(self, debug_solutions: bool = False) -> None:
        """Print the wordsearch to the console.

        Parameters:
            debug_solutions: Show the solutions.

        Example:
            >>> random.seed(1234)

            >>> ws = WordSearch(10, difficulty=Difficulty(1, backwards=False))
            >>> ws.add_words(['words','example','generate','hard','easy','search'])

            >>> ws.display()
            Words: words, example, generate, hard, easy, search
            e x a m p l e s g s
            m d d o n r g h e e
            s r o d n n e r n d
            e l a d i a e e e x
            a e e d e e a a r d
            r s m w t l s s a g
            c t l o e x x y t s
            h h a r d d n h e n
            w c w d y g e x e e
            r x a s e a r r t e

            >>> ws.display(debug_solutions=True)
            words: (5, 3) to (10, 3)
            example: (0, 0) to (0, 7)
            generate: (0, 8) to (8, 8)
            hard: (7, 1) to (7, 5)
            easy: (3, 7) to (7, 7)
            search: (2, 0) to (8, 0)
            e x a m p l e   g  
                            e  
            s               n  
            e             e e  
            a             a r  
            r     w       s a  
            c     o       y t  
            h h a r d       e  
                  d            
                  s            
        """
        if debug_solutions:
            # Print the solutions
            for word, (start, direction) in self.solutions.items():
                end = tuple(a + b * len(word) for a, b in zip(start, direction))
                print(f'{word}: {start} to {end}')

            # Generate the data
            raw = self._data_words

            data = np.zeros(self.shape, dtype=str)
            data[:] = ' '
            for word, (start, direction) in self.solutions.items():
                for i in range(len(word)):
                    idx = tuple(a + b * i for a, b in zip(start, direction))
                    data[idx] = raw[idx]
        else:
            print(f'Words: {", ".join(self.words)}')
            data = self.data

        # Print differently based on the dimension
        if self.dimensions == 1:
            print(' '.join(c for c in data.ravel()))

        elif self.dimensions == 2:
            for y in range(self.shape[0]):
                print(' '.join(data[y]))

        else:
            raise RuntimeError('unable to display more than 2 dimensions')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
