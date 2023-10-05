### Работа через cli.py

- Скопируйте файлы из данной директории в корневой каталог микросервиса.

- Проверьте работу командой:
``` sh
python cli.py cli.hello "hello_stranger()"
```


- Список команд:
``` sh
python cli.py cli.hello "hello_stranger()" # проверить что cli.py работает
python cli.py cli.db "create_role()" # создать роль
python cli.py cli.db "get_role()" # получить роль
python cli.py cli.produce "ping_pong_produce()" # отправить сообщение в топик ping_pong
python cli.py cli.consume "ping_pong_consume()" # подписаться на топик ping_pong
```