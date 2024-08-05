# eshop-delivery-bot

### Setup

Clone the repository:
```sh
$ git clone https://github.com/IslombekOrifov/eshop-delivery-bot.git
$ cd qr-code-task
```

Create a virtual environment for bot:
```sh
$ cd bot
$ python -m venv env
$ source env/bin/activate
```

Install the dependencies for bot:
```sh
(env)$ pip install -r requirements.txt
```

Create a virtual environment for admin:
```sh
$ python -m venv env
$ source env/bin/activate
```

Install the dependencies for admin:
```sh
(env)$ pip install -r requirements.txt
```

Upload your logo with name logo.jpg to site/media/logo/

In the root of the project create a .env file and set the environment variables
```sh
# Django Secret Key
SECRET_KEY = 

# Database configs
ADMINS =  # example 8596841,18496223,645441
SUPERUSERS =  # example 8596841,18496223,645441
BOT_TOKEN = # example 6363356505:AAFqSXkt2VJfd
ip = # example 192.168.0000.000 Your server ip 

DB_NAME =
DB_USER =
DB_PASS =
DB_HOST =

CLICK_SERVICE_ID = 
CLICK_MERCHANT_ID = 
CLICK_SECRET_KEY = 
CLICK_MERCHANT_USER_ID = 

Makemigrations:
```sh
(env)$ python manage.py makemigrations
```

Migrate database:
```sh
(env)$ python manage.py migrate
```

Create superuser:
```sh
(env)$ python manage.py createsuperuser
```

Run admin:
```sh
(env)$ python manage.py runserver
```

Run bot:
```sh
(env)$ python app.py
```


