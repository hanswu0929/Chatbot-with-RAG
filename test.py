from numpy import dot
from numpy.linalg import norm
from rag_retrieve import ollama_embed_text

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

vec1 = ollama_embed_text(["beef noodles is the most famous food in taiwan."])[0]
vec2 = ollama_embed_text(["What is the most famous food in taiwan?"])[0]
print("cosine similarity:", cosine_similarity(vec1, vec2))
