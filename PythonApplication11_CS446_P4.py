import json, re, copy, time, os, sys
from pprint import pprint

class Inverted():
    def __init__(self, file, inverted={}):
        self.file_name = file
        self.query = None
        self.json_data = None
        self.inverted_index = inverted

    def input_file(self):
        # creates a list of dictionaries from json
        self.file = open(self.file_name)
        self.json_data = json.load(self.file)
        self.json_data = self.json_data['corpus']

    def input_query(self):
        id = None
        self.query = raw_input("Query: ")
        #self.query = open('input.txt', 'r')
        #self.query = self.query.readline()

        # scene or play
        if "scene" in self.query:
            id = "sceneId"
        elif "play" in self.query:
            id = "playId"
        else:
            query = ""
            while ("scene" not in query):
                query = raw_input("scene or play? ").lower()
                id = "sceneId"
                if "play" in query:
                    id = "playId"
                    break

        # string between where and is
        word = self.query.split()
        pos = []
        for i in range(len(word)):
            if word[i] == "is":
                pos.append(i)
                break
            elif word[i] == "where":
                pos.append(i+1)

        # Term based Queries
        # 1. Find scene(s) where "thee" or "thou" is used more than "you"
        
        # Phrase based Queries
        # 2. Find scene(s) where "lady macbeth" is mentioned

        # extract main terms
        main_terms = []
        term_pos = range(pos[0], pos[1])
        for x in range(len(term_pos)):
            main_terms.append(word[term_pos[x]])

        # check for comparison: if yes add compare term
        compare_term = []
        if self.query_is_comparison:
            match = re.findall(r'"\w+"', self.query)
            for item in match:
                if item not in main_terms:
                    compare_term.append(item)
        
        # check if phrase based query
        query_type = "term"
        match = re.findall(r'"[\w\s]+"', self.query)
        for item in match:
            if len(item.split()) > 1:
                query_type = "phrase"

        # strip before processing
        temp_main_terms = []
        for stripped in main_terms:
            temp_main_terms.append(stripped.strip('"'))
        main_terms = copy.deepcopy(temp_main_terms)

        # process the query
        self.process_query(id, query_type, main_terms, compare_term)

    def process_query(self, id, type, main, compare):
        # initial setup
        list_of_results = []

        # boolean in main terms
        if type == "term":
            # OR
            if "or" in main:
                for term in main:
                    term = term.strip('",').lower()
                    if not term == "or":
                        result = self.term_subprocess_query(term, id, compare, list_of_results)
        
            # AND
            # assuming all names are in inverted index
            elif "and" in main:
                pass
        
            else:
                for term in main:
                    term = term.strip('"')
                    result = self.term_subprocess_query(term, id, compare, list_of_results)

        elif type == "phrase":
            # use position based search
            # only supports one phrase for now
            result = self.phrase_subprocess_query(main, id, compare, list_of_results)
        
        pprint(sorted(result))

    def term_subprocess_query(self, term, id, compare, list_of_results):
        if self.inverted_index.has_key(term):
            term_list = self.inverted_index[term]
            # main term
            for term_dicts in term_list:
                term_count = len(term_dicts['pos'])
                # compare term
                if len(compare) > 0:
                    for compare_dicts in self.inverted_index[compare[0].strip('"')]:
                        if compare_dicts[id] == term_dicts[id]:
                            compare_count = len(compare_dicts['pos'])
                            if term_count > compare_count:
                                if not term in list_of_results:
                                    list_of_results.append(term)
                                if not term_dicts[id] in list_of_results:
                                    list_of_results.append(term_dicts[id])
                else:
                    if not term_dicts[id] in list_of_results:
                        list_of_results.append(term_dicts[id])
        return list_of_results

    def phrase_subprocess_query(self, terms, id, compare, list_of_results):
        # search for phrases in documents
        if self.inverted_index.has_key(terms[0]):
            term_list = self.inverted_index[terms[0]]
            # each dictionary in first term
            for term_dict in term_list:
                temp_terms = [terms[0]]
                pos = term_dict['pos']
                for position in pos:
                    # for all following terms in phrase
                    for index in range(1, len(terms)):
                        #print "term: ", terms[index], position+index
                        temp_terms = self.subphrase_process(terms[index], id, term_dict[id], position + index, temp_terms)
                    # if phrase found in that scene/play: break
                    if len(terms) == len(temp_terms):
                        if not term_dict[id] in list_of_results:
                            list_of_results.append(term_dict[id])

        return list_of_results

    def subphrase_process(self, term, id, id_info, position, results):
        # search that term in that position
        term_list = self.inverted_index[term]
        # main term
        for term_dicts in term_list:
            if term_dicts[id] == id_info:
                if term_dicts['pos'].count(position) > 0:
                    results.append(term)
                    break
        return results
        
    def query_is_comparison(self):
        conditions = ["used more than", "greater than"]

        for condition in conditions:
            if condition in self.query:
                return True

    def create_inverted_indexes(self):
        # check if saved inverted indexes exist
        fname = self.file_name.split('.')[0] + "-output.json"
        if os.path.isfile(fname):
            try:
                # you need to open the file before you load it ot json
                with open(fname, 'rb') as fp:
                    self.inverted_index = json.load(fp)
            except:
                print "Incorrect file json data, creating new"
                os.remove(fname)
                self.create_inverted_indexes()

        else:
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
            self.save_inverted_indexes()

    def save_inverted_indexes(self):
        # saves inverted index in json format to a file
        save_file = self.file_name.split(".")[0] + "-output.json"
        with open(save_file, 'wb') as outfile:
            json.dump(self.inverted_index, outfile, indent=2, sort_keys=True)
                
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
    file = "shakespeare-scenes.json"
    I = Inverted(file)
    I.input_file()
    I.create_inverted_indexes()
    I.input_query()
