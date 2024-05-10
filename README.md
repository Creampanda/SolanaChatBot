# Сервис API

### Настройка

1. Переменные окружения

Перед запуском приложения убедитесь, что вы установили необходимые переменные окружения. Скопируйте содержимое файла `sample.env` в новый файл с названием `.env` и установите значения в соответствии с вашими настройками:

```bash
POSTGRES_USER="admin"
POSTGRES_PASSWORD="admin"
POSTGRES_DB="postgres"
TELEGRAM_TOKEN=""
SOLANA_RPC_URL=""
```

2. Запуск с помощью Docker Compose
Чтобы запустить приложение с использованием Docker Compose, выполните следующую команду в терминале:

```bash
docker-compose up --build
```

Эта команда запустит сервис API вместе с базой данных PostgreSQL и любыми другими необходимыми сервисами.

### Доступ к документации API
После запуска сервисов вы сможете получить доступ к документации API, перейдя по следующему URL в вашем веб-браузере:

http://localhost:8000/docs

Это откроет Swagger UI, где вы сможете исследовать и взаимодействовать с конечными точками API.

### Дополнительная информация
База данных PostgreSQL доступна по умолчанию на порту 5432.

Сервис API доступен по умолчанию на порту 8000.

Сервис Telegram бота настроен на взаимодействие с сервисом API, используя указанный порт API.

# Команды бота:
/get_token_info [адрес]: Получить информацию о токене по его адресу.

/add_token [адрес]: Добавить новый токен в базу данных.

Пожалуйста, замените YOUR_TELEGRAM_BOT_TOKEN на реальный токен вашего бота.