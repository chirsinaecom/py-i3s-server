install packages

```
pip install -r requirements.txt
```

start program

```
python app/main.py
```

debugger

```
uvicorn app.main:app --host localhost --port 8000 --reload
```

export requirements

```
pip freeze > requirements.txt
```

test

```
py app\test.py
```
