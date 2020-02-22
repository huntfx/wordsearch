import random, sys, string, base64, zlib, time

def list_to_text(value, connector=''):
    """Convert a list into a readable format.
    If 'to' or '-' is given as a connector, only the first and last list values will be used.
    
    >>> list_to_text([0,1,2,3,4,5])
    '0, 1, 2, 3, 4, 5'
    >>> list_to_text([0,1,2,3,4,5], 'and')
    '0, 1, 2, 3, 4 and 5'
    >>> list_to_text([0,1,2,3,4,5], 'to')
    '0 to 5'
    >>> list_to_text([0,1,2,3,4,5], '-')
    '0-5'
    >>> list_to_text([2])
    '2'
    
    """
    value = [str(i) for i in value]
    if len(value) == 1:
        return value[0]
    elif value:
        if connector:
            if connector in ('to', '-'):
                if connector == 'to':
                    connector = ' to '
                return value[0] + connector + value[-1]
            return ', '.join(value[:len(value)-1]) + ' ' + connector + ' ' + value[-1]
        else:
            return ', '.join(value)
    return ''
    
def encode_binary(x):
    """Encode a string of 1s and 0s to shorten it down.
    Use base 64 to make it readable.
    
    >>> encoded = encode_binary('1000010101110010111010000011011111001110101000100010111000100110')
    >>> base64.b64encode(encoded)
    'AIVy6DfOoi4m'
    """
    if x.replace('0', '').replace('1', ''):
        raise TypeError('input must be in binary')
    x_binary = [x[i:i+8] for i in range(0, len(x), 8)]
    x_padding = 8-len(x_binary[-1])
    x_padding_binary = '{0:08b}'.format(x_padding)
    x_binary = [x_padding_binary] + x_binary
    x_binary[-1] += '0'*x_padding
    return ''.join(chr(int(i, 2)) for i in x_binary)

def decode_binary(x):
    """Decode the output from the encode_binary function.
    
    >>> encoded = base64.b64decode('AIVy6DfOoi4m')
    >>> decode_binary(encoded)
    '1000010101110010111010000011011111001110101000100010111000100110'
    """    
    x_data = [ord(i) for i in list(x)]
    x_padding = x_data.pop(0)
    x_binary = ['{0:08b}'.format(i) for i in x_data]
    x_binary[-1] = x_binary[-1][:8-x_padding]
    return ''.join(x_binary)
    
class DifficultyLevels:
    """Set which directions each difficulty level activates.
    More levels may be added, though make sure they are in order since the Difficulty function can also work by index.
    """
    level = ['easy', 'medium', 'hard']
    all_levels = [i/2 if i%2 else level[i/2] for i in range(len(level)*2)]
    
    diff_level = {}
    diff_level[level[0]] = 'down right'.split()
    diff_level[level[1]] = 'up down right left'.split()
    diff_level[level[2]] = 'up down left right upleft upright downleft downright'.split()
    
def Difficulty(value):
    """Convert easy (0), medium (1) or hard (2+) into directions.
    If input is invalid, a message will be printed and hard difficulty will be chosen.
    
    >>> Difficulty('easy')
    ['down', 'right']
    >>> Difficulty(2)
    ['up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright']
    >>> Difficulty(7)
    Value '7' is out of range, please use either easy, medium or hard (0-2 also works).
    Automatically set difficulty to hard.
    ['up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright']
    >>> Difficulty('esy')
    Difficulty 'esy' doesn't exist, please use either easy, medium or hard (0-2 also works).
    Automatically set difficulty to hard.
    ['up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright']
    """
    try:
        if str(value).isdigit():
            return DifficultyLevels.diff_level[DifficultyLevels.level[int(value)]]
        elif isinstance(value, str):
            return DifficultyLevels.diff_level[value.lower()]
    except (KeyError, IndexError):
        if type(sys.exc_info()[1]) == type(KeyError()):
            msg = "Difficulty '{v}' doesn't exist"
        else:
            msg = "Value '{v}' is out of range"
        print msg.format(v=value) + ', please use either {d} ({n} also works).'.format(d=list_to_text(DifficultyLevels.level, 'or'),
                                                                                       n=list_to_text(range(len(DifficultyLevels.level)), '-'))
        print "Automatically set difficulty to hard."
        return DifficultyLevels.diff_level['hard']
    
    
