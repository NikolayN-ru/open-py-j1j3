поднимаем приложение
docker-compose up -d

делаем запрос на создание пользователя
(GET) http://127.0.0.1:5100/create_user

сервер возвращает access_token and user_identifier:
{
    "access_token": "ed27baaf-cad5-4b48-9911-85022c924559",
    "user_identifier": "93ffbbd4-d3e3-45e1-9ef4-8508c5a52376"
}

делаем запрос на загрузку аудио
(POST) http://127.0.0.1:5100/upload_audio

access_token: ed27baaf-cad5-4b48-9911-85022c924559
user_identifier: 93ffbbd4-d3e3-45e1-9ef4-8508c5a52376
audio: fileName.wav


сервер возвращает ссылку на загруженный путь к файлу
{
    "download_url": "http://localhost:5100/record?id=7f6f4e81-d3f5-42e7-a95f-65c3f98b6f7b&user=1",
    "message": "Audio uploaded successfully."
}

переходим по ссылке и скачиваем файл.
http://127.0.0.1:5100/record?id=cd3ec0e3-1380-4fb5-b0f2-ff3dd4e535fd&user=1



--------------------------------
docker exec -it <container_id> bash
psql -U postgres -d postgres -h localhost -p 5432

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Детализация задачи:

Реализован веб-сервис со следующими REST методами:
Создание пользователя, POST:
Принимает на вход запросы с именем пользователя;
Создаёт в базе данных пользователя заданным именем, так же генерирует уникальный идентификатор пользователя и UUID токен доступа (в виде строки) для данного пользователя;
Возвращает сгенерированные идентификатор пользователя и токен.
Добавление аудиозаписи, POST:
Принимает на вход запросы, содержащие уникальный идентификатор пользователя, токен доступа и аудиозапись в формате wav;
Преобразует аудиозапись в формат mp3, генерирует для неё уникальный UUID идентификатор и сохраняет их в базе данных;
Возвращает URL для скачивания записи вида http://host:port/record?id=id_записи&user=id_пользователя.
Доступ к аудиозаписи, GET:
Предоставляет возможность скачать аудиозапись по ссылке из п 2.2.3.
Для всех сервисов метода должна предусмотрена предусмотрена обработка различных ошибок, возникающих при выполнении запроса, с возвращением соответствующего HTTP статуса.
Модель данных (таблицы, поля) для каждого из заданий можно выбрать по своему усмотрению.
В репозитории предоставлены инструкции по сборке докер-образа с сервисами их настройке и запуску.
Использовались аннотации типов.