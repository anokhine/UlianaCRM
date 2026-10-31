# UlianaCRM (Ulyana SUVK)

[English](#english) | [Русский](#русский)

---

## English

**UlianaCRM** is a lightweight, fast, and fully offline CRM system for Windows, written in Python (PySide6). The application is designed for convenient management of clients, tasks, files, and reminders, without requiring an internet connection or third-party servers.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt_for_Python-green?logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite&logoColor=white)

### 🌟 Complete Feature Overview (Version 1.6)

#### 👥 Client Management
*   **Top Panel:** Quick access to active clients.
*   **"All Clients" Tab:** A dedicated screen with a list of all clients, supporting pagination (up to 300 per page) and instant search by name and description.
*   **Pinning (📌):** Important clients can be pinned to always stay at the top of the list.
*   **Archiving:** Inactive clients can be archived, hiding them from the workspace while preserving all data. Archived clients can be easily restored.
*   **Descriptions:** Add detailed descriptions to clients. Smart text truncation (up to 5 lines) keeps the cards looking neat.
*   **Bulk Actions:** Select multiple clients via checkboxes for bulk archiving or deletion.

#### 📋 Tasks & Calendar
*   **Tasks with Deadlines:** Create tasks with specific due dates.
*   **Recurring Events:** Set tasks to repeat weekly, monthly, or yearly.
*   **Important Tasks:** Mark tasks with a star (⭐) to highlight them in a separate block.
*   **General Calendar:** A global 73-month calendar highlighting days with active tasks in yellow.
*   **Individual Calendar:** A client-specific calendar with the ability to filter tasks by date.

#### 🔔 Reminder System
*   **Smart Notifications:** The app automatically checks deadlines (considering recurrences) on startup and every 2 hours thereafter.
*   **Popup Window:** A semi-transparent panel in the bottom-left corner listing overdue or current tasks.
*   **Quick Action Buttons:**
    *   "Got it" — hides the reminder (until the next recurrence or forever).
    *   "Remind tomorrow" — snoozes the notification until 9:00 AM the next day.
    *   "Go to" — instantly opens the task in the interface.
*   **"!" Indicator:** If you minimize the reminder window, a yellow button with an exclamation mark appears in the bottom panel, signaling active reminders.

#### 📎 Files & Contacts
*   **Client Files:** Attach any documents directly to a client's card.
*   **Task & Post Files:** Attach files to both the task itself and specific posts in the task feed.
*   **File Management:** View, open, save to your computer, or delete files via a convenient context menu.
*   **Contacts:** Maintain a contact database for each client with quick copy options for phones and emails.

#### 🛡️ Security & Localization
*   **Local Storage:** The database (SQLite) and all attached files are stored in a folder next to the program. No data is sent to the cloud or third parties.
*   **Two Languages:** Full support for English and Russian interfaces (toggle in the bottom-left corner).

### 🚀 Getting Started

