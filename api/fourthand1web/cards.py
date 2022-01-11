import importlib
import json
import os

import fourthand1
from fourthand1.cards import DefenseCard, OffenseCard

_OFFENSE_CARDS = {}
_DEFENSE_CARDS = {}


def _card_filepaths(path):
    cards_filepath = importlib.resources.files(fourthand1) / "data" / "cards" / path
    return [cards_filepath / filepath for filepath in os.listdir(cards_filepath)]

def _offense_card_filepaths():
    return _card_filepaths("offense")

def _defense_card_filepaths():
    return _card_filepaths("defense")

def _init_cards():
    global _OFFENSE_CARDS, _DEFENSE_CARDS
    for path in _offense_card_filepaths():
        with open(path) as card_file:
            card_json = json.load(card_file)
        _OFFENSE_CARDS[card_json["id"]] = OffenseCard.create(**card_json)
    for path in _defense_card_filepaths():
        with open(path) as card_file:
            card_json = json.load(card_file)
        _DEFENSE_CARDS[card_json["id"]] = DefenseCard.create(**card_json)


def get_offense_card(card_id):
    return _OFFENSE_CARDS.get(card_id)

def get_defense_card(card_id):
    return _DEFENSE_CARDS.get(card_id)

def get_all_offense_cards():
    return [get_offense_card(id) for id in _OFFENSE_CARDS.keys()]

def get_all_defense_cards():
    return [get_defense_card(id) for id in _DEFENSE_CARDS.keys()]


_init_cards()
