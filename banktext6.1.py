# -*- coding: utf-8 -*-
"""
Created on Thu May 31 19:15:42 2018

@author: Yommyshu
"""


#%%dictionary
url = 'https://www3.nd.edu/~mcdonald/Word_Lists_files/LoughranMcDonald_MasterDictionary_2014.xlsx'
 
lm = pd.read_excel(url)
lmpos = list(lm[lm.Positive!=0]['Word'])
lmneg = list(lm[lm.Negative!=0]['Word'])
lmunc = list(lm[lm.Uncertainty!=0]['Word'])
 
del mda
 

import re
#%% Extract the MD&A section
savedir_ = 'E:/Researchcode/Banktext10Q/'
files = os.listdir(savedir_)
print (files)
for f in files:
    with codecs.open(savedir_+f,'rb',encoding='latin-1') as fin:
        text = fin.read()
     
#Since the MDA section is very constant, you can select everything that is between
# the ITEM7s and ITEM8s. If he doesn't find it, it will say -1 
# All information between items that will start  with ITEM 7 and end with ITEM 8    
 
        item2_begins = ['ITEM 2.', 'ITEM 2 –', 'ITEM 2:', 'ITEM 2 ',
                'Item 2.', 'Item 2 –', 'Item 2:', 'Item 2 ']
        item2_ends   = ['ITEM 3', 'Item 3', 'ITEM 3.', 'Item 3.']
 
        beg = []
        for tx in item2_begins:
            if text.find(tx) != -1:
                beg.append(text.rfind(tx))
 
        end = []
        for tx in item2_ends:
            if text.find(tx) != -1:
                end.append(text.rfind(tx))
 
    
#Text is where the MDA is. .STRIP() gets rid off the extra spaces
        mda = text[beg[0]:end[0]].strip()
        mda = strip_tags(mda)

# remove white space and new lines
        mda1 = re.sub('\s+',' ',mda)  
        
        
        
 
# remove unwanted characters
        for notwanted in [',,', '$', ':', ',', '.', '%', ';', '|',
                  '\xa0', '&gt', '&apos', '&amp', '&quot',
                  'Form -K', '\\', '0x92','*','"','---','(',')','=','-','/','======','...','&']:
            mda = mda.replace(notwanted, ' ')
 
    

# Capitalize because words in LM are in CAPs
        mda = mda.upper()
 
# Convert string into list
        mda = mda.split()
        df_mda = pd.DataFrame(mda, columns=["words"])
        df_mda.to_csv(savedir_+f+'cleaned.csv', index=False)
 
# load LM dictionnary
# get the Loughran McDonald MasterDictionary at 
 
#%%
nwords = len(mda)
npos = len([i for i in mda if i in lmpos])
nneg = len([i for i in mda if i in lmneg])
nunc = len([i for i in mda if i in lmunc])
 
 
""" NLTK - Really important package in textual analysis """
import nltk
# http://www.nltk.org/
# http://www.nltk.org/book/ch01.html
 
tokens = [t for t in mda]
freq= nltk.FreqDist(tokens)
for key,val in freq.items(): 
    print (str(key) + ':' + str(val))





