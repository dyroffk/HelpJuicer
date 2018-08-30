#!/usr/bin/env python
import os
import csv
import sys
import logging
import requests
from io import StringIO

logger = logging.getLogger()

# Override CSV field size limit to accomodate 
# large HTML blobs in HelpJuice CSVs
csv.field_size_limit(sys.maxsize)

try:
  HELPJUICE_DOMAIN = os.environ['HELPJUICE_DOMAIN']
except:
  logger.error("HELPJUICE_DOMAIN environment variable must be set")
  exit(1)
HELPJUICE_BASE_URL = f'https://{HELPJUICE_DOMAIN}.helpjuice.com/api/'


def fetch(resource, page_num=1, page_size=1000, outformat='csv'):
  """Fetch HelpJuice `resource` in batches

      outformat: one of 'csv', 'json'

      returns: List of OrderedDicts representing `resource`
  """
  payload = {
    'api_key': os.environ['HELPJUICE_API_KEY'],
    'limit': page_size,
    'page': page_num,
  }
  logger.debug(f'Fetching {resource} page_num={page_num} page_size={page_size}')
  response = requests.get(HELPJUICE_BASE_URL + resource + f'.{outformat}', params=payload)
  if response.status_code not in range(200,300):
    logger.error(f'Error fetching HelpJuice questions: {response.message}')
    return

  if outformat == 'csv': 
    results = list(csv.DictReader(StringIO(response.text)))
  elif outformat == 'json':
    results = response.json()
  else:
    logger.error('Unsupported format requested: "{outformat}"')
    return
  logger.debug(f'Found {len(results)} HelpJuice {resource}')
  return results


def fetch_all(resource, outformat='csv'):
  """Fetch all of `resource` instances from HelpJuice

      `resource` can be one of [categories, questions, answers]
    """
  page_num = 1
  page_size = 1000
  all_results = []
  while True:
    results = fetch(resource, page_num, page_size, outformat)
    all_results.extend(results)
    page_num += 1
    if len(results) < 1000:
      break
  return all_results

def dump_all_resources(filename, categories, questions, answers):

  answer_lookup = {int(a['question_id']): a for a in answers}

  fields = list(questions[0].keys()) + ['answer']
  with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fields)
    writer.writeheader()

    for question in questions:
      #import pdb; pdb.set_trace()
      question['categories'] = [c['id'] for c in question['categories']]
      question['answer'] = answer_lookup[question['id']]['body']
      writer.writerow(question) 

  return


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)

  if 'HELPJUICE_API_KEY' not in os.environ:
    logger.error("HELPJUICE_API_KEY environment variable is required")
    exit(1);

  categories = fetch_all('categories')
  logger.info(f'Found {len(categories)} HelpJuice categories')
  with open('helpjuice_categories.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, categories[0].keys())
    writer.writeheader()
    writer.writerows(categories)

  questions = fetch_all('questions', outformat='json')
  logger.info(f'Found {len(questions)} total HelpJuice questions')

  answers = fetch_all('answers')
  logger.info(f'Found {len(answers)} total HelpJuice answers')

  # Dump all resources into single CSV
  dump_all_resources('helpjuice_questions.csv', categories, questions, answers)
