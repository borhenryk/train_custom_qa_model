import os
import json
import time
import mtranslate


with open('pl_squad_dev.json', encoding="utf8") as s:
    squad_nl = json.load(s)

def clean_squad(squad_eng, dest_lng):
	version = squad_eng['version']
	data = article_parser(squad_eng, dest_lng)
	translated_squad_set = {'version': version, 'data': data}
	with open('pl_squad_dev_clean.json', 'w', encoding='utf-8') as f:
                json.dump(translated_squad_set, f, ensure_ascii=False, indent=4)
	return translated_squad_set

def article_parser(data, dest_lng):
	article_info_all = []
	for article_id in list(range(0, len(data["data"]))):
		article = data["data"][article_id]
		article_title = article['title']
		paragraph_info = paragraph_parser(article ,dest_lng)
		article_info = {'title': article_title, 'paragraphs': paragraph_info}
		article_info_all.append(article_info)
		print(article_id)
	return article_info_all

def paragraph_parser(article, dest_lng):
	paragraph_info_all = []
	for article_paragraphs_id in range(0, len(article["paragraphs"])):
		article_paragraph = article["paragraphs"][article_paragraphs_id]
		article_paragraph_context = article_paragraph["context"]
		qas_info = qas_parser(article_paragraph, article_paragraph_context, dest_lng)
		paragraph_info = {'qas': qas_info,'context': article_paragraph_context}
		paragraph_info_all.append(paragraph_info)
	return paragraph_info_all

def qas_parser(article_paragraph, article_paragraph_context_nl, dest_lng):
	qas_info_all = []
	for paragraph_qas_id in range(0, len(article_paragraph['qas'])):
		paragraph_qas = article_paragraph['qas'][paragraph_qas_id]
		try:
			paragraph_question = paragraph_qas['question']
			paragraph_question_id = paragraph_qas['id']
			paragraph_answer_is_impossible = paragraph_qas['is_impossible']
			if paragraph_qas['is_impossible'] != True:
				if paragraph_qas['answers'][0]['answer_start'] != -1:
					answer_info = answer_parser(paragraph_qas, article_paragraph_context_nl, dest_lng)
				else:
					continue
			else:
				answer_info = []
			qas_info = {"question": paragraph_question, "id": paragraph_question_id, "answers": [answer_info], "is_impossible": paragraph_answer_is_impossible}
			qas_info_all.append(qas_info)
		except:
			continue
	return qas_info_all


def answer_parser(paragraph_qas, article_paragraph_context_nl, dest_lng):
	paragraph_answer_text = paragraph_qas['answers'][0]['text']
	paragraph_answer_start_nl = paragraph_qas['answers'][0]['answer_start']
	answers_info = {"text": str(paragraph_answer_text), "answer_start": int(paragraph_answer_start_nl)}
	return answers_info


result = clean_squad(squad_nl, 'nl')
