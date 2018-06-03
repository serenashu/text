# -*- coding: utf-8 -*-
"""
Created on Thu May 31 19:15:42 2018

@author: Yommyshu
"""

# download SEC bank financial statements
# Goes to the SEC file and automatically construct the dictionary, then we can extract the MD&A stuff

import numpy as np
import os
import pandas as pd
import requests
import codecs
from html.parser import HTMLParser


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


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# Two output directories, one for the 10-Ks, one for the Edgar index. They
# need to exist.
save_dir = '10K/'
index_dir = 'index/'
path = 'E:/Researchcode/Banktext'  # path to where to save your files

# create the directory on local machine, these will create two different folder names
dir_ = (path + index_dir)
savedir_ = (path + save_dir)

# This will create a directory called 10k and index
if not os.path.exists(dir_):
    os.mkdir(dir_)
    os.mkdir(savedir_)

# os.mkdir:Create a directory named path with numeric mode mode.     


# First, download the index files. Start from 2016 and end in 2016
start_year = 1993  # Min 1993
start_quarter = 1  # (1-4)
end_year = 2017
end_quarter = 4

# Generate the list of quarterly index files to download.
# Creates a list of tuples, so you have a list under the name qtr_list and inside
# it will have (2016,Q1) etc 

qtr_list1 = [(start_year, q + 1) for q in range(start_quarter - 1, 4)]
qtr_list2 = [(y, q + 1) for y in range(start_year + 1, end_year)
             for q in range(4)]
qtr_list3 = [(end_year, q + 1) for q in range(0, end_quarter)]
qtr_list = qtr_list1 + qtr_list2 + qtr_list3

print(qtr_list1)
print(qtr_list2)
print(qtr_list3)
print(qtr_list)

# Download all the quarterly index files. 
# Now it will loop over the tuples, y is the year, and q is the quarter 
# So it will automatically download each quarterly-yearly master file

for y, q in qtr_list:
    url = ('https://www.sec.gov/Archives/edgar/full-index/' + str(y)
           + '/QTR' + str(q) + '/master.gz')
    print('Downloading ' + str(y) + '-Q' + str(q) + ' ...')
    with open(dir_ + 'master_' + str(y) + '-Q' + str(q) + '.gz', 'wb') as f:
        f.write(requests.get(url).content)
    print('Done')

# Load all index files in pandas.
# Now loop over these files and use pandas.
# If you unzip these files, you get txt files. So you need to use a delimiter 
# Skip the 11 lines since they are copyright stuff
# Then it gets the names, CIK etc
# Here are all of the companies and their names    

idx_list = [x for x in os.listdir(dir_) if not x.startswith('.')]
dfs = []
print(idx_list)
print(dir_)
import csv

df = pd.read_csv('E:/Researchcode/Banktextindex/master_1993-Q1.gz', delimiter='|',
                 names=['CIK', 'Company Name', 'Form Type',
                        'Date Filed', 'Filename'],
                 skiprows=11)
print(df)
help(pd.read_csv)

for x in idx_list:
    df = pd.read_csv(dir_ + x, delimiter='|',
                     names=['CIK', 'Company Name', 'Form Type',
                            'Date Filed', 'Filename'], encoding='latin-1',
                     skiprows=11)
    dfs.append(df)
print(df)
master = pd.concat(dfs)
print(master)
# Click on 'master' then just run this part by right clickign to see the form types
# dfs = [] is a list and then you just concatinate 


# Extract only 10-Ks, 
master_10k = master[master['Form Type'] == '10-K']
master_10q = master[master['Form Type'] == '10-Q']
print(master_10k)

# Extract bank 10-Q
comp = pd.read_csv('E:/Researchcode/Banktext/Bankcik.csv')
master_10q_bank = master_10q[master_10q['CIK'].isin(comp['CIK'])]
master_10q_bank.sort_values(by=['CIK', 'Date Filed'])

master_10k_bank = master_10k[master_10k['CIK'].isin(comp['CIK'])]

# Get the Filename (includes part of the path.) If you have more file names for a given 
# company, it will loop over these files 

fn_list = [x for x in master_10k_bank['Filename']]

# Download all the files from EDGAR 
for fn in fn_list:
    url = 'https://www.sec.gov/Archives/' + fn
    print('Downloading ' + fn + ' ...')
    with open(savedir_ + fn.split('/')[-1], 'wb') as f:
        f.write(requests.get(url).content)
    print('Done')

# %%dictionary
url = 'https://www3.nd.edu/~mcdonald/Word_Lists_files/LoughranMcDonald_MasterDictionary_2014.xlsx'

lm = pd.read_excel(url)
lmpos = list(lm[lm.Positive != 0]['Word'])
lmneg = list(lm[lm.Negative != 0]['Word'])
lmunc = list(lm[lm.Uncertainty != 0]['Word'])

del mda

# %% Extract the MD&A section
savedir_ = 'E:/Researchcode/Banktext/Banktext10K'
files = os.listdir(savedir_)
for f in files:
    with codecs.open(savedir_ + f, 'rb', encoding='latin-1') as fin:
        text = fin.read()

        # Since the MDA section is very constant, you can select everything that is between
        # the ITEM7s and ITEM8s. If he doesn't find it, it will say -1
        # All information between items that will start  with ITEM 7 and end with ITEM 8

        item7_begins = ['ITEM 7.', 'ITEM 7 –', 'ITEM 7:', 'ITEM 7 ',
                        'Item 7.', 'Item 7 –', 'Item 7:', 'Item 7 ']
        item7_ends = ['ITEM 8', 'Item 8', 'Item 8.']

        beg = []
        for tx in item7_begins:
            if text.find(tx) != -1:
                beg.append(text.rfind(tx))

        end = []
        for tx in item7_ends:
            if text.find(tx) != -1:
                end.append(text.rfind(tx))

        # Text is where the MDA is. .STRIP() gets rid off the extra spaces
        mda = text[beg[0]:end[0]].strip()
        mda = strip_tags(mda)

        # remove numbers
        mda = ''.join([i for i in mda if not i.isdigit()])

        # remove unwanted characters
        for notwanted in [',,', '$', ':', ',', '.', '%', ';', '|',
                          '\xa0', '&gt', '&apos', '&amp', '&quot',
                          'Form -K', '\\', '0x92']:
            mda = mda.replace(notwanted, ' ')

        # Capitalize because words in LM are in CAPs
        mda = mda.upper()

        # Convert string into list
        mda = mda.split()
        df_mda = pd.DataFrame(mda, columns=["words"])
        df_mda.to_csv(savedir_ + f + 'cleaned.csv', index=False)

# load LM dictionnary
# get the Loughran McDonald MasterDictionary at 

# %%
nwords = len(mda)
npos = len([i for i in mda if i in lmpos])
nneg = len([i for i in mda if i in lmneg])
nunc = len([i for i in mda if i in lmunc])

""" NLTK - Really important package in textual analysis """
import nltk

# http://www.nltk.org/
# http://www.nltk.org/book/ch01.html

tokens = [t for t in mda]
freq = nltk.FreqDist(tokens)
for key, val in freq.items():
    print(str(key) + ':' + str(val))
