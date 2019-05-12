# datascience_api
Flask API + nginx + docker
Step
1. Build DockerFile first.
cd in local DockerFile and run this command
docker build -t myapi .
2. Customize this command and run it.
docker run -d --name myapi -p 7006:80 -v $(pwd)/app:/app -e FLASK_APP=main.py -e FLASK_DEBUG=1 myapi flask run --host=0.0.0.0 --port=80