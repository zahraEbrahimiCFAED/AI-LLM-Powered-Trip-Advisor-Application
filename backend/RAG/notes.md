docker build -t ai-grid .
docker run --rm -it -p "5000:5000" --name ai-grid ai-grid