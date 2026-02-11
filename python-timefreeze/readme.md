## Command to run mongo container
docker run -v jwtMongoData:/data/db -p 27017:27017 -d --name jwtMongo mongo

## Command to build app container
sudo docker run --name pyjwtApp -p5000:5000 --rm --net keploy-network py-jwt

## Native command to run application
python3 app.py