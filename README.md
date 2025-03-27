# allo-experts-backend

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py migrate
```

Run the server:
```
python manage.py runserver
```

Set env variables:
```
  CLOUND_NAME=
  CLOUD_API_KEY=
  CLOUD_API_SECRET=
```

Run the trends script:
```
python manage.py update_trends --months=27 (--clear-all)
```