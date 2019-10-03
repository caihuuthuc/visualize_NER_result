import re
from spacy import displacy
from collections import defaultdict
from bs4 import BeautifulSoup
import json
import os
def process_one_sentence(src_sentence):
    last_label = 'O'
    start = -1
    len_processed_token = -1
    tokens = list()
    end = -1
    begin_of_sentence = True
    sentence = []
    ents = list()
    
    for line in src_sentence:
        word, label = re.split('\t', line.strip())
        if begin_of_sentence: #con trỏ đang ở đầu câu
            if label != 'O': #label ở đầu câu khác O
                  tokens.append(word)
        else: #Con trỏ ở giữa câu
            if last_label != 'O': #Label trước đó khác O
                if label == last_label: #Vẫn chưa kết thúc mention
                    tokens.append(word)
                else: #Kết thúc mention
                    end = len_processed_token
                    start = end - sum([len(w) for w in tokens]) - len(tokens) + 1
                    ents.append({'start': start, 'end': end, 'label': last_label})
                    tokens = list()
                    if label != 'O':
                        tokens.append(word)
            else:
                if label != 'O':
                    tokens.append(word)
        last_label = label
        begin_of_sentence = False
        sentence.append(word)
        len_processed_token += len(word) + 1

    if last_label != 'O':
        end = len_processed_token
        start = end - sum([len(w) for w in tokens]) - len(tokens) + 1
        len_processed_token = end
        ents.append({'start': start, 'end': end, 'label': last_label})
        tokens = list()

    doc = {
        'text': " ".join(sentence),
        "ents": ents,
        'title': None
    }
    
    return doc

config_colors_fn = 'config_colors.json'
if not os.path.exists(config_colors_fn):
    raise 'Config file not found'

with open(config_colors_fn) as fin:
    options = json.load(fin)

def convert_sf_result_to_html(sf_result: str):
    lines = list()
    for line in re.split(',', sf_result.strip()):
        lines.append(re.sub(':', '\t', line.strip()))
    doc = process_one_sentence(lines)
    html = displacy.render(doc, style='ent', options=options, manual=True, page=True)
    soup = BeautifulSoup(html, 'html.parser')
    figure = soup.find('figure')
    
    return str(figure)


if __name__ == '__main__':
    string = 'tìm:O, dùm:O, địa:O, chỉ:O, trường:OBJ-ENTITY, hồng:OBJ-NAME, bàng:OBJ-NAME'
    figure = convert_sf_result_to_html(string)

    import pprint as pp
    pp.pprint(figure)
    with open('/home/thuc/Desktop/test_before_up_github.txt', 'w', encoding='utf-8') as fout:
        fout.write(figure)
