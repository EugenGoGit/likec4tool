Проект для хранения архитектурных диаграмм

В проекте используется DSL LikeC4 для описания диаграмм.

Используй skill likec4 для чтения документации по DSL LikeC4.

В проекте присутствуют **только** диаграммы и впомогательный код.

При запуске в ОС Windows Лексема "&&" не является допустимым разделителем операторов

## Структура проекта

- `diagrams/*.c4` — файлы диаграмм
- `diagrams/spec.c4` — общий specification (element kinds, styles)
- `.gigacode/skills/likec4/references/` — справочные материалы по LikeC4

## Правила написания диаграмм
- specification вынесен в `diagrams/spec.c4` — не дублируй element kinds в диаграммах
- description и notes связей должны включать параметры сообщения
- description и notes компонентов и связей должно быть оформлено в стиле markdown по примеру:

        description '''
        ### Reads/writes user profiles, subscriptions, watch history
    
        ### DTO
        - UserRecord { id, email, name, avatarUrl, subscribers, subscriptions: [channelId] }
        - WatchHistoryEntry { userId, videoId, watchedAt, position }
        '''
- связи dynamic view должны иметь notes и не иметь description
- связи static view должны иметь description и не иметь notes

## Правила разработки

### Описание связей

- `title` — краткое описание типа связи
- `technology` — протокол/технология взаимодействия
- `description` — подробное описание с gRPC API / REST endpoints и DTO

      description '''
      ### Reads/writes user profiles, subscriptions, watch history
    
      ### DTO
            - UserRecord { id, email, name, avatarUrl, subscribers, subscriptions: [channelId] }
            - WatchHistoryEntry { userId, videoId, watchedAt, position }
      '''


- `notes` — для dynamic views, описывают конкретные шаги с примерами данных
  
      notes '''
      ### Reads/writes user profiles, subscriptions, watch history
    
      ### DTO
            - UserRecord { id, email, name, avatarUrl, subscribers, subscriptions: [channelId] }
            - WatchHistoryEntry { userId, videoId, watchedAt, position }
      '''

### Форматирование DTO

```
### DTO
- UserRecord { id, email, name, avatarUrl, subscribers, subscriptions: [channelId] }
- WatchHistoryEntry { userId, videoId, watchedAt, position }
```

### Проверка и валидация

Проверяй диаграммы на соответствие правилам разработки

**Запуск линтера:**
```bash
python scripts/c4-lint.py diagrams/
npm run lint:c4
```

**Проверка синтаксиса LikeC4:**
```bash
npx likec4 validate diagrams/
```

**Полная проверка (синтаксис + правила):**
```bash
npm run lint
```

Для визуальной проверки:
```bash
npx likec4 serve
```

**Коды ошибок линтера:**
- `C4-001` — Двойное кодирование UTF-8
- `C4-002` — Дублирование specification
- `C4-003a` — Короткий синтаксис отношений
- `C4-003b-d` — Отношение без title/technology/description
- `C4-004` — Неправильный формат DTO
- `C4-005a` — Смешанный синтаксис элементов
- `C4-005b` — Незакрытый блок элемента
- `C4-006` — Описание без ### секций (warning)
- `C4-007` — Несоответствие именованию (warning)
- `C4-008` — Dynamic view: должен иметь `notes`, не должен иметь `description`
- `C4-009` — Static view: должен иметь `description`, не должен иметь `notes`
