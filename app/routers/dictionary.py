from fastapi import APIRouter
from ..dictionary.main import DictionaryService


router = APIRouter(
    prefix="/dictionary",
    tags=['Dictionary']
)

dictionary = DictionaryService()

@router.get('/')
async def get_term_definition(q: str):
  res = dictionary.get_term_definition(q)
  return res

@router.get('/term/')
async def get_similar_terms(q: str):
  res = dictionary.get_terms(q)
  return res

@router.get('/random')
async def get_random_word():
  res = dictionary.get_random_word()
  return res