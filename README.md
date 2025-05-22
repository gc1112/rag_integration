setup
1. start ollama container
2. inspect ip of ollama container
```
docker inspect bridge
```
3. edit gradio_UI.py, sepcify IP and model name of ollama container to connect, rag.py will follow
4. create container with gradio_UI.py and rag.py, 
```
docker build -t ui .
```
5. run container
```
docker run -itd -p 7860:7860 --name ui_container ui
```
6. visit site at http://127.0.0.1:7860/