1. Go to the **[Releases](https://github.com/anokhine/UlianaCRM/releases)** section.
2. Download the latest `UlianaCRM.exe` file (e.g., `v1.6`).
3. Place the file in a convenient folder and run it (no installation required).
4. On the first run, the following will be automatically created next to the `.exe`:
   * `calendar.db` — the database with all clients and tasks.
   * `data_files` — a folder to store your attachments.

> **Warning:** To keep your data safe, it is recommended to periodically back up the `calendar.db` file and the `data_files` folder.

### 🛠️ Technical Details & Build
*   **Language:** Python 3
*   **Framework:** PySide6 (Qt)
*   **Database:** SQLite3
*   **Build Tool:** PyInstaller (`--onefile --windowed`)

---
*Designed and developed by: Dmitry Anokhin, 2026. With the assistance of the DeepSeek AI assistant.*

---

## Русский

**UlianaCRM** — это легковесная, быстрая и полностью офлайн CRM-система для Windows, написанная на Python (PySide6). Программа создана для удобного управления клиентами, задачами, файлами и напоминаниями, не требуя подключения к интернету и сторонних серверов.

### 🌟 Полный обзор функционала (Версия 1.6)

#### 👥 Управление клиентами
*   **Верхняя панель:** Быстрый доступ к активным клиентам.
*   **Вкладка «Все клиенты»:** Отдельный экран со списком всех клиентов, поддерживающий пагинацию (до 300 на страницу) и мгновенный поиск по имени и описанию.
*   **Закрепление (📌):** Важных клиентов можно закрепить, чтобы они всегда были первыми в списке.
*   **Архивация:** Неактивных клиентов можно отправить в архив, скрыв их из рабочего пространства, но сохранив все данные. Архивных клиентов можно легко восстановить.
*   **Описания:** Добавление подробных описаний к клиентам. Умное обрезание текста (до 5 строк) сохраняет аккуратный вид карточек.
*   **Массовые действия:** Возможность выделять несколько клиентов галочками для массовой архивации или удаления.

#### 📋 Задачи и Календарь
*   **Задачи с дедлайнами:** Создание задач с указанием конкретной даты.
*   **Повторяющиеся события:** Настройка задач на повторение каждую неделю, месяц или год.
*   **Важные задачи:** Отметка задач звездочкой (⭐) для выделения их в отдельный блок.
*   **Общий календарь:** Глобальный календарь на 73 месяца, где желтым цветом подсвечиваются дни с активными задачами.
*   **Индивидуальный календарь:** Привязка календаря к конкретному клиенту с возможностью фильтрации задач по дате.

#### 🔔 Система напоминаний
*   **Умные уведомления:** Программа автоматически проверяет дедлайны (учитывая повторения) при запуске и далее каждые 2 часа.
*   **Всплывающее окно:** Полупрозрачная панель в левом нижнем углу со списком просроченных или текущих задач.
*   **Кнопки быстрого действия:**
    *   «Ясно» — скрывает напоминание (до следующего повторения или навсегда).
    *   «Напомнить завтра» — откладывает уведомление до 9:00 утра следующего дня.
    *   «Перейти» — мгновенно открывает задачу в интерфейсе.
*   **Индикатор «!»:** Если свернуть окно напоминаний, в нижней панели появится желтая кнопка с восклицательным знаком, сигнализирующая о наличии активных дел.

#### 📎 Файлы и Контакты
*   **Файлы клиента:** Возможность прикреплять любые документы непосредственно к карточке клиента.
*   **Файлы задачи и постов:** Вложения можно добавлять как к самой задаче, так и к конкретным записям (постам) в ленте задачи.
*   **Управление файлами:** Просмотр, открытие, сохранение на компьютер и удаление файлов через удобное контекстное меню.
*   **Контакты:** Ведение базы контактов для каждого клиента с возможностью быстрого копирования телефонов и email.

#### 🛡️ Безопасность и Локализация
*   **Локальное хранение:** База данных (SQLite) и все прикрепленные файлы хранятся в папке рядом с программой. Никакие данные не уходят в облако или третьим лицам.
*   **Два языка:** Полная поддержка русского и английского интерфейсов (переключается кнопкой в нижнем левом углу).

### 🚀 Как начать работу

1. Перейдите в раздел **[Releases](https://github.com/anokhine/UlianaCRM/releases)**.
2. Скачайте последнюю версию файла `UlianaCRM.exe` (например, `v1.6`).
3. Поместите файл в удобную для вас папку и запустите (установка не требуется).
4. При первом запуске рядом с `.exe` автоматически создадутся:
   * `calendar.db` — база данных со всеми клиентами и задачами.
   * `data_files` — папка для хранения ваших вложений (файлов).

> **Внимание:** Для сохранности данных рекомендуется периодически делать резервную копию файла `calendar.db` и папки `data_files`.

### 🛠️ Технические детали и сборка
*   **Язык:** Python 3
*   **Фреймворк:** PySide6 (Qt)
*   **БД:** SQLite3
*   **Сборка:** PyInstaller (`--onefile --windowed`)

---
*Спроектировано и разработано: Дмитрий Анохин, 2026 год. При участии ИИ-ассистента DeepSeek.*
