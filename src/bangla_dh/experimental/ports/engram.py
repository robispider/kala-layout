"""Source-derived scoring port of prep/prep_keypair_engram_scores.py at 179e1c08b220ae1b02f6c425a7d1cbd1150c1db2.

Copyright Arno Klein; MIT license: data/evaluators/mechanics-v1/LICENSE.
Extracted by mechanics_sources; scoring bodies and constants are unchanged.
Bangla adaptation is in experimental/mechanics.py.
"""

import csv

from pathlib import Path

from typing import Dict

QWERTY_LAYOUT = {
    # Number row (row 0)
    '1': (0, 1, 1, 'L', 0), '2': (0, 2, 2, 'L', 0), '3': (0, 3, 3, 'L', 0), '4': (0, 4, 4, 'L', 0), '5': (0, 5, 4, 'L', 0),
    '6': (0, 5, 4, 'R', 0), '7': (0, 4, 4, 'R', 0), '8': (0, 3, 3, 'R', 0), '9': (0, 2, 2, 'R', 0), '0': (0, 1, 1, 'R', 0),

    # Top row (row 1)
    'Q': (1, 1, 1, 'L', 0), 'W': (1, 2, 2, 'L', 0), 'E': (1, 3, 3, 'L', 0), 'R': (1, 4, 4, 'L', 0), 'T': (1, 5, 4, 'L', 0),
    'Y': (1, 5, 4, 'R', 0), 'U': (1, 4, 4, 'R', 0), 'I': (1, 3, 3, 'R', 0), 'O': (1, 2, 2, 'R', 0), 'P': (1, 1, 1, 'R', 0),

    # Home row (row 2)
    'A': (2, 1, 1, 'L', 1), 'S': (2, 2, 2, 'L', 1), 'D': (2, 3, 3, 'L', 1), 'F': (2, 4, 4, 'L', 1), 'G': (2, 5, 4, 'L', 0),
    'H': (2, 5, 4, 'R', 0), 'J': (2, 4, 4, 'R', 1), 'K': (2, 3, 3, 'R', 1), 'L': (2, 2, 2, 'R', 1), ';': (2, 1, 1, 'R', 1),

    # Bottom row (row 3)
    'Z': (3, 1, 1, 'L', 0), 'X': (3, 2, 2, 'L', 0), 'C': (3, 3, 3, 'L', 0), 'V': (3, 4, 4, 'L', 0), 'B': (3, 5, 4, 'L', 0),
    'N': (3, 5, 4, 'R', 0), 'M': (3, 4, 4, 'R', 0), ',': (3, 3, 3, 'R', 0), '.': (3, 2, 2, 'R', 0), '/': (3, 1, 1, 'R', 0),

    # Additional common keys
    '[': (1, 0, 1, 'R', 0), "'": (2, 0, 1, 'R', 0), 
}

qwerty_home_blocks = ['Q', 'W', 'E', 'R', 'U', 'I', 'O', 'P', 
                      'A', 'S', 'D', 'F', 'J', 'K', 'L', ';', 
                      'Z', 'X', 'C', 'V', 'M', ',', '.', '/']

FINGER_COLUMNS = {
    'L': {
        1: ['Q', 'A', 'Z'],    # Pinky
        2: ['W', 'S', 'X'],    # Ring
        3: ['E', 'D', 'C'],    # Middle
        4: ['R', 'F', 'V'] #, 'T', 'G', 'B']  # Index (not including T, G, B)
    },
    'R': {
        4: ['U', 'J', 'M'],    # Index (not including Y, H, N)
        3: ['I', 'K', ','],    # Middle
        2: ['O', 'L', '.'],    # Ring
        1: ['P', ';', '/'] #, "'", '[']  # Pinky (not including ' and [)
    }
}

criteria = ['key_preference', 'row_separation', 'same_row',
            'outside', 'same_finger',
            'scissor', 'half_scissor']

ncriteria = len(criteria)

engram_avg4_criteria = ['row_separation', 'same_row', 'same_finger', 'outside']

def get_key_info(key: str):
    """Get (row, finger, hand) for a key."""
    key = key.upper()
    return QWERTY_LAYOUT.get(key)

def is_finger_in_column(key: str, finger: int, hand: str) -> bool:
    """Check if a key is in the designated column for a finger."""
    key = key.upper()
    if hand in FINGER_COLUMNS and finger in FINGER_COLUMNS[hand]:
        return key in FINGER_COLUMNS[hand][finger]
    return False

