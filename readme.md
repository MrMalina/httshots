﻿# Twitch бот для игры Heroes of Storm.

Функционал:
* Выводит информацию о лобби во время загрузки матча (батлтеги, уровни аккаунтов, кто с кем в группе)
* Выводит выбранные таланты прямо во время матча (при  доступе к загрузке изображений по FTP)
* Послематчевая статистика с дополнительными параметрами
* Послематчевый список талантов
* Порядок драфта (для рейтинговых матчей)
* Результаты сыгранных матчей за день

Сохранённые изображения публикуются на Imgur или на FTP. \
**_Внимание:_** При использовании Imgur актуальные таланты не будут публиковаться! \
**_Внимание:_** Для работы бота понадобится второй twitch-аккаунт, который будет работать в качестве бота!

Для запуска необходимо:
1. Установить [Python3](https://www.python.org/downloads/)

2. Установить зависимости (вводить в командную строку)
```bash
py -m pip install configobj imgurpython Pillow mpyq
py -m pip install -U twitchio[starlette] --pre
py -m pip install -U git+https://github.com/Rapptz/asqlite.git
```

**_Уточнение:_** Если при вводе последней команды выводит ошибку: **ERROR: Cannot find command 'git' - do you have 'git' installed and in your PATH?**, то требуется установить [git](https://git-scm.com/downloads) \
**_Уточнение:_** Если появляется ошибка о недоступности github.com, то блокировать доступ к сайту может Zapret для обход DPI

3. Установить heroprotocol

Установите мой форк под актуальную версию python, либо поставьте официальную библиотеку под старую версию python (см. примечание ниже):
```bash
py -m pip install -U git+https://github.com/MrMalina/heroprotocol
```

**_Уточнение:_** Установить heroprotocol можно из [официального репозитория Blizzard](https://github.com/Blizzard/heroprotocol), но в этом случае, потребуется устанавливать устаревшую (начиная с python 3.12) библиотеку `imp.py`. Получить устаревшую библиотеку можно где-то в интернете, либо скачав `python < 3.12` и скопировав оттуда файл `python\Lib\imp.py` в такую же директорию актуального питона.

4. Скачать актуальный [релиз бота](https://github.com/MrMalina/httshots/releases)

5. Разархивировать архив с ботом в директорию, где установлен python
**_Уточнение:_** Если python установлен в директорию по умолчанию, то он располагается в `c:\Users\Пользователь\AppData\Local\Programs\Python\`
Переименовать разархивированную директорию в `httshots`

6. Заполнить конфигурационный файл
Перейти в директорию `config` сделать копию файла `example.ini` и переименовать копию в `config.ini`

**_Уточнение:_** Конфигурационный файл находится в `./httshots/config/config.ini` \
**_Уточнение:_** Более подробная настройка параметров twitch_client_id, twitch_client_secret, twitch_bot_id и twitch_owner_id описана в секции **Подключение к Twitch** \
**_Уточнение:_** Вероятно, понадобится выдать права модератора аккаунту-боту, так как при частом использовании команд, твич отстранит его за спам в чат

7. Запустить бота
Если директорию с файлами бота располагается в той же директории, где python, то запуск осуществляется командой:
```bash
py -m httshots
```

Для запуска бота с параметрами:
```bash
py -m httshots ПАРАМЕТРЫ
```

Список параметров:
* IGNORE_PREV_MATCHES - при запуске бота НЕ учитывать ранее сыгранные сегодня матчи.Приоритет выше, чем параметр add_previous_games в конфигурационном файле
* STARTING_FROM_HOUR <hour> - не учитывать сыгранные матчи до указанного часа. То есть, указав STARTING_FROM_HOUR 18, все матчи до 18 часов не учитываются при запуске бота
* SEND_BATTLE_LOBBY - при запуске бота выводить информацию о лобби, если её можно получить. Приоритет выше, чем параметр send_previous_battle_lobby в конфигурационном файле
* URL_TO_CONSOLE - дублировать все ссылки в консоль. Приоритет выше, чем параметр duplicate_url_in_console в конфигурационном файле
* GET_TWITCH_ID <account_name> - Получить идентификатора указанного аккаунта. После получения идентификатора бот будет выключен

Например, чтобы запустить бота с игнорированием предыдущих матчей и дублированием ссылок в консоль:
```bash
py -m httshots IGNORE_PREV_MATCHES URL_TO_CONSOLE
```
Или, например, для игнорирования матчей, сыгранных до 18 часов, и дублирования ссылок в консоль, команда будет выглядеть так:
```bash
py -m httshots STARTING_FROM_HOUR 18 URL_TO_CONSOLE
```

# Подключение к Twitch
Для применения бота требуется выполнить следующие шаги:
1. Создание приложения Twitch. Приложение необходимо для работы с API Twitch
- Перейдите по ссылке [Twitch Developer Console](https://dev.twitch.tv/console)
- Залогиньтесь с основного аккаунта
- Создайте приложение (не расширение!) - кнопка подать заявку:
    * Заполните название (далее оно нигде не будет фигурировать)
    * Добавьте `http://localhost:4343/oauth/callback` в OAuth Redirect URL и нажмите Добавить. Новую пустую строку удалите.
    * Категория - `Chat Bot`
    * Тип клиента - `Конфиденциально`
- Перейдите в управление созданным приложением
- Скопируйте Идентификатор клиента в переменную twitch_client_id конфига
- Скопируйте Секретный код клиента в переменную twitch_client_secret конфига
2. Получение идентификаторов аккаунта владельца и аккаунта бота
- Зайдите в консоль и введите `py -m httshots GET_TWITCH_ID ИМЯ_АККАУНТА`, вместо ИМЯ_АККАУНТА введите то имя аккаунта, для которого хотите получить ID
- Например, введя `py -m httshots GET_TWITCH_ID malinatest`, в ответ будет выведена строка `User: malinatest - ID: 660661446`. **Если ничего не выводится, значит такого аккаунта не существует!**
- Скопируйте ID аккаунта-владельца в переменную twitch_owner_id конфига
- Скопируйте ID аккаунта-бота в переменную twitch_bot_id конфига
3. Авторизация аккаунта-бота и приложения аккаунта-владельца
- Запустите бота `py -m httshots`
    * Вариант 1. Разлогиньтесь на твиче и залогиньтесь на аккаунте-боте
    * Вариант 2. Откройте браузер в режиме инкогнито и залогиньтеся там на аккаунте-боте
- Перейдите по ссылке для стандартных прав [http://localhost:4343/oauth?scopes=user:bot+user:read:chat+user:write:chat](http://localhost:4343/oauth?scopes=user:bot+user:read:chat+user:write:chat)
- Авторизуйтесь. Если всё прошло успешно, то в браузере будет выведено `Success. You can leave this page.`
4. Связь канала аккаунта-владельца и приложения аккаунта-владельца
- Залогиньтесь на аккаунт-владельца
- Перейдите по ссылке [http://localhost:4343/oauth?scopes=channel:bot](http://localhost:4343/oauth?scopes=channel:bot)
- Авторизуйтесь. Если всё прошло успешно, то в браузере будет выведено `Success. You can leave this page.`
5. Завершение настройки
- Отключение бота, нажав CTRL+C в консоли, или закрыв консоль
- Настройка подключения к twitch завершена. Не забудьте настроить конфигурационный файл до конца

# Подключение FTP
Для отображения талантов прямо из матча, создайте в директории `config::ftp_site_name/config::ftp_folder/` директорию `curname`.
Итого должно получиться, например: `/httshots.ru/mln/curgame.`
Перенесите в эту директорию файл `index.html` из директории `httshots/files/`
Файл `index.html` сгенерирован через генеративную сеть искусственного интеллекта.

# Список команд в twitch-чате
Ниже представлен список команд, которые доступны в чате трансляции, где активен бот.

- `!game <[cmd]> <[param]>` или `!матч <[команда]> <[параметр]>` - команда позволяет вывести информацию о прошлом сыгранном матче.
- `!game` или `!матч` без параметров - результат последнего сыгранного матча
- `!game score` или `!матч счёт` - уровни команд и количество убийств
- `!game bans` или `!матч баны` - список забаненных персонажей. Имена персонажей указываются так, как применимы в реплее игры
- `!game draft` или `!матч драфт` - порядок драфта в рейтинговом матче
- `!game heroes` или `!матч герои` - список персонажей в матче
- `!game meat` или `!матч мясо` - сколько мяса не поднял Мясник
- `!game <hero>` - таланты, которые были взяты у персонажа
- `!game <hero> score` или `!матч <персонаж> счёт` - итоговый KDA
- `!game <hero> <параметр>` - значение указанного параметра, если он будет обнаружен. Список параметров можно посмотреть, например, [тут](https://raw.githubusercontent.com/MrMalina/hots-replays-params/refs/heads/master/replay.ini)
- `!games` или `!матчи` - результаты сыгранных матчей
- `!talents <hero>` или `!таланты <персонаж>` - таланты персонажа в текущем матче. Таланты начинают публиковаться примерно через минуту после начала матча

# Известные проблемы
Нет гарантии, что будет корректно выводиться информация по своей игре. А именно:
1. Информация о лобби может обманывать по списку команд
2. Информация о матче, талантах и прочее может выводить информацию не в правильном порядке героев

# Обновление до актуальной версии
Сейчас процесс обновления бота не очень удобен, возможно, дальше он упростится
1. Скачать архив с актуальной версией
2. Перенести все директории, кроме config
3. Сравнить текущий конфигурационный файл и новый (в архиве)
4. Если конфигурационный файл отличается, то привести к новому виду 

# Обновление HoTS
При обновлении игры бот не сможет читать реплеи. Проверьте, есть ли актуальная версия heroprotocol. Если есть, обновите её. Если нет, напишите мне в DS.
Если при обновлении игры были добавлены новые таланты, потребуется обновление json файла с информацией о героях. Можно обновить самостоятельно через утилиту HeroesDataParser, либо написать мне в DS и подождать обновления бота.

# Благодарности
* С помощью приложения [CascView](http://www.zezula.net/en/casc/main.html) извлечены файлы из хотса
* Библиотека для работы с twitch - [twitchio 3.0](https://twitchio.dev/)
* Файл с информацией о героях (herodata.json) получен с помощью [HeroesDataParser](https://github.com/HeroesToolChest/HeroesDataParser)

# Лицензия
Авторские права 2025 MrMalina

Исходный код этого проекта опубликован в соответствии с лицензией MIT. Для получения дополнительной информации см. прилагаемый файл [LICENSE](https://github.com/MrMalina/httshots/blob/master/LICENSE).