import random
import string

# Common words to use in fallback text generation for more natural sentences
COMMON_WORDS = [
    # Articles
    "the", "a", "an",
    # Prepositions
    "in", "on", "with", "at", "by", "for", "from", "to", "of", "about", "around",
    # Conjunctions
    "and", "but", "or", "yet", "so", "while", "because", "though", "since",
    # Pronouns
    "I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    # Common verbs
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "done", "make", "makes", "made", "go", "goes", "went",
    "see", "sees", "saw", "seen", "come", "comes", "came", "get", "gets", "got",
    "know", "knows", "knew", "known", "take", "takes", "took", "taken",
    # Common adjectives
    "good", "new", "first", "last", "long", "great", "little", "own", "other", 
    "old", "right", "big", "high", "different", "small", "large", "important",
    # Common nouns
    "time", "person", "year", "way", "day", "thing", "world", "life", "hand",
    "part", "child", "eye", "place", "work", "week", "case", "point", "fact",
    "group", "problem", "number", "company", "business", "idea", "information",
]

def generate_sentence_structure():
    """Generate a plausible sentence structure with placeholders."""
    # More complex sentence structures with more words to ensure longer sentences
    structures = [
        # Basic structures (extended)
        "The {adj} {noun} {verb} {adv} {prep} the {adj} {noun}.",
        "{det} {adj} {noun} {verb} {det} {adj} {noun} {prep} {det} {adj} {noun}.",
        "{pronoun} {adv} {verb} that {det} {noun} {verb} {adv} {prep} {det} {noun}.",
        
        # Complex structures
        "When {det} {adj} {noun} {verb} {adv}, {det} {adj} {noun} {verb} {prep} {det} {noun}.",
        "If {pronoun} {verb} {det} {adj} {noun}, {pronoun} will {verb} {det} {adj} {noun} {adv}.",
        "{det} {adj} {noun} {verb} to {verb} {prep} {det} {adj} {noun} {prep} {det} {noun}.",
        
        # Compound sentences
        "{det} {noun} {verb} {adv}, but {det} {adj} {noun} {verb} {prep} {det} {adj} {noun}.",
        "Although {det} {noun} {verb} {adv}, {det} {adj} {noun} {verb} {prep} {det} {adj} {noun}.",
        "Not only {verb} {det} {adj} {noun} {adv}, but it also {verb} {prep} {det} {adj} {noun}.",
        
        # Descriptive sentences
        "During {det} {adj} {noun}, {det} {adj} {noun} {verb} {adv} {prep} {det} {noun}.",
        "{det} {adj} {noun} {verb} {adv} because {det} {adj} {noun} {verb} {prep} {det} {noun}.",
        "{det} {noun} that {verb} {prep} {det} {adj} {noun} {adv} {verb} {det} {adj} {noun}.",
        
        # Question structures
        "Why {verb} {det} {adj} {noun} {adv} {prep} {det} {adj} {noun}?",
        "How {adv} {verb} {det} {adj} {noun} {prep} {det} {adj} {noun}?",
    ]
    return random.choice(structures)

def fill_sentence_structure(structure, special_word=None, special_word_pos=None):
    """Fill in a sentence structure with words."""
    # Expanded word lists for more variety and longer sentences
    parts = {
        'noun': ["time", "person", "year", "way", "day", "thing", "world", "life", 
                "hand", "part", "child", "eye", "place", "work", "week", "case",
                "company", "system", "program", "question", "government", "number",
                "night", "point", "home", "water", "room", "mother", "area", "money",
                "story", "fact", "month", "lot", "right", "study", "book", "word", "business"],
        'verb': ["is", "are", "was", "were", "be", "been", "being", "have", "has", 
                "had", "do", "does", "did", "done", "make", "makes", "made",
                "know", "thinks", "takes", "goes", "comes", "uses", "finds", "gives",
                "tells", "works", "likes", "needs", "feels", "becomes", "leaves",
                "puts", "means", "keeps", "lets", "begins", "seems", "helps", "shows", "plays"],
        'adj': ["good", "new", "first", "last", "long", "great", "little", "own", 
               "other", "old", "right", "big", "high", "different", "small", "large",
               "early", "young", "important", "few", "public", "same", "able",
               "best", "better", "low", "certain", "special", "hard", "major", "personal",
               "current", "national", "natural", "physical", "strong", "possible", "clear"],
        'adv': ["quickly", "slowly", "carefully", "happily", "sadly", "really", 
               "very", "extremely", "quite", "rather", "almost", "nearly", "too",
               "also", "then", "however", "again", "still", "sometimes", "often",
               "usually", "always", "never", "ever", "perhaps", "especially", 
               "actually", "clearly", "certainly", "absolutely", "completely"],
        'prep': ["in", "on", "with", "at", "by", "for", "from", "to", "of", "about",
               "between", "among", "through", "without", "before", "after",
               "during", "around", "beyond", "under", "over", "into", "against",
               "despite", "throughout", "within", "along", "upon", "beside"],
        'pronoun': ["I", "you", "he", "she", "it", "we", "they", "me", "him", "her",
                   "us", "them", "my", "your", "his", "her", "its", "our", "their",
                   "mine", "yours", "hers", "ours", "theirs", "myself", "yourself",
                   "himself", "herself", "itself", "ourselves", "themselves"],
        'det': ["the", "a", "an", "this", "that", "these", "those", "my", "your", "his",
               "her", "its", "our", "their", "some", "any", "each", "every", "many", "much",
               "few", "several", "all", "both", "either", "neither", "no", "another"]
    }
    
    result = structure
    
    # Replace placeholders with random words from appropriate categories
    for category in parts:
        while '{'+category+'}' in result:
            word = random.choice(parts[category])
            if special_word and special_word_pos == category:
                word = special_word
                special_word = None  # Only use once
            result = result.replace('{'+category+'}', word, 1)
    
    # Ensure sentence is long enough
    while len(result) < 50:
        # Add extra descriptors to make sentence longer
        if " the " in result:
            adj = random.choice(parts['adj'])
            result = result.replace(" the ", f" the {adj} ", 1)
        elif " a " in result:
            adj = random.choice(parts['adj'])
            result = result.replace(" a ", f" a {adj} ", 1)
        else:
            # If no articles to expand, add suffix
            if result.endswith('.'):
                result = result[:-1] + " " + random.choice(["indeed", "for sure", "without doubt", "as expected", "interestingly"]) + "."
            break
    
    return result

