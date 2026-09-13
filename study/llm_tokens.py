"""Score label suffixes after a shared tokenizer prefix.

P(prefix, label | prompt) shares P(prefix | prompt) across candidates, so
normalizing full candidate likelihoods equals normalizing suffix logits after
appending the common prefix. Supports SentencePiece's standalone whitespace.
"""
import torch

def label_tokens(tokenizer):
    sequences=[tokenizer.encode(label,add_special_tokens=False) for label in ['0','1']]
    prefix=[]
    while all(len(s)>len(prefix) for s in sequences) and len({s[len(prefix)] for s in sequences})==1:
        prefix.append(sequences[0][len(prefix)])
    suffixes=[s[len(prefix):] for s in sequences]
    if not all(len(s)==1 for s in suffixes):raise ValueError('Expected one label token after shared prefix')
    return prefix,[s[0] for s in suffixes]

def append_prefix(ids,prefix):
    if not prefix:return ids
    return torch.cat([ids,ids.new_tensor([prefix])],dim=1)