def score_bigram(bigram: str) -> Dict[str, float]:
    """Calculate Engram criteria scores for a bigram."""
    if len(bigram) != 2:
        raise ValueError("Bigram must be exactly 2 characters long")    
    
    char1, char2 = bigram[0].upper(), bigram[1].upper()
    
    # Get key information
    key_info1 = get_key_info(char1)
    key_info2 = get_key_info(char2)
    
    if key_info1 is None or key_info2 is None:
        raise ValueError(f"Invalid keys: {char1}, {char2}")
    
    row1, column1, finger1, hand1, homekey1 = key_info1
    row2, column2, finger2, hand2, homekey2 = key_info2

    row_gap = abs(row1 - row2)
    column_gap = abs(column1 - column2)
    
    inside_columns1 = is_finger_in_column(char1, finger1, hand1)
    inside_columns2 = is_finger_in_column(char2, finger2, hand2)
    
    scores = {}

    #----------------------------------------------------------------------------------
    # Engram's bigram scoring criteria
    #----------------------------------------------------------------------------------    
    # 1. Key preferences (empirical Bradley-Terry tiers inside left finger-columns)
    # 2. Row separation (empirical meta-analysis of left same-row, reach, and hurdle key-pairs) 
    # 3. Same-row finger order and column separation
    #    - (empirical analysis of left key-pairs toward vs. away from the thumb)
    #    - (empirical meta-analysis of left key-pairs in adjacent vs. remote columns) 
    # 4. Same-finger (empirical analysis of left same- vs. different finger inside finger-columns)
    # 5. Outside reach (empirical analysis of left-hand lateral stretches outside finger-columns)
    # 6. Scissor (adjacent column hurdle; ignores all other awkward finger mechanics)
    # 7. Half-scissor (adjacent column reach; ignores all other awkward finger mechanics)
    #----------------------------------------------------------------------------------    
   
    # 1. Key preferences (empirical Bradley-Terry tiers inside left finger-columns)
    #    0.137 - 1.000: keys inside the 8 finger-columns
    #    0.000: keys outside the 8 finger-columns 
    tier_values = {
        'F': 1.000, 'J': 1.000,
        'D': 0.870, 'K': 0.870,
        'E': 0.646, 'I': 0.646,
        'S': 0.646, 'L': 0.646,
        'V': 0.568, 'M': 0.568,
        'R': 0.568, 'U': 0.568,
        'W': 0.472, 'O': 0.472,
        'A': 0.410, ';': 0.410,
        'C': 0.410, ',': 0.410,
        'Z': 0.137, '/': 0.137,
        'Q': 0.137, 'P': 0.137,
        'X': 0.137, '.': 0.137
    }

    key_score = 0
    for key in [char1, char2]:
        key_score += tier_values.get(key, 0)  # Get tier value or 0 if not found

    scores['key_preference'] = key_score / 2.0  # Average over 2 keys

    # 2. Row separation (empirical meta-analysis of left same-row, reach, and hurdle key-pairs) 
    #    1.000: 2 hands
    #    1.000: 2 keys in the same row
    #    0.588: 2 keys in adjacent rows (reach)
    #    0.000: 2 keys straddling home row (hurdle)
    if hand1 != hand2:
        scores['row_separation'] = 1.0        # Two hands
    else:
        if row_gap == 0:
            scores['row_separation'] = 1.0    # Same row
        elif row_gap == 1:
            scores['row_separation'] = 0.588  # Adjacent row (reach)
        else:
            scores['row_separation'] = 0.0    # Skip row (hurdle)

    # 3. Same-row finger order and column separation
    #    - (empirical analysis of left key-pairs toward vs. away from the thumb)
    #    - (empirical meta-analysis of left key-pairs in adjacent vs. remote columns) 
    #    1.000: 2 hands
    #    1.000: adjacent columns, inward roll, in the same row
    #    0.779: adjacent columns, outward roll, in the same row
    #    0.750: remote columns, inward roll, in the same row
    #    0.779 x 0.750: remote columns, outward roll, in the same row
    #    0.500: different rows, different fingers
    #    0.000: same finger
    if hand1 != hand2:
        scores['same_row'] = 1.0        # Two hands
    elif finger1 == finger2:
        scores['same_row'] = 0.0        # Same finger
    elif row_gap == 0:  # Same row logic

        # Apply same-row finger order/direction (stronger effect)
        if finger2 > finger1:           # Inward
            scores['same_row'] = 1.0
        elif finger2 < finger1:         # Outward  
            scores['same_row'] = 0.779
        
        # Apply column separation penalty (weaker effect)
        if column_gap >= 2:             # Remote columns
            scores['same_row'] *= 0.750

    else:
        scores['same_row'] = 0.5        # Different rows, different fingers

    # 4. Same-finger (empirical analysis of left same- vs. different finger inside finger-columns)
    #    1.0: 2 hands
    #    1.0: 2 fingers
    #    0.0: 1 finger
    if hand1 != hand2:
        scores['same_finger'] = 1.0          # Two hands
    elif finger1 != finger2:
        scores['same_finger'] = 1.0          # Two fingers
    else:
        scores['same_finger'] = 0.0          # Same finger

    # 5. Outside reach (empirical analysis of left-hand lateral stretches outside finger-columns)
    #    1.000: 0 outside keys
    #    0.846: 1 outside key
    #    0.716: 2 outside keys
    qwerty_home_blocks_set = set(qwerty_home_blocks)  # Convert to set for O(1) lookup performance

    # Count how many keys are outside the home blocks
    outside_count = sum(1 for key in [char1, char2] if key not in qwerty_home_blocks_set)

    # Apply score based on count
    outside_scores = {0: 1.0, 1: 0.846, 2: 0.716}
    scores['outside'] = outside_scores[outside_count]

    # 6. Scissor (adjacent column hurdle; ignores all other awkward finger mechanics)
    #    1.0: 2 hands
    #    1.0: non-scissor
    #    0.0: scissor
    scores['scissor'] = 1.0              # Default score
    if hand1 != hand2:
        scores['scissor'] = 1.0          # Two hands
    elif finger1 != finger2:
        if column_gap == 1 and row_gap == 2:
            scores['scissor'] = 0.0      # Adjacent hurdle

    # 7. Half-scissor (adjacent column reach; ignores all other awkward finger mechanics)
    #    1.0: 2 hands
    #    1.0: non-half-scissor
    #    0.0: half-scissor
    scores['half_scissor'] = 1.0              # Default score
    if hand1 != hand2:
        scores['half_scissor'] = 1.0          # Two hands
    elif finger1 != finger2:
        if column_gap == 1 and row_gap == 1:
            scores['half_scissor'] = 0.0      # Adjacent reach


    return scores

def get_all_qwerty_keys():
    """Get all standard QWERTY keys for testing."""
    return list("QWERTYUIOPASDFGHJKL;ZXCVBNM,./'[")
