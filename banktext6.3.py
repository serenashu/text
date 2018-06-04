import codecs
import logging
import os
import re
import tempfile
from html.parser import HTMLParser
from pprint import pprint  # pretty-printer

import pandas as pd
from six import iteritems
from smart_open import smart_open
from gensim import corpora
from collections import defaultdict


class MyCorpus(object):
    def __iter__(self):
        for line in smart_open('E:/dataset/mycorpus.txt', 'rb'):
            # assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())


# This gets rid off all HTML tag lines
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


if __name__ == "__main__":
    bank_text_dir = 'Banktext10Q/'
    bank_text_files = os.listdir(bank_text_dir)
    latin_encoding = 'latin'

    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    corpus = {}

    # for bank_text_file in bank_text_files:
    #     with codecs.open(bank_text_dir + bank_text_file, 'rb', encoding=latin_encoding) as fin:
    #         corpus.append(fin.read())

    # %% Extract the MD&A section
    bank_text_dir = 'Banktext10Q/'
    cleandir_ = 'Banktext10QClean'
    bank_text_files = os.listdir(bank_text_dir)
    print(bank_text_files)
    for bank_text_file in bank_text_files:
        with codecs.open(bank_text_dir + bank_text_file, 'rb', encoding=('%s-1' % latin_encoding)) as fin:
            text = fin.read()

            # Since the MDA section is very constant, you can select everything that is between
            # the ITEM7s and ITEM8s. If he doesn't find it, it will say -1
            # All information between items that will start  with ITEM 7 and end with ITEM 8

            # item2_begins = ['ITEM 2.', 'ITEM 2 –', 'ITEM 2:', 'ITEM 2 ',
            #                 'Item 2.', 'Item 2 –', 'Item 2:', 'Item 2 ']
            # item2_ends = ['ITEM 3', 'Item 3', 'ITEM 3.', 'Item 3.']

            # beg = []
            # for tx in item2_begins:
            #     if text.find(tx) != -1:
            #         beg.append(text.find(tx))
            #
            # end = []
            # for tx in item2_ends:
            #     if text.find(tx) != -1:
            #         end.append(text.find(tx))
            #
            # # Text is where the MDA is. .STRIP() gets rid off the extra spaces
            # for beg_i, end_i in beg end:

            all_matched_tockens = re.findall(r"(item\s?2\.?-?:?)(.*)(item\s?3\.?-?:?)", text, re.I | re.S)

            mda = all_matched_tockens[-1][1].strip()
            mda = strip_tags(mda)

            # remove numbers
            mda = ''.join([i for i in mda if not i.isdigit()])

            # remove unwanted characters
            # remove unwanted characters
            for notwanted in [',,', '$', ':', ',', '.', '%', ';', '|',
                              '\xa0', '&gt', '&apos', '&amp', '&quot',
                              'Form -K', '\\', '0x92', '*', '"', '---', '(', ')', '=', '-', '/', '======', '...', '&']:
                mda = mda.replace(notwanted, ' ')

            # remove white space and new lines
            mda = re.sub('\s+', ' ', mda)

            # Capitalize because words in LM are in CAPs
            mda = mda.upper()
            corpus[bank_text_file] = mda



    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    TEMP_FOLDER = tempfile.gettempdir()
    print('Folder "{}" will be used to save temporary dictionary and corpus.'.format(TEMP_FOLDER))


    documents = ["Human machine interface for lab abc computer applications applications",
                 "A survey of user opinion of computer system response time",
                 "The EPS user interface management system",
                 "System and human system engineering testing of EPS",
                 "Relation of user perceived response time to error measurement",
                 "The generation of random binary unordered trees",
                 "The intersection graph of paths in trees",
                 "Graph minors IV Widths of trees and well quasi ordering",
                 "Graph minors A survey"]

    # remove common words and tokenize
    stoplist = set('for a of the and to in'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist]
             for document in documents]
    print(texts)
    # remove words that appear only once

    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    print(texts)

    pprint(texts)

    pprint(texts)

    dictionary = corpora.Dictionary(texts)
    dictionary.save(os.path.join(TEMP_FOLDER, 'deerwester.dict'))  # store the dictionary, for future reference
    print(dictionary)

    print(dictionary.token2id)

    new_doc = "Human computer interaction"
    new_vec = dictionary.doc2bow(new_doc.lower().split())
    print(new_vec)  # the word "interaction" does not appear in the dictionary and is ignored

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize(os.path.join(TEMP_FOLDER, 'deerwester.mm'), corpus)  # store to disk, for later use
    for c in corpus:
        print(c)

    corpus_memory_friendly = MyCorpus()
    print(corpus_memory_friendly)

    for vector in corpus_memory_friendly:  # load one vector into memory at a time
        print(vector)

    # collect statistics about all tokens
    dictionary = corpora.Dictionary(line.lower().split() for line in smart_open('E:/dataset/mycorpus.txt', 'rb'))

    # remove stop words and words that appear only once
    stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
                if stopword in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]

    # remove stop words and words that appear only once
    dictionary.filter_tokens(stop_ids + once_ids)
    print(dictionary)
