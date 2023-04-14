import numpy as np
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
def ru_rank(texts : dict, query : str) -> dict:
    link_and_idx = dict()
    i = 0
    for l in texts.keys():
        link_and_idx[i] = l
        i+=1
    doc_embeddings = model.encode([i[0:100] for i in list(texts.items())], convert_to_tensor=True)
    queries_embeddings = model.encode(query, convert_to_tensor=True)
    scores = list(util.cos_sim(doc_embeddings, queries_embeddings))
    result = dict()
    for idx in range(0, len(scores)):
        result[link_and_idx[idx]] = scores[idx]
    return result
def bm25(word, sentence, avgdl, N, docs, k=1.2, b=0.75):
    freq = sentence.count(word)  # or f(q,D) - freq of query in Doc
    tf = (freq * (k + 1)) / (freq + k * (1 - b + b * (len(sentence) / avgdl)))
    N_q = sum([doc.count(word) for doc in docs])  # number of docs that contain the word
    idf = np.log(((N - N_q + 0.5) / (N_q + 0.5)) + 1)
    return round(tf*idf, 4)
def bm25_rank(texts:dict, query:str)->dict:
        ranks = dict()
        N = len(list(texts.items()))
        splitted_txts = [str(i).split(" ") for i in list(texts.items())]
        avgdl = sum(len(sentence) for sentence in splitted_txts) / N
        for link in texts.keys():
            splitted_query = query.split(" ")
            for w in splitted_query:
                ranks[link] = float(ranks.get(link) or  0) + bm25(w, texts[link], avgdl, N, list(texts.items()))
        return ranks
