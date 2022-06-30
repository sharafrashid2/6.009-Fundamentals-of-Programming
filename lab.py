# NO ADDITIONAL IMPORTS!
import doctest
from typing import Tuple
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, key_type):
        """
        Sets initial value of node to None, key type to whatever the specified key_type is and
        the intial children variable to an empty array.
        """
        self.value = None
        self.key_type = key_type
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        # If wrong type, then TypeError
        if self.key_type != type(key):
            raise TypeError
        # Creates new node if key doesn't already exist
        if key[:1] not in self.children:
                node = Trie(self.key_type)
                self.children[key[:1]] = node
        # Base case
        if len(key) == 1:
            self.children[key[:1]].value = value
        # Recursive case
        else:
            self.children[key[:1]].__setitem__(key[1:], value) 

    def __getitem__(self, key, contains_func=False):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.

        >>> t = Trie(str)
        >>> t['bc'] = 5
        >>> t['b'] = 2
        >>> print(t['b'])
        2

        >>> t = Trie(str)
        >>> t['cat'] = 5
        >>> t['catd'] = 2
        >>> print(t['cat'])
        5
        """
        # If wrong type, then TypeError
        if self.key_type != type(key):
            raise TypeError
        # Condition only for when using the get function in my contains function
        if key[:1] not in self.children and contains_func == True:
            return None
        # If the key is not in the trie or if the key is in the trie but has no value associated with it, a KeyError is raised.
        elif (key[:1] not in self.children) or (len(key) == 1 and self.children[key[:1]].value == None and len(self.children[key[:1]].children) != 0) and contains_func == False:
            raise KeyError
        # Base case of retrieving value
        elif len(key) == 1:
            return self.children[key[:1]].value
        # Recursive case of retrieving value
        else:
            return self.children[key[:1]].__getitem__(key[1:], contains_func)

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.

        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bar'] = 3
        >>> t['bark'] = ':)'
        >>> del t["bar"]
        >>> print(t['bar'])
        Traceback (most recent call last):
            ...
        KeyError
        >>> del t["foo"]
        Traceback (most recent call last):
            ...
        KeyError
        """
        # If the key has an associated value, sets that value to None, otherwise raises key Error
        if self.__getitem__(key) != None:
            self.__setitem__(key, None)
        elif self.__getitem__(key) == None:
            raise KeyError


    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.  If the given key is of
        the wrong type, raise a TypeError.

        >>> t = Trie(str)
        >>> t['bc'] = 5
        >>> print(t.__contains__('ac'))
        False
        >>> print(t.__contains__('b'))
        False
        >>> print(t.__contains__('bc'))
        True
        """
        # If value is retrievable from getting that key, then function is True, otherwise, False
        if self.__getitem__(key, True) != None:
            return True
        return False
        

    def __iter__(self, start=None):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!

        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bar'] = 3
        >>> t['bark'] = ':)'
        >>> list(t)
        [('bat', 7), ('bar', 3), ('bark', ':)')]
        """
        # For when the type is a string
        if self.key_type == str and start == None:
            start = ''
        # For when the type is a tuple
        elif self.key_type == tuple and start == None:
            start = ()
        # Loops through all the keys, adding to the generator if there is a value that is not None
        for key in self.children:
            # Base case
            if self.children[key].value != None:
                yield (start + key, self.children[key].value)
            # Recursive case
            yield from self.children[key].__iter__(start+key)
    
    def make_subtrie(self, prefix):
        """
        Generates values in a trie from a certain key onward.
        """
        sub_trie = self
        for char in prefix:
            if self.key_type == tuple:
                char = (char,)
            if char in sub_trie.children:
                sub_trie = sub_trie.children[char]
            else:
                return []
        items = list(sub_trie)
        return items

    def shorten(self, length, start=None, layer=0):
        """
        Generates values in a trie up to a certain layer.
        """
        # For when the type is a string
        if self.key_type == str and start == None:
            start = ''
        # For when the type is a tuple
        elif self.key_type == tuple and start == None:
            start = ()
        # Loops through all the keys, adding to the generator if there is a value that is not None
        for key in self.children:
            # Base case
            if self.children[key].value != None:
                yield (start + key, self.children[key].value)
            # Recursive case
            if layer + 1 < length:
                yield from self.children[key].shorten(length, start+key, layer+1)

