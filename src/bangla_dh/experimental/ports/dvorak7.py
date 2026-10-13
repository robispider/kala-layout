"""Source-derived scoring port of prep/prep_keypair_dvorak7_scores.py at 179e1c08b220ae1b02f6c425a7d1cbd1150c1db2.

Copyright Arno Klein; MIT license: data/evaluators/mechanics-v1/LICENSE.
Extracted by mechanics_sources; scoring bodies and constants are unchanged.
Bangla adaptation is in experimental/mechanics.py.
"""

import csv

from pathlib import Path

from typing import Dict

QWERTY_LAYOUT = {
    # Number row (row 0) - finger numbers
    '1': (0, 1, 'L', 0), '2': (0, 2, 'L', 0), '3': (0, 3, 'L', 0), '4': (0, 4, 'L', 0), '5': (0, 4, 'L', 0),
    '6': (0, 4, 'R', 0), '7': (0, 4, 'R', 0), '8': (0, 3, 'R', 0), '9': (0, 2, 'R', 0), '0': (0, 1, 'R', 0),
    
    # Top row (row 1) - finger numbers
    'Q': (1, 1, 'L', 0), 'W': (1, 2, 'L', 0), 'E': (1, 3, 'L', 0), 'R': (1, 4, 'L', 0), 'T': (1, 4, 'L', 0),
    'Y': (1, 4, 'R', 0), 'U': (1, 4, 'R', 0), 'I': (1, 3, 'R', 0), 'O': (1, 2, 'R', 0), 'P': (1, 1, 'R', 0),
    
    # Home row (row 2) - finger numbers
    'A': (2, 1, 'L', 1), 'S': (2, 2, 'L', 1), 'D': (2, 3, 'L', 1), 'F': (2, 4, 'L', 1), 'G': (2, 4, 'L', 0),
    'H': (2, 4, 'R', 0), 'J': (2, 4, 'R', 1), 'K': (2, 3, 'R', 1), 'L': (2, 2, 'R', 1), ';': (2, 1, 'R', 1),
    
    # Bottom row (row 3) - finger numbers
    'Z': (3, 1, 'L', 0), 'X': (3, 2, 'L', 0), 'C': (3, 3, 'L', 0), 'V': (3, 4, 'L', 0), 'B': (3, 4, 'L', 0),
    'N': (3, 4, 'R', 0), 'M': (3, 4, 'R', 0), ',': (3, 3, 'R', 0), '.': (3, 2, 'R', 0), '/': (3, 1, 'R', 0),
    
    # Additional common keys - finger numbers
    "'": (2, 1, 'R', 0), '[': (1, 1, 'R', 0),
}

STRONG_FINGERS = {3, 4}

HOME_ROW = 2

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

criteria = ['distribution', 
            'strength', 
            'home', 
            'vspan', 
            'columns',
            'remote', 
            'inward']

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

