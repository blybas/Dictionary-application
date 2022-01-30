"""
Blythe Bassart
CS3B Assignment 10, Online Dictionary
November 29, 2021
"""
import requests

import json

import time

from enum import Enum

from datalist import *


class DictionaryEntry:
    def __init__(self, word, part_of_speech, definition, example=None):
        self.word = word
        self.part_of_speech = part_of_speech
        self.definition = definition
        self.example = example

    def __str__(self):
        return (f"Word          : {self.word}\n"
                f"Part of speech: {self.part_of_speech}\n"
                f"Definition    : {self.definition}\n"
                f"Example       : {self.example}")


class LocalDictionary:
    def __init__(self, dictionary_json_name="dictionary.json"):
        with open(dictionary_json_name) as file:
            self._dictionary = {}
            data = json.load(file, object_hook=self.dictionary_entry_decoder)
            for d in data["entries"]:
                if isinstance(d, DictionaryEntry):
                    self._dictionary[d.word.lower()] = d

    def dictionary_entry_decoder(self, o):
        try:
            if "example" in o:
                example = o["example"]
            else:
                example = None

            return DictionaryEntry(word=o["word"],
                                   part_of_speech=o["part_of_speech"],
                                   definition=o["definition"],
                                   example=example)
        except (KeyError, TypeError):
            return o

    def search(self, word):
        return self._dictionary[word.lower()]


class OxfordDictionary:

    APP_ID = "85481fc3"
    APP_KEY = "4178487b609ca98c5f347c197bc9c112"

    def search(self, word):
        self.word = word

        language = "en-us"
        word_id = self.word

        url = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/" + word_id.lower()

        r = requests.get(url, headers={"app_id": self.APP_ID, "app_key": self.APP_KEY})

        if r.status_code != 200:
            raise KeyError(f'Cannot find "{word}"')

        json_resp = r.json()

        if "examples" in json_resp["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]:
            try:
                example = json_resp["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["examples"][1]["text"]
            except IndexError:
                example = None
        else:
            example = None

        return DictionaryEntry(
            word=self.word,
            part_of_speech=json_resp["results"][0]["lexicalEntries"][0]
                                    ["lexicalCategory"]["id"],
            definition=json_resp["results"][0]["lexicalEntries"][0]
                                ["entries"][0]["senses"][0]["definitions"][0],
            example=example
        )


class DictionaryEntryCache(DataList):
    MIN_CAPACITY = 1

    def __init__(self, capacity=1):
        super().__init__()
        if capacity < self.MIN_CAPACITY:
            raise ValueError("Capacity should be at least 1")
        self.capacity = capacity
        self.count = 0

    def add(self, entry):
        if not isinstance(entry, DictionaryEntry):
            raise TypeError("entry should be DictionaryEntry")
        self.add_to_head(entry)
        self.count += 1
        if self.count > self.capacity:
            self.remove_tail()

    def remove_tail(self):
        self.reset_current()
        current = self.iterate()
        while current:
            if current.next is None:
                raise RuntimeError("Something's very wrong")

            if current.next.next is None:
                current.remove_after()
                break
            current = self.iterate()
        self.count -= 1

    def search(self, word):
        self.reset_current()
        current = self.iterate()
        while current:
            if current.data.word.lower() == word.lower():
                entry = current.data
                self.remove(entry)
                self.add_to_head(entry)
                return entry
            current = self.iterate()
        raise KeyError(f"Cannot find {word}")


class DictionarySource(Enum):
    LOCAL = 1
    CACHE = 2
    OXFORD_ONLINE = 3

    def __str__(self):
        return self.name


class Dictionary:
    def __init__(self, source=DictionarySource.OXFORD_ONLINE):
        self.source = source
        if self.source is DictionarySource.OXFORD_ONLINE:
            self.dictionary = OxfordDictionary()
        elif self.source is DictionarySource.LOCAL:
            self.dictionary = LocalDictionary()
        else:
            raise ValueError("Source must be DictionarySource: LOCAL or OXFORD_ONLINE")


        self.dictionary_entry_cache = DictionaryEntryCache(1)

    def search(self, word):

        start = time.perf_counter()
        try:
            result, duration = time_func(self.dictionary_entry_cache.search, word)
            return result, DictionarySource.CACHE, duration
        except KeyError:
            result, duration = time_func(self.dictionary.search, word)
            self.dictionary_entry_cache.add(result)
            return result, self.source, duration


def time_func(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return result, duration


def main():
    dictionary = Dictionary()
    while True:
        word = input("Enter a word to lookup: ")
        try:
            entry, source, duration = dictionary.search(word)
            print(f"{entry}\n(Found in {source} in {duration} seconds)\n")
        except requests.exceptions.ConnectionError as e:
            print(f"Error when searching: {str(e)}\n")


if __name__ == '__main__':
    main()
    # dictionary = Dictionary()
    # first_search = dictionary.search("ace")
    # print(first_search)
    # second_search = dictionary.search("ace")
    # print(second_search)