def generate_random_text_snippet(highlighted_text, min_lines, max_lines, fallback_char_set=None):
    """Generates multiple lines of readable text with a highlighted phrase."""
    # Ensure we generate at least min_lines
    num_lines = random.randint(max(1, min_lines), max(min_lines, max_lines))
    highlight_line_index = random.randint(0, num_lines - 1)
    lines = []
    
    # Ensure all lines are substantial length
    MIN_LINE_LENGTH = 50
    MAX_LINE_LENGTH = 80
    
    for i in range(num_lines):
        if i == highlight_line_index:
            # For the highlighted line, make sure to include the highlighted text
            # Create a sentence with the highlighted text randomly placed
            words_count = len(highlighted_text.split())
            
            if ' ' in highlighted_text and words_count > 1:
                # If it's a phrase, incorporate it naturally
                structures = [
                    "The {adj} {noun} " + highlighted_text + " {prep} {det} {adj} {noun}.",
                    "{det} {adj} {noun} {adv} " + highlighted_text + " {prep} {det} {noun}.",
                    "When " + highlighted_text + ", {det} {adj} {noun} {verb} {adv} {prep} {det} {noun}.",
                    "{pronoun} {verb} that " + highlighted_text + " {verb} {adv} {prep} {det} {adj} {noun}.",
                    "Because of " + highlighted_text + ", {det} {adj} {noun} {verb} {adv} {prep} {det} {noun}.",
                ]
                sentence = random.choice(structures)
                sentence = fill_sentence_structure(sentence)
            else:
                # If it's a single word, incorporate as the appropriate part of speech
                pos_options = ['noun', 'verb', 'adj']
                special_pos = random.choice(pos_options)
                sentence = fill_sentence_structure(generate_sentence_structure(), 
                                                  highlighted_text, special_pos)
            
            # Ensure line is long enough
            attempts = 0
            while len(sentence) < MIN_LINE_LENGTH and attempts < 5:
                if ' ' in highlighted_text and words_count > 1:
                    # Try again with a more complex structure
                    structure = "Although {det} {adj} {noun} {verb} {adv}, " + highlighted_text + " {verb} {prep} {det} {adj} {noun}."
                    sentence = fill_sentence_structure(structure)
                else:
                    # Try a more complex structure
                    sentence = fill_sentence_structure(generate_sentence_structure(), 
                                                      highlighted_text, special_pos)
                attempts += 1
            
            lines.append(sentence)
        else:
            # Generate a normal sentence for non-highlighted lines
            sentence = fill_sentence_structure(generate_sentence_structure())
            
            # Ensure line is long enough
            attempts = 0
            while len(sentence) < MIN_LINE_LENGTH and attempts < 5:
                # Try again with a more complex structure
                sentence = fill_sentence_structure(generate_sentence_structure())
                attempts += 1
            
            lines.append(sentence)

    # Validate all lines meet the length requirements
    final_lines = []
    for line in lines:
        # Cut excessively long lines
        if len(line) > MAX_LINE_LENGTH:
            # Try to find a good place to cut the sentence
            cut_point = MAX_LINE_LENGTH
            while cut_point > 0 and line[cut_point] != ' ':
                cut_point -= 1
            
            if cut_point > MIN_LINE_LENGTH:
                line = line[:cut_point] + "."
        
        # Extend short lines
        if len(line) < MIN_LINE_LENGTH:
            # Add descriptive phrases to extend the line
            extra_phrases = [
                " in the most unexpected way",
                " as we had anticipated earlier",
                " according to recent observations",
                " with remarkable precision and detail",
                " throughout the entire process",
                " despite previous contradicting evidence",
                " in this particular context",
            ]
            
            if line.endswith('.'):
                line = line[:-1] + random.choice(extra_phrases) + "."
            elif line.endswith('?'):
                line = line[:-1] + random.choice(extra_phrases) + "?"
            elif line.endswith('!'):
                line = line[:-1] + random.choice(extra_phrases) + "!"
        
        final_lines.append(line)

    # Double-check final line count
    if len(final_lines) < min_lines:
        print(f"Warning: Random generator created only {len(final_lines)} lines (min: {min_lines}). This shouldn't happen.")
        return None, -1  # Treat as failure if check fails unexpectedly

    return final_lines, highlight_line_index
