from sanic import Sanic, text
from sanic.response import json as json_response
from sanic.exceptions import NotFound
from sanic_motor import BaseModel
from bson import ObjectId

app = Sanic(__name__)

settings = dict(
    MOTOR_URI='mongodb://localhost:27017/myapp', LOGO=None
)

app.config.update(settings)

BaseModel.init_app(app)

class Movie(BaseModel):
    __coll__ = "movies"

@app.route("/add_movie", methods=["POST"])
async def add_movie(request):
    movie = request.json
    movie["_id"] = str(ObjectId())

    new_movie = await Movie.insert_one(movie)
    created_movie = await Movie.find_one({"_id": new_movie.inserted_id}, as_raw=True)
    return json_response(created_movie)


@app.route("/movies", methods=["GET"])
async def list_movies(request):
    movies = await Movie.find(as_raw=True)
    return json_response(movies.objects)



@app.route("/movies/<id>", methods=["GET"])
async def get_movie(request, id):
    if (movies := await Movie.find_one({"_id": id}, as_raw=True)) is not None:
        return json_response(movies)

    raise NotFound(f"Movie {id} not found")


@app.route("/movies/<id>", methods=["DELETE"])
async def delete_movie(request, id):
    delete_result = await Movie.delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return json_response({}, status=204)

    raise NotFound(f"Movie {id} not found")

@app.route("/movies", methods=["DELETE"]) 
async def delete_all_movies(request):
    await Movie.delete_many({})
    return json_response({}, status=204)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)