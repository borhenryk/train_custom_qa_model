from nltk import ngrams
from difflib import SequenceMatcher



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

    output = {'answer': context_answer,'context': start_token}
    return output


if if __name__ == "__main__":

    sentence = 'Warszawa (polski: Warszawa [varˈʂava] (słuchaj); patrz także inne nazwy) jest stolicą i największym miastem Polski. Stoi nad Wisłą w ​​środkowo-wschodniej Polsce, około 260 km od Morza Bałtyckiego i 300 km od Karpat. Jego populacja szacowana jest na 1.740 milionów mieszkańców na większym obszarze metropolitalnym (2.666 milionów mieszkańców), co sprawia, że ​​Warszawa jest 9. najludniejszą stolicą w Unii Europejskiej. Granice miasta obejmują 516,9 kilometrów kwadratowych (199,6 mil kwadratowych), podczas gdy obszar metropolitalny obejmuje 6100,43 kilometrów kwadratowych (2 355,39 mil kwadratowych).'
    answer = 'około 260 kilometrów'

    ngramm_similarity(answer, sentence)

