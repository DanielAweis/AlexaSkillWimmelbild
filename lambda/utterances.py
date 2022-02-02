import json
import random

UTTERANCES = "jsondata/utterances.json"

def load_utterances(file_name):
    """Loads a json file and returns dictionary """
    with open(file_name, encoding="utf-8") as file:
        utterances = json.load(file)
    return utterances

def choose_utterance(modus, step):
    """Choose random utterance for according modus and step. """
    utt_dict = load_utterances(UTTERANCES)
    modus_dict = utt_dict[modus]
    return  random.choice(modus_dict[step])
    