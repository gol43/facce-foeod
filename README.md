# Face-food - Удоный сайт, где вы можете найти всё, что вам нужно из рецептов.

### Возможности сервиса:
Face-food- это хороший помощник по созданию рецептов и последующим просмотром этих самых рецептов.
Вы можете приглашать свои друзей и близких, чтобы лёгким способом обмениваться рецептами.
Также вы можете подписываться на пользователей, рецепты которых вам приметелись.
Вы можете и сами рецепты добавлять в избранные, чтобы не забыть и не потерять нужное вам блюдо.
Нажав на кнопку список покупок, вы получите доступ к рецептам, ингредиенты которых вы можете скачать в обычный файл.
Всем приятного аппетита
Проект доступен по [адресу](https://face-food.ddns.net)

### Установка:
1. Клонируйте проект:
    ```bash
    git clone https://github.com/gol43/foodgram-project-react.git
    ```
    ```bash
    cd foodgram-project-react
    ```
2. Собираем контейнеры и делаем необходимые миграции:
```
sudo docker compose up -d
sudo docker-compose exec backend python manage.py migrate
```
3. Cобериаем статику и юзера для админки создаём:
```
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
4. Супер юзер:
```
email: saigh06@gmail.com
password: 123
```
### Сервис доступен по адресу:
```
http://51.250.99.225/
```
А также:
```
https://face-food.ddns.net
```

## Автор <a id=author></a>

Сайгушев Дамир 
https://github.com/gol43