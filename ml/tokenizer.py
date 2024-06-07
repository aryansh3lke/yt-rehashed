from nltk.tokenize import sent_tokenize
import json
import sys

text = sys.argv[1] if len(sys.argv) > 1 else ""
sentences = sent_tokenize(text)
print(json.dumps(sentences))