def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text.

    >>> text = "I like to eat apples. I like to eat apples. I like to eat apples."
    >>> word_trie = make_word_trie(text)
    >>> print(list(word_trie))
    [('i', 3), ('like', 3), ('to', 3), ('eat', 3), ('apples', 3)]

     >>> text = "A dog is a very, very loyal animal."
    >>> word_trie = make_word_trie(text)
    >>> print(list(word_trie))
    [('a', 2), ('animal', 1), ('dog', 1), ('is', 1), ('very', 2), ('loyal', 1)]
    """
    # Creates list of individual words in the text
    sentences = tokenize_sentences(text)
    words = []
    for sentence in sentences:
        word = ''
        for char in sentence:
            if char != ' ':
                word += char
            else:
                words.append(word)
                word = ''
        words.append(word)

    word_freq = {}
    # Maps words to their frequencies in a dictionary
    for word in words:
        if word not in word_freq:
            word_freq[word] = 0
        word_freq[word] += 1
    # Creates the word trie
    word_trie = Trie(str)
    for word in word_freq:
        word_trie[word] = word_freq[word]

    return word_trie

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.

    >>> text = "I like to eat apples. I like to eat apples. I like to eat apples."
    >>> phrase_trie = make_phrase_trie(text)
    >>> print(list(phrase_trie))
    [(('i', 'like', 'to', 'eat', 'apples'), 3)]
    >>> text = "Hello. How are you? Do you want a snack?"
    >>> phrase_trie = make_phrase_trie(text)
    >>> print(list(phrase_trie))
    [(('hello',), 1), (('how', 'are', 'you'), 1), (('do', 'you', 'want', 'a', 'snack'), 1)]
    """
    # Similar process as make word trie, except now tuples have tuples of words inside them to make a sentence
    sentences = tokenize_sentences(text)
    sentences_final = []

    for sentence in sentences:
        words = []
        word = ''
        for char in sentence:
            if char != ' ':
                word += char
            else:
                words.append(word)
                word = ''
        words.append(word)
        tuple_words = tuple(words)
        sentences_final.append(tuple_words)
    
    sentence_freq = {}
    for sentence in sentences_final:
        if sentence not in sentence_freq:
            sentence_freq[sentence] = 0
        sentence_freq[sentence] += 1
    
    phrase_trie = Trie(tuple)
    for sentence in sentence_freq:
        phrase_trie[sentence] = sentence_freq[sentence]
    
    return phrase_trie


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.

    # OWN TEST CASE
    >>> text = "I like to eat apples. I hate cats. I like ice cream."
    >>> phrase_trie = make_phrase_trie(text)
    >>> print(autocomplete(phrase_trie, ('i', 'like')))
    [('i', 'like', 'to', 'eat', 'apples'), ('i', 'like', 'ice', 'cream')]

    # BASED ON EXAMPLES
    >>> t = make_word_trie("bat bat bark bar")
    >>> print(autocomplete(t, "ba", 1))
    ['bat']

    >>> print(autocomplete(t, "ba", 2) == ['bat', 'bar'] or autocomplete(t, "ba", 2) == ['bat', 'bark'])
    True

    >>> print(autocomplete(t, "be", 2))
    []
    """
    # Saves time, in case max_count is entered as zero, by checking at start
    if max_count == 0:
        return []
    
    # If key and prefix are not of same type
    if trie.key_type != type(prefix):
        raise TypeError
    
    # Creates a list of sub trie values of only the prefix
    items = trie.make_subtrie(prefix)

    # Adds prefix to list if it is also in trie
    if prefix in trie and isinstance(prefix, str):
        items.append(('', trie[prefix]))
    elif prefix in trie and isinstance(prefix, tuple):
        items.append(((), trie[prefix]))
    
    # Sorts through list of words with maximum frequency at front and returns up to max count
    items.sort(reverse=True, key = lambda x: x[1])
    return [prefix + item[0] for item in items[:max_count]]

def chars_in_common(str1, str2):
    """
    Helper function that returns the characters in common between two words.
    """
    in_common = 0
    for i in range(len(str1)):
        if str1[i] == str2[i]:
            in_common += 1
    return in_common

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.

    OWN TEST CASE:
    >>> t = make_word_trie("heart heat heap heal heed hearth healer heaps")
    >>> print(set(autocorrect(t, 'heat')) == set(['heart', 'heat', 'heap', 'heal']))
    True

    BASED ON EXAMPLE:
    >>> t = make_word_trie("bat bat bark bar")
    >>> print(set(autocorrect(t, "bar", 3)) == set(['bar', 'bark', 'bat']))
    True

    """
    autocorrects = autocomplete(trie, prefix, max_count)
    if len(autocorrects) == max_count:
        return autocorrects

    valid_edits = set()
    all_possible = list(trie.shorten(len(prefix)+1))

    for item in all_possible:
        # single-character insertion
        for i in range(len(prefix)+1):
            if len(item[0]) == (len(prefix) + 1) and chars_in_common(prefix[:i] + '0' + prefix[i:], item[0]) == (len(item[0]) - 1):
                valid_edits.add(item)
        # single character deletion
        for i in range(len(prefix)):
            if (prefix[:i] + prefix[i+1:]) == item[0]:
                valid_edits.add(item)
        # single character replacement
        if len(prefix) == len(item[0]) and chars_in_common(prefix, item[0]) == (len(item[0]) - 1):
            valid_edits.add(item)
        # two char transpose
        for i in range(len(prefix)-1):
            if len(prefix) == len(item[0]) and prefix[i] == item[0][i+1] and item[0][i] == prefix[i+1]:
                if prefix[i+2:] == item[0][i+2:]:
                    valid_edits.add(item)
    
    valid_edits = list(valid_edits)

    # Adds edits to list until max count is reached
    valid_edits.sort(reverse=True, key = lambda x: x[1])
    valid_edits = [item[0] for item in valid_edits]
    autocorrects.extend(valid_edits)

    if max_count != None:
        autocorrects = autocorrects[:max_count]
    else:
        autocorrects = set(autocorrects)
        autocorrects = list(autocorrects)
    return autocorrects
  
