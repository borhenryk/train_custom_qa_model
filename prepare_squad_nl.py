import os
import json
import time
import mtranslate
from nltk import ngrams
from difflib import SequenceMatcher


with open('squad_en/dev-v2.0.json') as f:
    squad_en = json.load(f)

def translate_squad(squad_eng, dest_lng):
        version = squad_eng['version']
        data = article_parser(squad_eng, dest_lng)
        translated_squad_set = {'version': version, 'data': data}
        with open('pl_squad_dev.json', 'w', encoding='utf-8') as f:
                json.dump(translated_squad_set, f, ensure_ascii=False, indent=4)
        return translated_squad_set

def article_parser(data, dest_lng):
        article_info_all = []
        for article_id in list(range(0, len(data["data"]))):
                article = data["data"][article_id]
                article_title = article['title']
                article_title_nl = str(mtranslate.translate(to_translate=article_title, to_language=dest_lng, from_language="en"))
                paragraph_info = paragraph_parser(article ,dest_lng)
                article_info = {'title': article_title_nl, 'paragraphs': paragraph_info}
                article_info_all.append(article_info)
                print(article_id)
        return article_info_all

def paragraph_parser(article, dest_lng):
        paragraph_info_all = []
        for article_paragraphs_id in range(0, len(article["paragraphs"])):
                article_paragraph = article["paragraphs"][article_paragraphs_id]
                article_paragraph_context = article_paragraph["context"]
                #paragraph_answer_text_nl = str(mtranslate.translate(to_translate=paragraph_answer_text, to_language=dest_lng, from_language="en"))
                try:
                        article_paragraph_context_nl = str(mtranslate.translate(to_translate=article_paragraph_context, to_language=dest_lng, from_language="en"))
                except:
                        continue
                qas_info = qas_parser(article_paragraph, article_paragraph_context_nl, dest_lng)
                paragraph_info = {'qas': qas_info,'context': article_paragraph_context_nl}
                paragraph_info_all.append(paragraph_info)
        return paragraph_info_all


def qas_parser(article_paragraph, article_paragraph_context_nl, dest_lng):
        qas_info_all = []
        for paragraph_qas_id in range(0, len(article_paragraph['qas'])):
                paragraph_qas = article_paragraph['qas'][paragraph_qas_id]
                paragraph_question = paragraph_qas['question']
                try:
                        paragraph_question_nl = str(mtranslate.translate(to_translate=paragraph_question, to_language=dest_lng, from_language="en"))
                except:
                        continue
                paragraph_question_id = paragraph_qas['id']
                paragraph_answer_is_impossible = paragraph_qas['is_impossible']
                if paragraph_qas['is_impossible'] == False:
                        answer_info = answer_parser(paragraph_qas, article_paragraph_context_nl, dest_lng)
                else:
                        answer_info = []
                qas_info = {"question": paragraph_question_nl, "id": paragraph_question_id, "answers": [answer_info], "is_impossible": paragraph_answer_is_impossible}
                qas_info_all.append(qas_info)
        return qas_info_all

def ngramm_similarity(answer, context):

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    n = len(answer.split())
    sixgrams = ngrams(context.split(), n)
    list_of_ngramms = []
    list_of_scores = []

    for grams in sixgrams:
        score = similar(answer, ' '.join(grams))
        list_of_scores.append(score)
        list_of_ngramms.append(' '.join(grams))

    context_answer = list_of_ngramms[list_of_scores.index(max(list_of_scores))]
    start_token = context.find(context_answer)

    output = {'answer': context_answer,'start_token': start_token}
    return output

def answer_parser(paragraph_qas, article_paragraph_context_nl, dest_lng):
        paragraph_answer_text = paragraph_qas['answers'][0]['text']
        paragraph_answer_text_nl = str(mtranslate.translate(to_translate=paragraph_answer_text, to_language=dest_lng, from_language="auto"))
        paragraph_answer_start_nl = (str(article_paragraph_context_nl)).find(str(paragraph_answer_text_nl))
        if int(paragraph_answer_start_nl) == -1:
                ngramm_answer_info = ngramm_similarity(paragraph_answer_text_nl, article_paragraph_context_nl)
                paragraph_answer_text_nl = ngramm_answer_info['answer']
                paragraph_answer_start_nl = ngramm_answer_info['start_token']
        else:
                pass
        answers_info = {"text": str(paragraph_answer_text_nl), "answer_start": int(paragraph_answer_start_nl)}
        return answers_info

if __name__ == "__main__":
        translate_squad(squad_en, "pl")



