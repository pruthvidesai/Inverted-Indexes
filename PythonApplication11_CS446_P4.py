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
            # for each term in text
            length_text = len(text)
            print length_text
            temp_text = copy.deepcopy(text)
            temp_dict = {'pos':[]}
            # for term in each packet
            for term in range(length_text):
                # if not in main dict
                if not self.inverted_index.has_key(text[term]):
                    self.inverted_index[text[term]] = []
                    # create a dict for term values
                    temp_dict = {'pos':[]}
                    temp_dict['playId'] = packet['playId']
                    temp_dict['sceneId'] = packet['sceneId']
                    temp_dict['sceneNum'] = packet['sceneNum']
                    # add term to main dict
                    self.inverted_index[text[term]].append(temp_dict)
                

    def print_indexes(self):
        pprint(self.inverted_index)

if __name__ == '__main__':
    file = "1.json"
    I = Inverted(file)
    I.input()
    I.create_inverted_indexes()
    I.print_indexes()