def word_filter_gen(trie, pattern, prefix=''):
    """
    Return generator of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    # Base case, when at end of pattern, returns word and value
    if pattern == '':
        if trie.value != None:
            yield prefix, trie.value
        return None
    
    # If character in pattern is a letter, recursively generates values of that correct letter
    if pattern[0] in trie.children:
        yield from word_filter_gen(trie.children[pattern[0]], pattern[1:], prefix+pattern[0])
    
    # If character in pattern is a question mark, loops through each child trie's and recursively generates words 
    elif pattern[0] == '?':
        for key in trie.children:
            yield from word_filter_gen(trie.children[key], pattern[1:], prefix + key)

    
    # If character in pattern is a star, loops through each child trie, recursively generating the correct words with entire pattern
    # Also, generates words after loop of the remainder of the pattern
    elif pattern[0] == '*':
        for key in trie.children:
            yield from word_filter_gen(trie.children[key], pattern, prefix + key)
        yield from word_filter_gen(trie, pattern[1:], prefix)

    
def word_filter(trie, pattern):
    """
    Executes the generator helper function above to produce a list of all possible 
    words derived from the pattern.

    OWN TEST CASE:
    >>> t = make_word_trie("dashing prancing running swimming hiker biker dig sing")
    >>> print(set(word_filter(t, '*ing')) == {('prancing', 1), ('swimming', 1), ('dashing', 1), ('sing', 1), ('running', 1)})
    True

    BASED ON EXAMPLE:
    >>> t = make_word_trie("bat bat bark bar")
    >>> print(set(word_filter(t, "*")) == {('bat', 2), ('bar', 1), ('bark', 1)})
    True
    >>> print(set(word_filter(t, "???")) == {('bat', 2), ('bar', 1)})
    True
    >>> print(set(word_filter(t, "*r*")) == {('bar', 1), ('bark', 1)})
    True
    """
    return list(set(word_filter_gen(trie, pattern)))


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    # with open("tale.txt", encoding="utf-8") as f:
    #     text = f.read()

    # autocorrect test
    # tw = make_word_trie(text)
    # print(autocorrect(tw, 'hear', 12))

    # autocomplete test
    # t = make_word_trie(text)
    # print(autocomplete(t, 'gre', 6))

    # distinct words/phrases
    # t = make_word_trie(text)
    # l1 = list(t)
    # print(len(l1))

    # total words/phrases
    # total = 0
    # l1 = list(t)
    # for item in l1:
    #     total += item[1]
    # print(total)

    # word filter
    # t = make_word_trie(text)
    # print(word_filter(t, 'r?c*t'))

    # t = make_phrase_trie(text)
    # total = 0
    # l1 = list(t)
    # for item in l1:
    #     total += item[1]
    # print(total)