class WordSearch(object):
    """Generate a random word search using a list of words.
    
    >>> random.seed(1234)
    
    This is an example use showing how to generate an easy word search.
    
    >>> ws = WordSearch(10, 10, 'easy')
    >>> ws.generate(['words','example','generate','hard','easy','search'])
    WordSearch(data='eJw1jjsOwkAMRBvEp6LlAJRbkCgIcMVVrOxoFwk2KztSSMsF4IgcgSPgKEnj3zzbw8zsI4tPIePJj3wHoD6oRZYQBSFZia4R7gzoRQBpxBLnYZFRcwut4VsYbUhWMCJ7DUgQE91i9f7ulpvX9bNfb3+uODhDpI5Unsg3XXJ23StV1dgNduhIcguxdZMpKsp5wNpTcR7R+QVdJvkPC2hN1g==')
    
    >>> ws.display()
    a a a a d h a r d n
    g p e x a m p l e e
    e s d g s e e s a r
    g h r e g n e e s e
    w o r a w e x a y r
    r e e r o r r r e a
    p d h a r a e c a t
    e s c e d t e h r e
    e x a p s e a e h a
    d s g e n e r a t e
    Words: easy, example, generate, hard, search, words
    
    >>> ws.solutions()
    search: (7, 2) down
    words: (4, 4) down
    hard: (5, 0) right
    example: (2, 1) right
    easy: (8, 1) down
    generate: (2, 9) right
    
    >>> ws.display(show_solutions=True)
              h a r d  
        e x a m p l e  
                  s a  
                  e s  
            w     a y  
            o     r    
            r     c    
            d     h    
            s          
        g e n e r a t e
    Words: easy, example, generate, hard, search, words
    
    By setting the density value along with others, it's possible to fine tune the type of output when using a large list of words.
    See the generate function for more information.
    """
    
    direction_move_amount = {}
    direction_move_amount['right'] = 1
    direction_move_amount['left'] = -1
    
    def __init__(self, width=10, height=10, difficulty='hard', data=None):
        """Set up the basic options, or import them from the data string.
        
        Paramaters:
            width:
                Default: 10
                Number of columns.
                
            height:
                Default: 10
                Number of rows.
                
            difficulty:
                Default: 'hard'
                Which directions words can move in.
                Possible values: 'easy', 'medium', 'hard', 0, 1 or 2.
            
            data:
                Default: None
                Encoded string that can be used to load a previously generated word search.
        """
        
        #Decode data string
        if data is not None:
            data_parts = zlib.decompress(base64.b64decode(data)).split(',')
            self.grid = [i if i != '_' else '' for i in data_parts[0]]
            filled_ids = decode_binary(data_parts[1])
            self.filled_cells = []
            for i in range(len(filled_ids)):
                if filled_ids[i] == '1':
                    self.filled_cells.append(i)
            #self.filled_cells = data_parts[1]
            
            width = int(data_parts[2])
            height = len(self.grid)/width
            self.used_words = {k:(int(v1), v2) for k, v1, v2 in [i.split(':') for i in data_parts[3:]]}
        
        #Set values
        self.width = width
        self.height = height
        self.grid_ids = range(self.width*self.height)
        self.max_id_len = len(str(self.width*self.height-1))
        self.difficulty(difficulty)
        
        #Generate grid data
        if data is None:
            self.grid = ['' for i in self.grid_ids]
            self.filled_cells = []
            self.used_words = {}
            
        #Complete the direction calculations now that width is given
        self.direction_move_amount['down'] = self.width
        self.direction_move_amount['up'] = -self.width
        self.direction_move_amount['downright'] = self.direction_move_amount['down']+self.direction_move_amount['right']
        self.direction_move_amount['downleft'] = self.direction_move_amount['down']+self.direction_move_amount['left']
        self.direction_move_amount['upright'] = self.direction_move_amount['up']+self.direction_move_amount['right']
        self.direction_move_amount['upleft'] = self.direction_move_amount['up']+self.direction_move_amount['left']
    
    def __repr__(self):
        """Encode all important data into a string."""
        
        filled_ids = []
        for i in range(self.width*self.height):
            filled_ids.append(str(int(i in self.filled_cells)))
        
        output = [''.join(i if i else '_' for i in self.grid), 
                  encode_binary(''.join(filled_ids)),
                  self.width]
        output += [':'.join((k, str(v[0]), v[1])) for k,v in self.used_words.iteritems()]
        
        return "WordSearch(data='{o}')".format(o=base64.b64encode(zlib.compress(','.join(str(i) for i in output))))
    
    def difficulty(self, value):
        """Update the difficulty level."""
        self.difficulty_value = value
        self.difficulty_directions = Difficulty(value)
        return self
        
    def id_to_coordinate(self, id):
        """Convert a coordinate ID to its x and y value.
        
        >>> WordSearch(width=10, height=10).id_to_coordinate(13)
        (3, 1)
        >>> WordSearch(width=5, height=10).id_to_coordinate(13)
        (3, 2)
        >>> WordSearch(width=5, height=5).id_to_coordinate(13)
        (3, 2)
        >>> WordSearch(width=5, height=5).id_to_coordinate(25)
        >>> WordSearch(width=5, height=5).id_to_coordinate(24)
        (4, 4)
        """
        
        location_x = id%self.width
        location_y = id/self.width
        
        #Only return value if it's within range
        if location_y < self.height:
            return (location_x, location_y)

    def move_in_direction(self, initial_location, direction):
        """Calculate the new coordinate ID based on a direction.
        Returns None if out of range, otherwise return the new coordinate ID.
        
        Parameters:
            initial_location:
                Coordinate ID where to attempt the move from.
                
            direction:
                Direction to move, needs to be in string format.
                Can be 'up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft' or 'downright'.
        
        >>> WordSearch(10, 10).move_in_direction(57, 'up')
        47
        >>> WordSearch(5, 10).move_in_direction(57, 'up')
        >>> WordSearch(5, 10).move_in_direction(47, 'up')
        42
        """
        
        #Calculate new location
        old_coordinate = self.id_to_coordinate(initial_location)
        new_location = initial_location+self.direction_move_amount[direction]
        new_coordinate = self.id_to_coordinate(new_location)
        
        #Check if it's next to the current coordinate, and if it's still in the grid
        if old_coordinate and new_coordinate:
            is_in_range = all(new_coordinate[i] in (old_coordinate[i]+j for j in xrange(-1, 2)) for i in xrange(2))
            is_in_grid = 0 < new_location < self.width*self.height
            if is_in_range and is_in_grid:
                return new_location

    def word_variations(self, words, min_results=1):
        """Take the list of used words and cut them up a little, so the user will find similar combinations
        of letters in the word search that don't amount to the full word.
        Parameters:
            min_results:
                Minimum amount of results to generate. 
                It will iterate through all words multiple times until the resulting output is longer than this.
        >>> random.seed(1234)
        >>> WordSearch().word_variations(['testing', 'word'], 10)
        ['etint', 'er', 'estd', 'tstd', 'rsti', 'isti', 'oi', 'teoin', 'teown', 'tesn', 'test', 'wod']
        >>> WordSearch().word_variations(['testing', 'word'], 5)
        ['twsig', 'wwrd', 'wwod', 'en', 'ein']
        """
        all_letters = ''.join(words)
        word_list = []
        while len(word_list) < min_results:

            for word in words:
                original_word = word
                word_len = len(word)
                word_range = xrange(word_len)

                for repeat in xrange(random.randint(0, 4)):

                    #Remove random letters from the word - word = wrd, wod, etc
                    remove_letters = random.sample(word_range, random.randint(0, word_len/3))
                    num_removed_letters = 0
                    for index in remove_letters:
                        word = word[:index-num_removed_letters]+word[index+1-num_removed_letters:]
                        num_removed_letters += 1

                    #Replace random letters in word - word = ward, wore, wond, etc
                    word_section = sorted(random.sample(word_range, 2))
                    if word_section[0] or word_section[1] != word_len:

                        new_word = word[random.randint(0, word_section[0]):random.randint(word_section[1], word_len)]
                        new_word_len = len(new_word)

                        for replacement in xrange(random.randint(0, new_word_len/2)):
                            replacement_index = random.randint(0, new_word_len-1)
                            new_letter = random.choice(all_letters)

                            new_word = new_word[:replacement_index]+new_letter+new_word[replacement_index+1:]

                            #Only add to list if
                            if new_word != original_word:
                                word_list.append(new_word)
        return word_list
    
    def generate(self, word_list=None, word_file=None, 
                 density=0.7, max_iterations=1000, min_len=3, max_len=None, max_words=10000):
        """Generate data for the word search. The second pass simply means a second loop that will fill the
        grid with similar segments of words similar to the words already there.
        This function works by selecting a starting point, assigning a random first letter from the word list,
        and then branching out in all directions to find a matching word. Since the first matching word is
        always the smallest, there is a chance to skip this depending on how many existing words there are, to
        give larger words a chance to appear. The results get narrowed down for each further step in the direction,
        where it will check for existing characters in the grid and compare them to the current words.
        After a successful attempt, the word is written into the grid and stored in the used_words dictionary with
        some extra information on locating it.
        
        Parameters:
            word_list:
                Default: None
                List or tuple of words to use in the generation.
                If None, word_file will be used instead
                
            word_file:
                Default: None
                Path to a text file with words on individual lines.
                If both word_list and word_file are None, a ValueError will be raised.
            
            density:
                Default: 0.7
                What percentage of space should be taken by words.
                A low value will keep the word search simple, and a high value will cram as many words in as possible.
            
            max_iterations:
                Default: 1000
                Limits the number of iterations that can run to stop generation taking too long.
                An iteration counts as each attempted placement, so 10 iterations does not necessarily result in 10 words.
                
            min_len:
                Default: 3
                Minimum length of words to include in the word search.
                If None, will set itself to 2.
            
            max_len:
                Default: None
                Maximum length of words to include in the word search.
                If None, will set itself to either the width or height of the word search, depending on which is smallest.
            
            max_words:
                Default: 10000
                Maximum number of words to generate.
                Set to a low value for an easier word search.
        """
        
        #For debug purposes
        second_pass = True
        fill_empty_values = True
        print_time_taken = False
        start_time = time.time()
        
        if min_len is None:
            min_len = 2
        if max_len is None:
            max_len = min(self.width, self.height)
        density = max(0.0, min(1.0, density))
        
        #Build list of words
        if word_list is None:
            word_list = []
            if word_file is None:
                raise ValueError("neither word_list nor word_file specified")
            with open(word_file) as f:
                for line in f:
                    word = line.strip()
                    if min_len <= len(word) <= max_len:
                        word_list.append(word)
        else:
            word_list = [word for word in word_list if min_len <= len(word) <= max_len]
        if not word_list:
            raise ValueError("no words within valid range of characters")

        if print_time_taken:
            print "{} seconds to generate word list.".format(time.time()-start_time)

        target_cells = self.width*self.height*density
        
        for generation_stage in range(1+second_pass):
        
            #Detect which word list to use depending on the pass
            if generation_stage and self.used_words:
                word_bank = self.word_variations(self.used_words.keys(), max_iterations)
                if print_time_taken:
                    print "{} seconds to generate invalid word list.".format(time.time()-start_time)
            else:
                word_bank = word_list
                
            #Loop until maximum iterations, words or density is reached, or until word_bank is empty
            num_iterations = 0
            while num_iterations < max_iterations and word_bank and (len(self.filled_cells) < target_cells and len(self.used_words) < max_words or generation_stage):
                num_iterations += 1
                
                random.shuffle(self.difficulty_directions)
                
                
                #Pick a coordinate, and fill with letter if empty
                current_coordinate = random.choice(self.grid_ids)
                using_new_letter = False
                if not self.grid[current_coordinate]:
                    using_new_letter = True
                    next_coordinate = random.choice(word_bank)[0]
                    
                #Create a selection of words
                initial_word_list = [word for word in word_bank if self.grid[current_coordinate] in word[0]]
                initial_word_list = random.sample(initial_word_list, min(len(initial_word_list), max_iterations))

                valid_word = None
                for direction in self.difficulty_directions:
                    
                    
                    matching_word_list = initial_word_list
                    random.shuffle(matching_word_list)
                    next_direction = current_coordinate
                    
                    #Loop while there are matching words
                    count = 0
                    while matching_word_list:
                        
                
                        #Cancel if invalid direction
                        if next_direction is None:
                            matching_word_list = []
                            break
                            
                        if not using_new_letter:
                            next_coordinate = self.grid[next_direction]
                        else:
                            using_new_letter = False
                            
                        #Loop for each word
                        delete_count = 0
                        for i in range(len(matching_word_list)):

                            i -= delete_count
                            
                            #Delete word if the letter doesn't match
                            if next_coordinate and next_coordinate != matching_word_list[i][count]:
                                del matching_word_list[i]
                                delete_count += 1

                                #Break again if word list is empty
                                if not matching_word_list:
                                    break
                                    
                            #If reached the length of a word, it's succeeded
                            elif count >= len(matching_word_list[i])-1:
                                
                                #Choose whether to stop here or continue for a longer word
                                if random.uniform(0, 1) < 1.0/(max(1, len(matching_word_list)/2)):
                                    valid_word = matching_word_list[i]
                                    matching_word_list = []
                                    break
                                else:
                                    del matching_word_list[i]
                                    delete_count += 1

                        next_direction = self.move_in_direction(next_direction, direction)
                        count += 1
                        
                        
                    #Update the grid data
                    if valid_word is not None:
    
                        if not generation_stage:
                            used_word = word_bank.pop(word_list.index(valid_word))
                            self.used_words[used_word] = (current_coordinate, direction)
    
                        next_direction = current_coordinate
                        for i in range(len(valid_word)):
    
                            letter = valid_word[i]
                            if not self.grid[next_direction]:
                                self.grid[next_direction] = letter
                                if not generation_stage:
                                    self.filled_cells.append(next_direction)
                            next_direction = self.move_in_direction(next_direction, direction)
    
                        break
            if print_time_taken:
             
                if not generation_stage:
                    print "{} seconds to populate grid.".format(time.time()-start_time)
                    
                else:
                    print "{} seconds to populate grid with invalid words.".format(time.time()-start_time)
        
        #Fill with random letters
        if fill_empty_values:
            for i in xrange(len(self.grid)):
                if not self.grid[i]:
                    self.grid[i] = random.choice(string.ascii_lowercase)
                    
            if print_time_taken:
                print "{} seconds to populate grid with random letters.".format(time.time()-start_time)
                        
        return self
                            
    def display(self, show_solutions=False):
        """Print the word search result.
        
        Parameters:
            show_solutions:
                Default: False
                Only show the words, and make any random characters invisible.
        """
        count = 0
        for i in xrange(self.height):
            current_row = []
            for j in xrange(self.width):
                letter = self.grid[count]
                
                if not letter or count not in self.filled_cells and show_solutions:
                    letter = ' '
                current_row.append(letter)
                count += 1
            print ' '.join(current_row)
        print 'Words: '+', '.join(sorted(self.used_words.keys()))


    def solutions(self):
        """Print the solutions (location and direction) to the generated words.
        Example Output:
            realtor: (8, 1) down
            gawk: (1, 2) downright
            marmoset: (13, 9) up
            canvasses: (3, 13) upright
            nils: (0, 11) upright
            frizzer: (6, 13) right
            unmade: (13, 10) left
            engining: (8, 2) left
        """
        words = self.used_words
        for word in words:
            print '{}:'.format(word), self.id_to_coordinate(words[word][0]), words[word][1]