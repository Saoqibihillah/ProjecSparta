import requests

api_key = '0ca15627-792b-4726-897a-583fe85aacfc'
word = 'potato'
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

res = requests.get(url)

definitions = res.json() 

print(definitions)

for definitions in definitions :
    print(definitions)