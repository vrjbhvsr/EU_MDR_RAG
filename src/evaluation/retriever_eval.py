from pathlib import Path
import json

def recall_at_k(retrieved_ids, gold_ids, k):
    """This function evalute the retrieval on recall.
    Did the right chunk make it into the top-k at all?
    Gold is 1 chunk only, so is that gold chunk present in top-k?

    Args:
        retrieved_ids (list): list of retrieved chunk ids
        gold_ids (list): list of gold chunk ids
        k (int): top-k to evaluate
    Returns:
        recall (float): 1 if gold chunk is present in top-k, else 0
    """
    ret_ids = set(retrieved_ids[:k])
    gold_id = set(gold_ids)

    if not len(ret_ids & gold_id) == 0: return 1
    else : return 0


########################################################################################################################
"""Across all questions, Recall@5 = fraction that scored 1. "For 82% of questions, the right chunk was somewhere in the top 5." It's presence — in or out. Position doesn't matter. Rank 1 and rank 5 both count as 'found'."""


"""why isn't "it's in the top-5" good enough — why do we need a second metric?
 -> because your LLM reads the chunks in order and weights the early ones. 
 A gold chunk at rank 5 is technically "found" but might get ignored in generation. Recall can't tell rank-1 from rank-5. 
 That's the gap MRR fills."""
########################################################################################################################


def reciprocal_rank(retrieved_ids, gold_ids):
    """How high up was the right chunk?
    Higher = golds land nearer the top.
    MRR heavily rewards getting the answer to position 1. That's deliberate: it cares about "is the best chunk first?"
    Args:
        retrieved_ids (list): list of retrieved chunk ids
        gold_ids (list): list of gold chunk ids
    Returns:
        reciprocal_rank (float): 1/rank if gold chunk is present in retrieved_ids, else 0
    """

    rank = None
    for i, r_id in enumerate(retrieved_ids):
        if r_id in gold_ids:
            rank = i + 1
            break
    if rank is not None:
        return 1/rank

    return 0


def evaluate_retriever(evaluation_set: str, retriever, top_k: int):
    with open(Path(evaluation_set), 'r') as f:
        eval_data = json.load(f)

        hits= 0
        reciprocal_ranks = []

        for x in eval_data:
            question = x['question']
            data = x.get('retrieved_data')
            g_ids = data['ids'][0]
            #print(g_ids)

            result = retriever.retrieve(question)

            r_ids = [c.get("chunk_id") for c in result]

            recall = recall_at_k(retrieved_ids=r_ids, gold_ids= g_ids, k=top_k)
            if recall:
                hits += 1
            reciprocal_ranks.append(reciprocal_rank(retrieved_ids=r_ids, gold_ids=g_ids))

        recall = hits/len(eval_data)
        MRR = sum(reciprocal_ranks)/len(eval_data)

        return recall, MRR