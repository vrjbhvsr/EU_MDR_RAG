from src.retrieval import Hybrid_Retriever
import json
chunks = json.load(open('data/processed/chunks/chunks_from_script.json'))
hr = Hybrid_Retriever(chunks)
print(hr.retrieve("What is the definition of a medical device under MDR?"))