# coding: utf-8
import pandas as pd
from jeeves.preprocessing.text import remove_stopwords, rem_unicode, remove_punctuation, remove_digits
from wordcloud import WordCloud

df = pd.read_table("tabularcfp.tsv", usecols='title Description:'.split())
textData = df.apply(" ".join, axis=1)
for cleaner in [lambda x: x.lower(), remove_stopwords, rem_unicode, remove_punctuation, remove_digits]:
    textData = textData.apply(cleaner)

extra_words = "python talk using used".split()
extra_words.extend("use one code also project make based following tool".split())

for word in extra_words:
    textData = textData.str.replace(word, "")

im = WordCloud().generate(" ".join(textData)).to_image()
im.show()
