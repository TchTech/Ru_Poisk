# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# # from sentence_transformers import SentenceTransformer, util
# import torch
# from transformers import AutoTokenizer, AutoModel
# tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
# model = AutoModel.from_pretrained("cointegrated/rubert-tiny2")
# # model.cuda()  # uncomment it if you have a GPU

# def embed_bert_cls(text, model, tokenizer):
#     t = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
#     with torch.no_grad():
#         model_output = model(**{k: v.to(model.device) for k, v in t.items()})
#     embeddings = model_output.last_hidden_state[:, 0, :]
#     embeddings = torch.nn.functional.normalize(embeddings)
#     return embeddings[0].cpu().numpy()
# # model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

# def fast_rank(query : str, links : list, depth : int):
#     links = links[:depth]
#     scores_dict = dict()
#     queries_embeddings = embed_bert_cls(query, model, tokenizer)#(, convert_to_tensor=True)
#     for link in links:
#         link_embedding = embed_bert_cls(link, model, tokenizer)
#         score = list(cosine_similarity([link_embedding], [queries_embeddings]))
#         scores_dict[link] = score[0]
#     return dict(sorted(scores_dict.items(), key=lambda item: item[1], reverse=True))