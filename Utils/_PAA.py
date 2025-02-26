import people_also_ask
import requests
from typing import List, Dict, Any, Optional, Generator

def generate_answer(key: str, proxy: str = "") -> Generator[dict, None, None]:
	return people_also_ask.generate_answer(key, proxy=proxy)

def generate_related_questions(key: str, proxy: str = "") -> Generator[dict, None, None]:
	return people_also_ask.generate_related_questions(key, proxy=proxy)

def get_answer(key: str, proxy: str = "") -> Dict[str, Any]:
	return people_also_ask.get_answer(key, proxy=proxy)

def get_related_questions(key: str, numRQs: Optional[int] = None, proxy: str = "") -> (List[str] | list):
	return people_also_ask.get_related_questions(key, numRQs, proxy=proxy)

def get_simple_answer(key: str, proxy: str = "") -> str:
	return people_also_ask.get_simple_answer(key, True, proxy=proxy)
 
if __name__ == "__main__":
	print(generate_answer('How does the sun momve?'))

	print(f"generate_related_questions: {generate_related_questions('What do chickens eat?')}")
	print(f"get_answer: {get_answer('What do chickens eat?')}")
	print(f"get_related_questions: {get_related_questions('What do chickens eat?')}")
	print(f"get_simple_answer: {get_simple_answer('What do chickens eat?')}")