from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# Database connection
password = '12345'
db_url = f'mongodb://syaoqibihillah:{password}@dbsparta-shard-00-00.ykgta.mongodb.net:27017,dbsparta-shard-00-01.ykgta.mongodb.net:27017/?ssl=true&replicaSet=atlas-vhrewc-shard-0&authSource=admin&retryWrites=true&w=majority&appName=dbsparta'
client = MongoClient(db_url)
db = client.dbsparta_plus_week2

# Ensure 'examples' collection exists
if 'examples' not in db.list_collection_names():
    db.create_collection('examples')
    print("Collection 'examples' created successfully.")

# Home route to display words and any messages
@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = [
        {
            'word': word['word'],
            'definition': word['definitions'][0]['shortdef'][0] if isinstance(word['definitions'][0]['shortdef'], list) else word['definitions'][0]['shortdef']
        } for word in words_result
    ]
    msg = request.args.get('msg')
    return render_template('index.html', words=words, msg=msg)

# Error page for words not found
@app.route('/error')
def error():
    word = request.args.get('word')
    suggestions = request.args.getlist('suggestions')
    return render_template('error.html', word=word, suggestions=suggestions)

# Detail page for a specific word
@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = "0ca15627-792b-4726-897a-583fe85aacfc"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    # Handle cases where the word is not found
    if not definitions:
        return redirect(url_for('error', word=keyword))

    # If API returns suggestions instead of definitions
    if isinstance(definitions[0], str):
        return redirect(url_for('error', word=keyword, suggestions=definitions))

    status = request.args.get('status_give', 'new')
    return render_template('detail.html', word=keyword, definitions=definitions, status=status)

# Save a new word to the database
@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    # Create the document
    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d')
    }

    # Insert the document into the words collection
    db.words.insert_one(doc)

    return jsonify({'result': 'success', 'msg': f'The word "{word}" was saved!'})

# Delete a word from the database
@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({'result': 'success', 'msg': f'The word "{word}" was deleted.'})

# Fetch examples for a specific word
@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word': word})
    examples = [
        {
            'example': example.get('example'),
            'id': str(example.get('_id'))
        } for example in example_data
    ]
    return jsonify({'result': 'success', 'examples': examples})

# Save an example sentence for a specific word
@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    json_data = request.get_json()
    word = json_data.get('word_give')
    example_text = json_data.get('example_give')

    # Ensure 'examples' collection exists before inserting
    if 'examples' not in db.list_collection_names():
        db.create_collection('examples')

    # Create the document
    doc = {
        'word': word,
        'example': example_text,
        'date_added': datetime.now().strftime('%Y%m%d')
    }

    # Insert the document into the examples collection
    db.examples.insert_one(doc)

    return jsonify({'result': 'success', 'msg': f'Example for "{word}" saved successfully!'})

# Delete an example sentence from the database
@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    example_id = request.form.get('example_id')
    db.examples.delete_one({'_id': ObjectId(example_id)})
    return jsonify({'result': 'success', 'msg': 'Example deleted successfully.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
