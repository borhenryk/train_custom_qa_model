import os
import json
import time
import mtranslate
from nltk import ngrams
from difflib import SequenceMatcher
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='squad translation')
    parser.add_argument('--dest_lng', type=str,
                        help='destination language for squad')
    parser.add_argument('--train_or_dev', type=str,
                        help='translation of train or dev set')
    args = parser.parse_args()
    return args

def run_translation_squad(args):

    if args.train_or_dev == 'train':
        train_or_dev_set = 'train-v2.0.json'
    else:
        train_or_dev_set = 'dev-v2.0.json'

    path_to_en_squad = 'squad_en/' + train_or_dev_set

    with open(path_to_en_squad) as f:
        squad_en = json.load(f)

    def translate_squad(squad_eng, dest_lng):
        save_dir = 'squad_' + dest_lng
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        version = squad_eng['version']
        data = article_parser(squad_eng, dest_lng)
        translated_squad_set = {'version': version, 'data': data}
        file_to_save = save_dir + '/' + dest_lng + '_squad_' + args.train_or_dev + '.json'

        with open(file_to_save, 'w', encoding='utf-8') as f:
            json.dump(translated_squad_set, f, ensure_ascii=False, indent=4)


    def article_parser(data, dest_lng):
        article_info_all = []
        for article_id in list(range(0, len(data["data"]))):
            article = data["data"][article_id]
            article_title = article['title']
            article_title_translated = str(mtranslate.translate(to_translate=article_title, to_language=dest_lng, from_language="en"))
            paragraph_info = paragraph_parser(article, dest_lng)
            article_info = {'title': article_title_translated, 'paragraphs': paragraph_info}
            article_info_all.append(article_info)
            print('topic ' + article_id + ' finished')
        return article_info_all

    def paragraph_parser(article, dest_lng):
        paragraph_info_all = []
        for article_paragraphs_id in range(0, len(article["paragraphs"])):
            article_paragraph = article["paragraphs"][article_paragraphs_id]
            article_paragraph_context = article_paragraph["context"]
            try:
                article_paragraph_context_translated = str(mtranslate.translate(to_translate=article_paragraph_context, to_language=dest_lng, from_language="en"))
            except:
                continue
            qas_info = qas_parser(article_paragraph, article_paragraph_context_translated, dest_lng)
            paragraph_info = {'qas': qas_info,'context': article_paragraph_context_translated}
            paragraph_info_all.append(paragraph_info)
        return paragraph_info_all


    def qas_parser(article_paragraph, article_paragraph_context_translated, dest_lng):
        qas_info_all = []
        for paragraph_qas_id in range(0, len(article_paragraph['qas'])):
            paragraph_qas = article_paragraph['qas'][paragraph_qas_id]
            paragraph_question = paragraph_qas['question']
            try:
                paragraph_question_translated = str(mtranslate.translate(to_translate=paragraph_question, to_language=dest_lng, from_language="en"))
            except:
                continue
            paragraph_question_id = paragraph_qas['id']
            paragraph_answer_is_impossible = paragraph_qas['is_impossible']
            if paragraph_qas['is_impossible'] == False:
                answer_info = answer_parser(paragraph_qas, article_paragraph_context_translated, dest_lng)
            else:
                answer_info = []
            qas_info = {"question": paragraph_question_translated, "id": paragraph_question_id, "answers": [answer_info], "is_impossible": paragraph_answer_is_impossible}
            qas_info_all.append(qas_info)
        return qas_info_all

    def ngram_similarity(answer, context):

        def similar(a, b):
            return SequenceMatcher(None, a, b).ratio()

        n = len(answer.split())
        sixgrams = ngrams(context.split(), n)
        list_of_ngrams = []
        list_of_scores = []

        for grams in sixgrams:
            score = similar(answer, ' '.join(grams))
            list_of_scores.append(score)
            list_of_ngrams.append(' '.join(grams))

        context_answer = list_of_ngrams[list_of_scores.index(max(list_of_scores))]
        start_token = context.find(context_answer)

        output = {'answer': context_answer,'start_token': start_token}
        return output

    def answer_parser(paragraph_qas, article_paragraph_context_translated, dest_lng):
        paragraph_answer_text = paragraph_qas['answers'][0]['text']
        paragraph_answer_text_translated = str(mtranslate.translate(to_translate=paragraph_answer_text, to_language=dest_lng, from_language="auto"))
        paragraph_answer_start_translated = (str(article_paragraph_context_translated)).find(str(paragraph_answer_text_translated))
        if int(paragraph_answer_start_translated) == -1:
            ngram_answer_info = ngram_similarity(paragraph_answer_text_translated, article_paragraph_context_translated)
            paragraph_answer_text_translated = ngram_answer_info['answer']
            paragraph_answer_start_translated = ngram_answer_info['start_token']
        else:
            pass
        answers_info = {"text": str(paragraph_answer_text_translated), "answer_start": int(paragraph_answer_start_translated)}
        return answers_info


    translate_squad(squad_en, args.dest_lng)



if __name__ == "__main__":

    args = parse_args()
    run_translation_squad(args=args)




