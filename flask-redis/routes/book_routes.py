from flask import Blueprint, request, jsonify
from redisClient import get_redis_client
import json

book = Blueprint('book', __name__)
redis_client = get_redis_client()

@book.route('/', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    book_id = redis_client.incr('book_id')  # Auto-increment ID for new book
    redis_client.hset(f'book:{book_id}', mapping={"title": title, "author": author})

    return jsonify({"message": "Book added successfully", "book_id": book_id}), 201


@book.route('/', methods=['GET'])
def get_books():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start = (page - 1) * limit
    end = start + limit - 1

    # Define your cache key here
    cache_key = f'books_cache:page_{page}'

    # Check if the result is already in cache
    cached_books = redis_client.get(cache_key)
    if cached_books:
        return jsonify(json.loads(cached_books)), 200

    # If not cached, fetch from Redis
    keys = redis_client.keys('book:*')
    books = [
        {k.decode('utf-8'): v.decode('utf-8') for k, v in redis_client.hgetall(key).items()}
        for key in keys
    ]
    redis_client.setex(cache_key, 300, json.dumps(books))

    return jsonify({"books": books}), 200


@book.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    # Create a cache key based on the book ID
    cache_key = f'book:{book_id}'

    # Check if the key exists in the cache
    cached_book = redis_client.hgetall(cache_key)  # Use hgetall for hash

    if cached_book:
        # Decode the keys and values from bytes to strings
        decoded_book = {key.decode('utf-8'): value.decode('utf-8') for key, value in cached_book.items()}
        return jsonify(decoded_book), 200
    else:
        return jsonify({"message": "Book not found"}), 404


@book.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')

    if not redis_client.exists(f'book:{book_id}'):
        return jsonify({"error": "Book not found"}), 404

    if title:
        redis_client.hset(f'book:{book_id}', "title", title)
    if author:
        redis_client.hset(f'book:{book_id}', "author", author)

    # Retrieve the updated book data
    updated_book = {
        "title": redis_client.hget(f'book:{book_id}', "title").decode('utf-8'),
        "author": redis_client.hget(f'book:{book_id}', "author").decode('utf-8')
    }

    # Update the cache with the latest data
    redis_client.hmset(f'book:{book_id}', updated_book)

    return jsonify({"message": "Book updated successfully", "book": updated_book}), 200



@book.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    # Check if the book exists
    if not redis_client.exists(f'book:{book_id}'):
        return jsonify({"message": "Book not found"}), 404

    # Delete the book
    redis_client.delete(f'book:{book_id}')

    # Invalidate related caches
    redis_client.delete(f'books_cache:page_*')  # Adjust this if you cache other items

    return jsonify({"message": "Book deleted successfully"}), 200

@book.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('query', '')

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    cache_key = f'search:books:{query}'
    cached_results = redis_client.get(cache_key)

    if cached_results:
        return jsonify(json.loads(cached_results)), 200

    all_books = redis_client.keys(f'book:*')
    search_results = []

    for book_key in all_books:
        book_data = redis_client.hgetall(book_key)
        title = book_data[b'title'].decode('utf-8')
        author = book_data[b'author'].decode('utf-8')
        if query.lower() in title.lower():
            search_results.append({"title": title, "author": author})

    # Store search results in cache
    redis_client.setex(cache_key, 300, json.dumps(search_results))  # Cache for 5 minutes

    return jsonify({"results": search_results}), 200

