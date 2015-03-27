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
        #print self.json_data

    def query(self):
        pass

    def create_inverted_indexes(self):
        # each packet in the list
        for packet in self.json_data:
            # strip terms from text
            text = packet['text'].split()
            length_text = len(text)
            # for term in each packet
            for term in range(length_text):
                # creates list of dicts for new term
                if not self.inverted_index.has_key(text[term]):
                    self.inverted_index[text[term]] = []
                    term_dict = {}
                    term_dict['playId'] = packet['playId']
                    term_dict['sceneId'] = packet['sceneId']
                    term_dict['sceneNum'] = packet['sceneNum']
                    term_dict['pos'] = []
                    self.inverted_index.get(text[term]).append(term_dict)
                # for a term that already exists
                for dicts in self.inverted_index.get(text[term]):
                    if dicts['sceneId'] == packet['sceneId']:
                        dicts['pos'].append(term + 1)
                

    def print_indexes(self):
        pprint(self.inverted_index)
        #pprint(self.json_data)

if __name__ == '__main__':
    file = "1.json"
    I = Inverted(file)
    I.input()
    I.create_inverted_indexes()
    I.print_indexes()
