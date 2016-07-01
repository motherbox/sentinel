# coding: utf-8

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from requests import get
from IPython import embed

DOMAIN = "https://in.pycon.org"

r = get(DOMAIN + "/cfp/2016/proposals/")
soup = BeautifulSoup(r.content, "html.parser")
tags = soup.find_all("a", href=True)

proposal_tags = []

for tag in tags:
    if tag['href'].startswith(r'/cfp/2016/proposals/'):
        assert(len(tag.contents) == 1)
        proposal_tags.append(tag)


def get_proposal_content(tag):
    url = DOMAIN + tag['href']
    r = get(url)
    proposal_soup = BeautifulSoup(r.content, "html.parser")
    paragraphs = proposal_soup.find_all("p")
    text_elements = []
    for para in paragraphs:
        pchildren = list(para.children)
        if len(pchildren) == 1:
            if isinstance(pchildren[0], NavigableString):
                text_elements.append(pchildren[0])
    return text_elements[:3]
