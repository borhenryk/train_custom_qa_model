# Translate SQuAD and train a language specific QA Model

This repository includes the script for translation the SQuADv2 to a chosen language:
* The structure of SQuAD is kept as it was
* Translated answers are matched through a similarity matcher on ngram basis
* Text is translated with the ´mtransalte´ package

## Example

* Run `python prepare_squad.py --dest_lng pl --train_or_dev dev` for translating the dev set to polish
* Run `python prepare_squad.py --dest_lng pl --train_or_dev train` for translating the train set to polish


As a result a new dir with the name of the translated SQuAD will be created

## Train QA Model with transformers

The output files can than be used for training a QA model:
* Use the existing multilingual bert as lm or any other language specific model
* Run the following script from huggigface tranformers

```python
export SQUAD_DIR=path/to/translated_squad

python run_squad.py
  --model_type bert \
  --model_name_or_path bert-base-multilingual-cased \
  --do_train \
  --do_eval \
  --version_2_with_negative \
  --train_file $SQUAD_DIR/translated_squad_train.json \
  --predict_file $SQUAD_DIR/translated_squad_dev.json \
  --num_train_epochs 2 \
  --max_seq_length 384 \
  --doc_stride 128 \
  --save_steps=8000 \
  --output_dir ../../output \
  --overwrite_cache \
  --overwrite_output_dir
```
Now the model can be shared on the [Huggigface Model Platform](https://huggingface.co/models)

The model can than be used for QA tasks with the following code:

```python
from transformers import pipeline

qa_pipeline = pipeline(
    "question-answering",
    model="henryk/bert-base-multilingual-cased-finetuned-polish-squad2",
    tokenizer="henryk/bert-base-multilingual-cased-finetuned-polish-squad2"
)

qa_pipeline({
    'context': "Warszawa jest największym miastem w Polsce pod względem liczby ludności i powierzchni",
    'question': "Jakie jest największe miasto w Polsce?"})

```

**Output:**

```json
{
  "score": 0.9986,
  "start": 0, 
  "end": 8,
  "answer": "Warszawa"
}
```

## Model benchmark (date: 26.05.2020)

| Model                | EM/F1 |HasAns (EM/F1) | NoAns |
| ---------------------- | ----- | ----- | ----- |
| [SlavicBERT](https://huggingface.co/DeepPavlov/bert-base-bg-cs-pl-ru-cased)   | 52.90/59.61  | **37.04**/**50.48** | 68.71 |
| [polBERT](https://huggingface.co/dkleczek/bert-base-polish-uncased-v1)   | 50.63/57.24| 35.98/49.21  | 65.24 |
| [multiBERT](https://huggingface.co/bert-base-multilingual-cased) | **55.67**/**61.94**  | 35.76/48.31 | **75.52** |

