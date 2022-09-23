import json
import random

# Link json file where strings are stored
UTTERANCES = "jsondata/utterances.json"

# Load file with utterances
def load_utterances(file_name):
    """Loads a json file and returns dictionary """
    with open(file_name, encoding="utf-8") as file:
        utterances = json.load(file)
    return utterances

# Extract specific utterance from file (e.g. modus=mood, step=object)
def choose_utterance(modus, step):
    """Choose random utterance for according modus and step. """
    utt_dict = load_utterances(UTTERANCES)
    modus_dict = utt_dict[modus]
    return  random.choice(modus_dict[step])
    