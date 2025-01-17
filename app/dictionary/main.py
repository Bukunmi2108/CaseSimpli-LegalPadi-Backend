import json
from fastapi import HTTPException
from ..schemas import TermDefinition
from random import choice

# Load terms and definitions from JSON file
def load_dictionary(filename):
  """Loads the Black's Law Dictionary from a JSON file."""
  with open(filename, 'r') as f:
    return json.load(f)

dict = load_dictionary('data.json')

law_dict = {}

for id in dict['term']:
  law_dict[dict['term'][id]] = dict['definition'][id]




class DictionaryService:
  def get_term_definition(self, q: str):
    """Returns the definition of a given legal term."""
    q = q.upper()
    if law_dict[q]:
      return law_dict[q]
    else:
      raise HTTPException(status_code=404, detail='Definition Not Found')
  
  def get_terms(self, q: str):
    """Finds terms in the dictionary that contain the search string."""
    q = q.upper()
    results = []
    count = 0

    for k in law_dict.keys():
      if q in k:
        results.append(k)
        count += 1

        if count >= 10:
            break 
    return results
  
  def get_random_word(self):
    q = choice(list(law_dict.keys()))
    return {
      'term': q,
      'definition': law_dict[q]
    }