def score_bigram_dvorak7(bigram: str) -> Dict[str, float]:
    """Calculate all 7 Dvorak criteria scores for a bigram."""
    if len(bigram) != 2:
        raise ValueError("Bigram must be exactly 2 characters long")    
    
    char1, char2 = bigram[0].upper(), bigram[1].upper()
    
    # Get key information
    key_info1 = get_key_info(char1)
    key_info2 = get_key_info(char2)
    
    if key_info1 is None or key_info2 is None:
        raise ValueError(f"Invalid keys: {char1}, {char2}")
    
    row1, finger1, hand1, homekey1 = key_info1
    row2, finger2, hand2, homekey2 = key_info2

    in_column1 = is_finger_in_column(char1, finger1, hand1)
    in_column2 = is_finger_in_column(char2, finger2, hand2)

    scores = {}

    #----------------------------------------------------------------------------------
    # Dvorak-7 scoring criteria
    #----------------------------------------------------------------------------------    
    # 1.  Distribution: Typing with 2 hands or 2 fingers
    # 2.  Strength: Typing with stronger fingers 3 and 4
    # 3.  Home row: Typing within the home row
    # 4.  Row separation: Typing in the same row, reaches, and hurdles 
    # 5.  Finger columns: Typing within the 8 finger columns
    # 6.  Remote fingers: Typing with non-adjacent fingers (except fingers 1 and 2)
    # 7.  Inward direction: Finger sequence toward the thumb
    #----------------------------------------------------------------------------------    
   
    # 1. Distribution: Typing with 1 hand or 1 finger
    #    1.0: 2 fingers on 2 hands to type 2 keys
    #    0.5: 2 fingers on 1 hand to type 2 keys
    #    0.0: 1 finger on 1 hand to type 1-2 keys
    if hand1 != hand2:
        scores['distribution'] = 1.0  # 2 fingers on 2 hands to type 2 keys
    elif finger1 != finger2:
        scores['distribution'] = 0.5  # 2 fingers on 1 hand to type 2 keys
    elif finger1 == finger2:
        scores['distribution'] = 0.0  # 1 finger on 1 hand to type 1-2 keys

    # 2. Finger strength: Typing with the stronger two fingers
    #    1.0: 2 keys typed with strong fingers
    #    0.5: 1 key typed with 1 strong finger
    #    0.0: 0 keys typed with strong finger
    strong_count = sum(1 for finger in [finger1, finger2] if finger in STRONG_FINGERS)
    if strong_count == 2:
        scores['strength'] = 1.0      # 2 keys typed with strong fingers
    elif strong_count == 1:
        scores['strength'] = 0.5      # 1 key typed with 1 strong finger
    else:
        scores['strength'] = 0.0      # 0 keys typed with strong finger

    # 3. Home row: Typing within the home row
    #    1.0: 2 home row keys
    #    0.5: 1 home row key
    #    0.0: 0 home row keys
    home_count = sum(1 for row in [row1, row2] if row == HOME_ROW)
    if home_count == 2:
        scores['home'] = 1.0      # 2 home row keys
    elif home_count == 1:
        scores['home'] = 0.5      # 1 home row key
    else:
        scores['home'] = 0.0      # 0 home row keys

    # 4. Row separation: Typing in the same row, reaches, and hurdles 
    #    1.0: 2 keys in the same row, or opposite hands
    #    0.5: 2 keys in adjacent rows (reach)
    #    0.0: 2 keys straddling home row (hurdle)
    if hand1 != hand2:
        scores['vspan'] = 1.0          # opposite hands always score well
    else:
        if row1 == row2:
            scores['vspan'] = 1.0      # 2 keys in the same row
        elif abs(row1 - row2) == 1:
            scores['vspan'] = 0.5      # 2 keys in adjacent rows (reach)
        else:
            scores['vspan'] = 0.0      # 2 keys straddling home row (hurdle)

    # 5. Finger columns: Typing within the 8 finger columns
    #    1.0: 2 keys within finger columns
    #    0.5: 1 key within finger columns
    #    0.0: 0 keys within finger columns
    if in_column1 and in_column2:
        scores['columns'] = 1.0      # 2 keys within finger columns
    elif in_column1 or in_column2:
        scores['columns'] = 0.5      # 1 key within finger columns
    else:
        scores['columns'] = 0.0      # 0 keys within finger columns

    # 6. Remote fingers: Typing with non-adjacent fingers
    #    (except on the same row, or strong pair of fingers 1 and 2)
    #    1.0: non-adjacent fingers, adjacent on same row, strong finger pair, or opposite hands
    #    0.0: same finger, or adjacent fingers where at least one is weak
    if hand1 != hand2:
        scores['remote'] = 1.0      # opposite hands always score well
    elif row1 == row2:
        scores['remote'] = 1.0      # same row always scores well
    elif finger1 == finger2:
        scores['remote'] = 0.0      # same finger scores zero
    elif finger1 in STRONG_FINGERS and finger2 in STRONG_FINGERS:
        scores['remote'] = 1.0      # strong finger pair (index & middle)
    else:
        finger_gap = abs(finger1 - finger2)
        if finger_gap == 1:
            scores['remote'] = 0.0  # adjacent fingers where at least 1 is weak
        elif finger_gap == 2:
            scores['remote'] = 1.0  # non-adjacent fingers: skipping 1 finger
        elif finger_gap == 3:
            scores['remote'] = 1.0  # non-adjacent fingers: skipping 2 fingers

    # 7. Inward direction: Finger sequence toward the thumb
    #    1.0: inward roll, or opposite hands
    #    0.0: outward roll, or same finger
    if hand1 != hand2:
        scores['inward'] = 1.0             # opposite hands always score well
    elif finger1 == finger2:
        scores['inward'] = 0.0             # same finger scores zero
    else:
        if finger1 < finger2:
            scores['inward'] = 1.0         # inward roll
        else:
            scores['inward'] = 0.0         # outward roll

    return scores

def get_all_qwerty_keys():
    """Get all standard QWERTY keys for testing."""

    return list("QWERTYUIOPASDFGHJKL;ZXCVBNM,./'[")
