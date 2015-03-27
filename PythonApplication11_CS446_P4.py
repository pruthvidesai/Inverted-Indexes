import json
import copy
from pprint import pprint
import subprocess

class Inverted():
    def __init__(self, file):
        self.file = file
        self.json_data = None
        self.inverted_index = {}

    def input(self):
        # creates a list of dictionaries from json
        self.file = open(self.file)
        self.json_data = json.load(self.file)
        self.json_data = self.json_data['corpus']

    def query(self):
        pass

    def create_inverted_indexes(self):
        # each packet in the corpus
        for packet in self.json_data:
            text = packet['text'].split()
            # for term in each packet
            for term in range(len(text)):
                # creates a list of dictionaries for new term
                if not self.inverted_index.has_key(text[term]):
                    self.create_term(text[term], packet['playId'], packet['sceneId'], packet['sceneNum'])
                
                # if it's a different scene: create new dictionary
                scene_exists = False
                for dictionary in self.inverted_index.get(text[term]):
                    if dictionary['sceneId'] == packet['sceneId']:
                        scene_exists = True
                if not scene_exists:
                    self.create_term(text[term], packet['playId'], packet['sceneId'], packet['sceneNum'])
                
                # for a term that already exists: add position
                for dicts in self.inverted_index.get(text[term]):
                    if dicts['sceneId'] == packet['sceneId']:
                        dicts['pos'].append(term + 1)
                
    def create_term(self, term, play, scene, num):
        term_dict = {}
        # creates list of dicts for new term
        if not self.inverted_index.has_key(term):
            self.inverted_index[term] = []
        term_dict['playId'] = play
        term_dict['sceneId'] = scene
        term_dict['sceneNum'] = num
        term_dict['pos'] = []
        self.inverted_index.get(term).append(term_dict)

    def print_indexes(self):
        pprint(self.inverted_index)

if __name__ == '__main__':
    file = "1.json"
    I = Inverted(file)
    I.input()
    I.create_inverted_indexes()
    I.print_indexes()
