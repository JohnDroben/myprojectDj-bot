# Проект интеграции Django API и Telegram-бота
## Ниже представлен полный проект, включающий Django API для получения информации о пользователе и Telegram-бота с командой /myinfo.

```bash
Структура проекта:
text
myprojectDj-bot/
├── myprojectDj/
│   ├── users/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── myprojectDj/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
├── bot/
│   └── bot_main.py
├── requirements.txt
└── README.md
```
```bash
1. Django API (django_api/)
models.py:

python
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.username
serializers.py:

python
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'telegram_id', 'phone']
views.py:

python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer

class UserInfoView(APIView):
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({"error": "Telegram ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
urls.py (api/):

python
from django.urls import path
from .views import UserInfoView

urlpatterns = [
    path('user-info/', UserInfoView.as_view(), name='user-info'),
]
urls.py (django_api/):

python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
settings.py (CORS настройки):

python
INSTALLED_APPS = [
    ...
    'corsheaders',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
]

 Разрешить запросы с любых доменов (для теста)
 CORS_ALLOW_ALL_ORIGINS = True

 Для продакшена используйте:
 CORS_ALLOWED_ORIGINS = [
     "https://your-domain.com",
 ]
 ```
### 2. Telegram бот (telegram_bot/bot.py)
```bash
python
import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

 Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
API_URL = "http://localhost:8000/api/user-info/"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Используй /myinfo чтобы получить свои данные')

def myinfo(update: Update, context: CallbackContext) -> None:
    telegram_id = str(update.effective_user.id)
    
    try:
        response = requests.get(API_URL, params={'telegram_id': telegram_id})
        
        if response.status_code == 200:
            user_data = response.json()
            message = (
                f"👤 Пользователь: {user_data['username']}\n"
                f"📝 Имя: {user_data['first_name'] or 'Не указано'}\n"
                f"📝 Фамилия: {user_data['last_name'] or 'Не указано'}\n"
                f"📧 Email: {user_data['email'] or 'Не указан'}\n"
                f"📱 Телефон: {user_data['phone'] or 'Не указан'}\n"
                f"🆔 Telegram ID: {user_data['telegram_id']}"
            )
        elif response.status_code == 404:
            message = "❌ Пользователь не зарегистрирован"
        else:
            message = "⚠️ Ошибка сервера. Попробуйте позже"
    
    except requests.exceptions.RequestException:
        message = "🚫 Ошибка подключения к API"

    update.message.reply_text(message)

def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("myinfo", myinfo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
3. requirements.txt
text
django==4.2
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-telegram-bot==20.3
requests==2.31.0
4. Инструкция по запуску (README.md)
markdown
## Интеграция Django и Telegram-бота
## Настройка и запуск проекта
### 1. Django API
```bash
cd django_api
pip install -r ../requirements.txt
```
### 2. Применить миграции
python manage.py migrate

### 3. Создать суперпользователя
python manage.py createsuperuser

### 4. Запустить сервер
python manage.py runserver

### Настройка пользователей
Перейдите в админ-панель: http://localhost:8000/admin

Добавьте пользователей через раздел Custom Users

Для тестового пользователя укажите:

Telegram ID (должен совпадать с ID вашего Telegram-аккаунта)

Другие поля (имя, email и т.д.)

### Telegram бот
Создайте бота через @BotFather

В файле telegram_bot/bot.py замените YOUR_BOT_TOKEN на полученный токен

Запустите бота:

bash
cd telegram_bot
python bot.py
4. Тестирование
В Telegram найдите своего бота

Отправьте команды:

/start - приветствие

/myinfo - получение ваших данных из Django API

Важные замечания
Для продакшн-среды:

Замените CORS_ALLOW_ALL_ORIGINS = True на белый список доменов

Используйте переменные окружения для секретных данных

Настройте HTTPS

Убедитесь что Django сервер доступен для бота (при развертывании измените API_URL)

text

### Тестирование функционала:
```bash
1. Зарегистрируйте пользователя в Django с вашим Telegram ID
2. Отправьте боту команду `/myinfo`
3. Бот должен вернуть информацию о пользователе в формате:
👤 Пользователь: username
📝 Имя: Иван
📝 Фамилия: Иванов
📧 Email: user@example.com
📱 Телефон: +79991234567
🆔 Telegram ID: 123456789
```
4. Если пользователь не найден, бот вернет:
❌ Пользователь не зарегистрирован


Для использования:
1. Распакуйте архив
2. Следуйте инструкциям в README.md
3. Для теста CORS можно использовать запросы с другого домена:

```javascript
// Пример запроса из браузера на другом домене
fetch('http://localhost:8000/api/user-info/?telegram_id=123')
.then(response => response.json())
.then(data => console.log(data));