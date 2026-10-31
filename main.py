import sys
import os
import sqlite3
import shutil
import calendar
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QPushButton, QLabel, QScrollArea, 
                               QSplitter, QCalendarWidget, QTextEdit, QListWidget, 
                               QFrame, QInputDialog, QMessageBox, QMenu, QDialog,
                               QLineEdit, QDateEdit, QFormLayout, QDialogButtonBox,
                               QGridLayout, QFileDialog, QStackedWidget, QTableView,
                               QListWidgetItem, QGraphicsDropShadowEffect, QSizePolicy,
                               QStyle, QCheckBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QDate, QTimer, QEvent, QLocale, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QIcon


def get_db_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, "calendar.db")


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


DB_PATH = get_db_path()

TRANSLATIONS = {
    "RU": {
        "general": "Общий", "add_client": "+ Добавить клиента", "all_clients": "Все клиенты",
        "archive_tasks": "Архив задач", "all_tasks": "Все активные задачи", "gen_cal": "Общий календарь задач",
        "tasks": "Задачи", "important": "Важные задачи", "contacts": "Контакты", "client_files": "Файлы клиента",
        "task_files": "Файлы задачи", "calendar": "Календарь клиента", "today": "Сегодня", "send": "Отправить",
        "attach": "📎 Прикрепить файлы к посту", "select_task": "Выберите задачу слева", "about_title": "О программе",
        "lang_btn": "EN", "reset_filter": "✖ Сбросить фильтр по дате", "post_placeholder": "Нажмите здесь, чтобы добавить пост...",
        "search_placeholder": "Поиск по контактам...", "archive_title": "Архив задач", "all_clients_title": "Все клиенты",
        "delete_all": "Удалить всё", "delete_selected": "Удалить выделенное", "restore": "Восстановить",
        "to_archive": "📦 В архив", "delete_task": "❌ Удалить задачу", "recur_none": "Не повторяется",
        "recur_weekly": "Повторить раз в 7 дней", "recur_monthly": "Повторить раз в месяц", "recur_yearly": "Повторять каждый год",
        "recur_weekly_short": "Повторяется еженедельно", "recur_monthly_short": "Повторяется ежемесячно", "recur_yearly_short": "Повторяется ежегодно",
        "recur_label": "Повторение:", "client_name": "Имя клиента:", "client_desc": "Описание:",
        "pin_client": "📌 Закрепить клиента", "search_clients_placeholder": "Поиск по клиентам...", "clear_search": "✖ Снять фильтр",
        "edit_client": "✏️ Редактировать клиента", "delete_client": "❌ Удалить клиента", "go_to_client": "Перейти",
        "pinned": "📌 ", "in_archive": "В архиве",
        "reminders_title": "Напоминания", "reminder_clear": "Ясно",
        "reminder_snooze": "Напомнить завтра", "reminder_go": "Перейти",
        "reminders_tooltip": "Напоминания"
    },
    "EN": {
        "general": "General", "add_client": "+ Add Client", "all_clients": "All Clients",
        "archive_tasks": "Task Archive", "all_tasks": "All active tasks", "gen_cal": "General task calendar",
        "tasks": "Tasks", "important": "Important tasks", "contacts": "Contacts", "client_files": "Client files",
        "task_files": "Task files", "calendar": "Client calendar", "today": "Today", "send": "Send",
        "attach": "📎 Attach files to post", "select_task": "Select a task on the left", "about_title": "About",
        "lang_btn": "RU", "reset_filter": "✖ Reset date filter", "post_placeholder": "Click here to add a post...",
        "search_placeholder": "Search contacts...", "archive_title": "Task Archive", "all_clients_title": "All Clients",
        "delete_all": "Delete All", "delete_selected": "Delete Selected", "restore": "Restore",
        "to_archive": "📦 To Archive", "delete_task": "❌ Delete task", "recur_none": "Does not repeat",
        "recur_weekly": "Repeat every 7 days", "recur_monthly": "Repeat every month", "recur_yearly": "Repeat every year",
        "recur_weekly_short": "Repeats weekly", "recur_monthly_short": "Repeats monthly", "recur_yearly_short": "Repeats yearly",
        "recur_label": "Recurrence:", "client_name": "Client name:", "client_desc": "Description:",
        "pin_client": "📌 Pin client", "search_clients_placeholder": "Search clients...", "clear_search": "✖ Clear filter",
        "edit_client": "✏️ Edit client", "delete_client": "❌ Delete client", "go_to_client": "Go to",
        "pinned": "📌 ", "in_archive": "In archive",
        "reminders_title": "Reminders", "reminder_clear": "Got it",
        "reminder_snooze": "Remind tomorrow", "reminder_go": "Go to",
        "reminders_tooltip": "Reminders"
    }
}


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)


def get_all_occurrences(deadline_str, recurrence, max_date):
    if not deadline_str: return []
    try:
        d, m, y = map(int, deadline_str.split('.'))
        current = datetime(y, m, d)
    except: return []
    if recurrence == 'none' or not recurrence: return [current]
    occurrences = []
    while current <= max_date:
        occurrences.append(current)
        if recurrence == 'weekly': current += timedelta(days=7)
        elif recurrence == 'monthly': current = add_months(current, 1)
        elif recurrence == 'yearly': current = add_months(current, 12)
        else: break
    return occurrences


def is_task_on_date(deadline_str, recurrence, target_qdate):
    if not deadline_str: return False
    try:
        d, m, y = map(int, deadline_str.split('.'))
        base_date = datetime(y, m, d)
    except: return False
    target_date = datetime(target_qdate.year(), target_qdate.month(), target_qdate.day())
    if recurrence == 'none' or not recurrence: return target_date == base_date
    current = base_date
    while current <= target_date:
        if current == target_date: return True
        if recurrence == 'weekly': current += timedelta(days=7)
        elif recurrence == 'monthly': current = add_months(current, 1)
        elif recurrence == 'yearly': current = add_months(current, 12)
        else: break
    return False


class MultiLineElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.lines_limit = 5
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fm = self.fontMetrics()
        self.setMinimumHeight(fm.lineSpacing() * self.lines_limit)
        self.setMaximumHeight(fm.lineSpacing() * self.lines_limit)
        self.setStyleSheet("color: #5f6368; font-size: 12px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.palette().color(self.foregroundRole()))
        fm = self.fontMetrics()
        line_spacing = fm.lineSpacing()
        text = self.text()
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if fm.horizontalAdvance(test_line) <= self.width():
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        if len(lines) > self.lines_limit:
            lines = lines[:self.lines_limit]
            last_line = lines[-1]
            lines[-1] = fm.elidedText(last_line + " ...", Qt.ElideRight, self.width())
        elif len(lines) == self.lines_limit:
            total_len = sum(len(l) for l in lines)
            original_len = len(text)
            if total_len < original_len:
                last_line = lines[-1]
                lines[-1] = fm.elidedText(last_line + " ...", Qt.ElideRight, self.width())
        y = 0
        for line in lines:
            painter.drawText(0, y + fm.ascent(), line)
            y += line_spacing


class MiniCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dates_with_tasks = set()
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setNavigationBarVisible(False)
        self.setGridVisible(False)
        self.view = self.findChild(QTableView)
        if self.view:
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.viewport().installEventFilter(self)
            self.view.clicked.connect(self.handle_table_click)
            self.view.doubleClicked.connect(self.handle_table_click)

    def handle_table_click(self, index):
        if index.isValid():
            date = self.dateForCell(index.row(), index.column())
            if date.isValid():
                m = self.monthShown() or QDate.currentDate().month()
                y = self.yearShown() or QDate.currentDate().year()
                if date.month() == m and date.year() == y:
                    self.clicked.emit(date)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            main_scroll = self.window().findChild(QScrollArea, "general_calendar_scroll")
            if main_scroll:
                vbar = main_scroll.verticalScrollBar()
                vbar.setValue(vbar.value() - event.angleDelta().y())
            return True
        return super().eventFilter(obj, event)

    def set_task_dates(self, dates):
        self.dates_with_tasks = dates
        self.updateCells()

    def paintCell(self, painter, rect, date):
        m = self.monthShown() or QDate.currentDate().month()
        y = self.yearShown() or QDate.currentDate().year()
        if date.month() != m or date.year() != y:
            painter.fillRect(rect, Qt.white)
            return
        painter.save()
        is_task_date = date in self.dates_with_tasks
        is_today = date == QDate.currentDate() 
        if is_today:
            painter.fillRect(rect, QColor("#e8f0fe")) 
            painter.setPen(QColor("#1967d2"))
        elif is_task_date:
            painter.fillRect(rect, QColor("#FFEB3B")) 
            painter.setPen(Qt.black) 
        else:
            painter.fillRect(rect, Qt.white)
            if date.dayOfWeek() in (6, 7): painter.setPen(QColor("#c5221f")) 
            else: painter.setPen(Qt.black)
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))
        painter.restore()


class CustomCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dates_with_tasks = set()
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

    def set_task_dates(self, dates):
        self.dates_with_tasks = dates
        self.updateCells()

    def paintCell(self, painter, rect, date):
        m = self.monthShown() or QDate.currentDate().month()
        y = self.yearShown() or QDate.currentDate().year()
        if date.month() != m or date.year() != y:
            painter.fillRect(rect, Qt.white)
            return
        painter.save()
        is_task_date = date in self.dates_with_tasks
        is_today = date == QDate.currentDate()
        if is_today:
            painter.fillRect(rect, QColor("#1a73e8")) 
            painter.setPen(Qt.white)
        elif is_task_date:
            painter.fillRect(rect, QColor("#FFEB3B")) 
            painter.setPen(Qt.black)
        else:
            painter.fillRect(rect, Qt.white)
            if date.dayOfWeek() in (6, 7): painter.setPen(QColor("#c5221f")) 
            else: painter.setPen(Qt.black)
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))
        painter.restore()


class TaskDialog(QDialog):
    def __init__(self, parent=None, title_text="", default_qdate=None, recurrence='none'):
        super().__init__(parent)
        self.current_lang = parent.current_lang if parent else "RU"
        is_ru = self.current_lang == "RU"
        t = TRANSLATIONS[self.current_lang]
        self.setWindowTitle("Задача" if is_ru else "Task")
        self.resize(400, 250)
        layout = QFormLayout(self)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Например: Оплатить хостинг..." if is_ru else "Example: Pay for hosting...")
        self.title_input.setText(title_text)
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("dd.MM.yyyy")
        self.deadline_input.setLocale(QLocale("ru_RU") if is_ru else QLocale("en_US"))
        popup_cal = self.deadline_input.calendarWidget()
        if popup_cal:
            popup_cal.setLocale(QLocale("ru_RU") if is_ru else QLocale("en_US"))
            popup_cal.setMinimumSize(320, 240)
            popup_cal.setStyleSheet("QCalendarWidget QWidget { background-color: #ffffff; } QCalendarWidget QToolButton { color: #3c4043; background-color: transparent; border: none; padding: 5px; } QCalendarWidget QAbstractItemView:enabled { background-color: #ffffff; color: #3c4043; selection-background-color: #1a73e8; selection-color: #ffffff; } QCalendarWidget QTableView { outline: none; }")
        if default_qdate and default_qdate.isValid(): self.deadline_input.setDate(default_qdate)
        else: self.deadline_input.setDate(QDate.currentDate())
        self.recur_group = QButtonGroup(self)
        self.radio_none = QRadioButton(t["recur_none"])
        self.radio_weekly = QRadioButton(t["recur_weekly"])
        self.radio_monthly = QRadioButton(t["recur_monthly"])
        self.radio_yearly = QRadioButton(t["recur_yearly"])
        self.recur_group.addButton(self.radio_none)
        self.recur_group.addButton(self.radio_weekly)
        self.recur_group.addButton(self.radio_monthly)
        self.recur_group.addButton(self.radio_yearly)
        if recurrence == 'weekly': self.radio_weekly.setChecked(True)
        elif recurrence == 'monthly': self.radio_monthly.setChecked(True)
        elif recurrence == 'yearly': self.radio_yearly.setChecked(True)
        else: self.radio_none.setChecked(True)
        recur_layout = QVBoxLayout()
        recur_layout.addWidget(self.radio_none)
        recur_layout.addWidget(self.radio_weekly)
        recur_layout.addWidget(self.radio_monthly)
        recur_layout.addWidget(self.radio_yearly)
        layout.addRow("Название задачи:" if is_ru else "Task name:", self.title_input)
        layout.addRow("Дедлайн:" if is_ru else "Deadline:", self.deadline_input)
        layout.addRow(t["recur_label"], recur_layout)
        buttons = QDialogButtonBox()
        buttons.addButton("ОК" if is_ru else "OK", QDialogButtonBox.AcceptRole)
        buttons.addButton("Отмена" if is_ru else "Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def get_recurrence(self):
        if self.radio_weekly.isChecked(): return 'weekly'
        if self.radio_monthly.isChecked(): return 'monthly'
        if self.radio_yearly.isChecked(): return 'yearly'
        return 'none'


class ContactDialog(QDialog):
    def __init__(self, parent=None, contact_data=None):
        super().__init__(parent)
        is_ru = parent and parent.current_lang == "RU"
        self.setWindowTitle("Контакт" if is_ru else "Contact")
        self.resize(500, 450)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        def create_copy_row(line_edit):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(line_edit)
            btn_copy = QPushButton("📋")
            btn_copy.setFixedSize(30, 30)
            def copy_to_clipboard():
                QApplication.clipboard().setText(line_edit.text())
                btn_copy.setText("✅")
                QTimer.singleShot(1000, lambda: btn_copy.setText("📋"))
            btn_copy.clicked.connect(copy_to_clipboard)
            row_layout.addWidget(btn_copy)
            return row_widget
        self.name_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.phone1 = QLineEdit()
        self.phone2 = QLineEdit()
        self.phone3 = QLineEdit()
        self.email1 = QLineEdit()
        self.email2 = QLineEdit()
        self.email3 = QLineEdit()
        if contact_data:
            self.name_input.setText(contact_data[0] or "")
            self.desc_input.setText(contact_data[1] or "")
            self.phone1.setText(contact_data[2] or "")
            self.phone2.setText(contact_data[3] or "")
            self.phone3.setText(contact_data[4] or "")
            self.email1.setText(contact_data[5] or "")
            self.email2.setText(contact_data[6] or "")
            self.email3.setText(contact_data[7] or "")
        form_layout.addRow("Имя (обязательно):" if is_ru else "Name (required):", create_copy_row(self.name_input))
        form_layout.addRow("Описание:" if is_ru else "Description:", self.desc_input)
        form_layout.addRow(QLabel("<b>Телефоны:</b>" if is_ru else "<b>Phones:</b>"))
        form_layout.addRow("Телефон 1:" if is_ru else "Phone 1:", create_copy_row(self.phone1))
        form_layout.addRow("Телефон 2:" if is_ru else "Phone 2:", create_copy_row(self.phone2))
        form_layout.addRow("Телефон 3:" if is_ru else "Phone 3:", create_copy_row(self.phone3))
        form_layout.addRow(QLabel("<b>Email:</b>"))
        form_layout.addRow("Email 1:", create_copy_row(self.email1))
        form_layout.addRow("Email 2:", create_copy_row(self.email2))
        form_layout.addRow("Email 3:", create_copy_row(self.email3))
        layout.addLayout(form_layout)
        buttons = QDialogButtonBox()
        buttons.addButton("Сохранить" if is_ru else "Save", QDialogButtonBox.AcceptRole)
        buttons.addButton("Отмена" if is_ru else "Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ClientDialog(QDialog):
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.current_lang = parent.current_lang if parent else "RU"
        is_ru = self.current_lang == "RU"
        t = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(t["add_client"] if not client_data else t["edit_client"])
        self.resize(400, 300)
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        self.pin_checkbox = QCheckBox(t["pin_client"])
        if client_data:
            self.name_input.setText(client_data[1] or "")
            self.desc_input.setText(client_data[2] or "")
            self.pin_checkbox.setChecked(bool(client_data[3]))
        layout.addRow(t["client_name"], self.name_input)
        layout.addRow(t["client_desc"], self.desc_input)
        layout.addRow("", self.pin_checkbox)
        buttons = QDialogButtonBox()
        buttons.addButton("Сохранить" if is_ru else "Save", QDialogButtonBox.AcceptRole)
        buttons.addButton("Отмена" if is_ru else "Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class ReminderPopup(QWidget):
    """Полупрозрачная всплывающая панель напоминаний в левом нижнем углу окна."""
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            ReminderPopup {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #dadce0;
                border-radius: 10px;
            }
        """)
        self.setFixedWidth(440)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        header = QHBoxLayout()
        self.title = QLabel(TRANSLATIONS[self.main_window.current_lang]["reminders_title"])
        self.title.setStyleSheet("font-weight: bold; font-size: 15px; color: #202124; background: transparent;")
        header.addWidget(self.title)
        header.addStretch()
        btn_close = QPushButton("✖")
        btn_close.setFixedSize(24, 24)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setToolTip("Свернуть" if self.main_window.current_lang == "RU" else "Minimize")
        btn_close.setStyleSheet(
            "QPushButton { background-color: transparent; border: none; font-size: 14px; "
            "color: #5f6368; border-radius: 12px; padding: 0; } "
            "QPushButton:hover { background-color: rgba(0,0,0,30); }"
        )
        btn_close.clicked.connect(self.main_window.hide_reminder_popup)
        header.addWidget(btn_close)
        outer.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; } "
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        self.scroll.viewport().setStyleSheet("background: transparent;")
        self.items_container = QWidget()
        self.items_container.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(8)
        self.items_layout.addStretch()
        self.scroll.setWidget(self.items_container)
        outer.addWidget(self.scroll, 1)

        self.hide()

    def update_title(self):
        self.title.setText(TRANSLATIONS[self.main_window.current_lang]["reminders_title"])

    def refresh(self, reminders):
        # Очищаем всё, кроме растяжки в конце
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not reminders:
            return

        t = TRANSLATIONS[self.main_window.current_lang]

        for r in reminders:
            reminder_id, task_id, client_id, task_title, client_name, occurrence_date, status = r

            card = QFrame()
            card.setAttribute(Qt.WA_StyledBackground, True)
            card.setStyleSheet(
                "QFrame { background-color: rgba(255, 255, 255, 220); "
                "border: 1px solid #dadce0; border-radius: 6px; }"
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 10, 10, 10)
            cl.setSpacing(6)

            lbl_title = QLabel(task_title)
            lbl_title.setWordWrap(True)
            lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #202124; background: transparent; border: none;")
            cl.addWidget(lbl_title)

            lbl_info = QLabel(f"👤 {client_name}   |   📅 {occurrence_date}")
            lbl_info.setStyleSheet("color: #5f6368; font-size: 11px; background: transparent; border: none;")
            cl.addWidget(lbl_info)

            btns = QHBoxLayout()
            btns.setSpacing(6)

            btn_clear = QPushButton(t["reminder_clear"])
            btn_clear.setCursor(Qt.PointingHandCursor)
            btn_clear.setStyleSheet(
                "QPushButton { background-color: #1a73e8; color: #ffffff; font-weight: bold; "
                "border: none; border-radius: 4px; padding: 6px 12px; } "
                "QPushButton:hover { background-color: #1557b0; }"
            )
            btn_clear.clicked.connect(
                lambda checked=False, rid=reminder_id: self.main_window.mark_reminder_cleared(rid)
            )
            btns.addWidget(btn_clear)

            btn_snooze = QPushButton(t["reminder_snooze"])
            btn_snooze.setCursor(Qt.PointingHandCursor)
            btn_snooze.setStyleSheet(
                "QPushButton { background-color: #f1f3f4; color: #202124; "
                "border: none; border-radius: 4px; padding: 6px 12px; } "
                "QPushButton:hover { background-color: #e8eaed; }"
            )
            btn_snooze.clicked.connect(
                lambda checked=False, rid=reminder_id: self.main_window.snooze_reminder(rid)
            )
            btns.addWidget(btn_snooze)

            btn_go = QPushButton(t["reminder_go"])
            btn_go.setCursor(Qt.PointingHandCursor)
            btn_go.setStyleSheet(
                "QPushButton { background-color: #e8f0fe; color: #1967d2; font-weight: bold; "
                "border: none; border-radius: 4px; padding: 6px 12px; } "
                "QPushButton:hover { background-color: #d2e3fc; }"
            )
            btn_go.clicked.connect(
                lambda checked=False, tid=task_id, cid=client_id:
                self.main_window.reminder_go_to_task(cid, tid)
            )
            btns.addWidget(btn_go)

            cl.addLayout(btns)
            self.items_layout.insertWidget(self.items_layout.count() - 1, card)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UlianaCRM (Ульяна СУВК)")
        self.setWindowIcon(QIcon(get_resource_path("app.ico")))
        self.resize(1400, 900)
        self.setMinimumSize(1100, 700) 
        self.current_lang = "RU"
        self.current_client_id = None
        self.current_task_id = None 
        self.pending_post_files = []
        self.filter_date = None
        self.today_month_widget = None
        self.mini_calendars = []
        self.all_clients_page_num = 1
        self.all_clients_per_page = 300
        self.all_clients_filter = ""
        self.reminder_popup_dismissed = False
        self.reminder_popup = None
        self.init_db()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        top_panel = QWidget()
        top_panel.setObjectName("topPanel")
        top_panel.setFixedHeight(60)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(20, 0, 20, 0)
        
        client_nav_container = QWidget()
        client_nav_layout = QHBoxLayout(client_nav_container)
        client_nav_layout.setContentsMargins(0, 0, 0, 0)
        client_nav_layout.setSpacing(5)
        self.btn_scroll_left = QPushButton()
        self.btn_scroll_left.setFixedSize(30, 30)
        self.btn_scroll_left.setCursor(Qt.PointingHandCursor)
        self.btn_scroll_left.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.btn_scroll_left.setIconSize(QSize(16, 16))
        self.btn_scroll_left.setStyleSheet("QPushButton { background-color: #ffffff; border: 1px solid #dadce0; border-radius: 15px; } QPushButton:hover { background-color: #f1f3f4; } QPushButton:disabled { background-color: #f8f9fa; border: 1px solid #f1f3f4;}")
        self.btn_scroll_left.clicked.connect(self.scroll_clients_left)
        self.btn_scroll_left.hide()
        self.clients_scroll = QScrollArea()
        self.clients_scroll.setWidgetResizable(True)
        self.clients_scroll.setStyleSheet("background: transparent; border: none;")
        self.clients_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clients_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clients_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.clients_container = QWidget()
        self.clients_layout = QHBoxLayout(self.clients_container)
        self.clients_layout.setContentsMargins(0, 0, 0, 0)
        self.clients_layout.setSpacing(10)
        self.clients_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.clients_scroll.setWidget(self.clients_container)
        self.btn_scroll_right = QPushButton()
        self.btn_scroll_right.setFixedSize(30, 30)
        self.btn_scroll_right.setCursor(Qt.PointingHandCursor)
        self.btn_scroll_right.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.btn_scroll_right.setIconSize(QSize(16, 16))
        self.btn_scroll_right.setStyleSheet("QPushButton { background-color: #ffffff; border: 1px solid #dadce0; border-radius: 15px; } QPushButton:hover { background-color: #f1f3f4; } QPushButton:disabled { background-color: #f8f9fa; border: 1px solid #f1f3f4;}")
        self.btn_scroll_right.clicked.connect(self.scroll_clients_right)
        self.btn_scroll_right.hide()
        client_nav_layout.addWidget(self.btn_scroll_left)
        client_nav_layout.addWidget(self.clients_scroll, 1) 
        client_nav_layout.addWidget(self.btn_scroll_right)
        top_layout.addWidget(client_nav_container, 1)
        
        self.btn_archive = QPushButton("Архив задач")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_archive.clicked.connect(self.show_archive_view)
        self.btn_archive.setStyleSheet("QPushButton { background-color: #f1f3f4; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; margin-left: 10px; } QPushButton:hover { background-color: #e8eaed; }")
        top_layout.addWidget(self.btn_archive)
        self.btn_all_clients = QPushButton("Все клиенты")
        self.btn_all_clients.setCursor(Qt.PointingHandCursor)
        self.btn_all_clients.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_all_clients.clicked.connect(self.show_all_clients_view)
        self.btn_all_clients.setStyleSheet("QPushButton { background-color: #f1f3f4; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; margin-left: 10px; } QPushButton:hover { background-color: #e8eaed; }")
        top_layout.addWidget(self.btn_all_clients)
        self.btn_add_client = QPushButton("+ Добавить клиента")
        self.btn_add_client.setObjectName("primaryBtn")
        self.btn_add_client.setCursor(Qt.PointingHandCursor)
        self.btn_add_client.clicked.connect(self.add_client_dialog)
        top_layout.addWidget(self.btn_add_client)
        self.main_layout.addWidget(top_panel)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #dadce0;")
        self.main_layout.addWidget(line)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)

        # ================= СТРАНИЦА 0: ОБЩИЙ ВИД =================
        self.general_page = QWidget()
        general_layout = QHBoxLayout(self.general_page)
        general_layout.setContentsMargins(0, 0, 0, 0)
        general_layout.setSpacing(0)
        self.gen_splitter = QSplitter(Qt.Horizontal)
        self.gen_splitter.setHandleWidth(1)
        self.gen_splitter.setChildrenCollapsible(False) 
        gen_left_widget = QWidget()
        gen_left_widget.setObjectName("leftPanel")
        gen_left_widget.setMinimumWidth(250) 
        gen_left_layout = QVBoxLayout(gen_left_widget)
        gen_left_layout.setContentsMargins(20, 20, 20, 20)
        self.gen_tasks_title = QLabel("Все активные задачи")
        self.gen_tasks_title.setObjectName("sectionTitle")
        gen_left_layout.addWidget(self.gen_tasks_title)
        self.general_tasks_list = QListWidget()
        self.general_tasks_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.general_tasks_list.itemClicked.connect(self.on_general_task_clicked)
        gen_left_layout.addWidget(self.general_tasks_list, 1) 
        search_container = QWidget()
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(0, 10, 0, 0)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по контактам...")
        self.search_input.setStyleSheet("QLineEdit { border: 1px solid #dadce0; border-radius: 4px; padding: 8px; background-color: #ffffff; } QLineEdit:focus { border: 1px solid #1a73e8; }")
        self.search_input.textChanged.connect(self.on_contact_search)
        search_layout.addWidget(self.search_input)
        gen_left_layout.addWidget(search_container)
        gen_right_widget = QWidget()
        gen_right_widget.setObjectName("centerPanel")
        gen_right_widget.setMinimumWidth(700) 
        gen_right_layout = QVBoxLayout(gen_right_widget)
        gen_right_layout.setContentsMargins(20, 20, 20, 20)
        gen_cal_header = QHBoxLayout()
        self.gen_cal_title = QLabel("Общий календарь задач")
        self.gen_cal_title.setObjectName("sectionTitle")
        gen_cal_header.addWidget(self.gen_cal_title)
        gen_cal_header.addStretch()
        self.btn_gen_today = QPushButton("Сегодня")
        self.btn_gen_today.setObjectName("primaryBtn")
        self.btn_gen_today.setCursor(Qt.PointingHandCursor)
        self.btn_gen_today.clicked.connect(self.scroll_to_current_month)
        self.btn_gen_today.setStyleSheet("padding: 4px 12px; font-size: 12px;") 
        gen_cal_header.addWidget(self.btn_gen_today)
        gen_right_layout.addLayout(gen_cal_header)
        self.general_calendar_scroll = QScrollArea()
        self.general_calendar_scroll.setWidgetResizable(True)
        self.general_calendar_scroll.setStyleSheet("border: none; background-color: transparent;")
        self.general_calendar_scroll.setObjectName("general_calendar_scroll") 
        self.general_calendar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.calendar_container = QWidget()
        self.calendar_grid_layout = QGridLayout(self.calendar_container)
        self.calendar_grid_layout.setSpacing(20)
        self.calendar_grid_layout.setColumnStretch(0, 1)
        self.calendar_grid_layout.setColumnStretch(1, 1)
        self.calendar_grid_layout.setColumnStretch(2, 1)
        self.general_calendar_scroll.setWidget(self.calendar_container)
        gen_right_layout.addWidget(self.general_calendar_scroll, 1)
        self.gen_splitter.addWidget(gen_left_widget)
        self.gen_splitter.addWidget(gen_right_widget)
        self.gen_splitter.setSizes([350, 1050])
        general_layout.addWidget(self.gen_splitter)
        self.stacked_widget.addWidget(self.general_page)

        self.search_popup = QListWidget(self) 
        self.search_popup.setStyleSheet("QListWidget { border: 1px solid #dadce0; border-radius: 8px; background-color: #ffffff; outline: none; } QListWidget::item { border-bottom: 1px solid #f1f3f4; } QListWidget::item:hover { background-color: #f1f3f4; } QListWidget::item:selected { background-color: #e8f0fe; }")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.search_popup.setGraphicsEffect(shadow)
        self.search_popup.itemClicked.connect(self.on_search_result_clicked)
        self.search_popup.hide()

        # ================= СТРАНИЦА 1: ВИД КЛИЕНТА =================
        self.client_page = QWidget()
        client_page_layout = QVBoxLayout(self.client_page)
        client_page_layout.setContentsMargins(0, 0, 0, 0)
        client_page_layout.setSpacing(0)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setObjectName("leftPanel")
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)
        tasks_header = QHBoxLayout()
        self.tasks_title = QLabel("Задачи")
        self.tasks_title.setObjectName("sectionTitle")
        tasks_header.addWidget(self.tasks_title)
        tasks_header.addStretch()
        btn_add_task = QPushButton("+")
        btn_add_task.setObjectName("iconBtn")
        btn_add_task.setCursor(Qt.PointingHandCursor)
        btn_add_task.clicked.connect(self.add_task_dialog)
        tasks_header.addWidget(btn_add_task)
        left_layout.addLayout(tasks_header)
        self.reset_filter_btn = QPushButton("✖ Сбросить фильтр по дате")
        self.reset_filter_btn.setStyleSheet("color: #c5221f; text-align: left; font-weight: bold; border: none; background: transparent; padding: 0;")
        self.reset_filter_btn.setCursor(Qt.PointingHandCursor)
        self.reset_filter_btn.clicked.connect(self.reset_date_filter)
        self.reset_filter_btn.hide()
        left_layout.addWidget(self.reset_filter_btn)
        self.tasks_list = QListWidget()
        self.tasks_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tasks_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tasks_list.itemClicked.connect(self.on_task_clicked)
        self.tasks_list.itemDoubleClicked.connect(self.edit_task_dialog) 
        self.tasks_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tasks_list.customContextMenuRequested.connect(self.show_task_context_menu)
        left_layout.addWidget(self.tasks_list, 3) 
        self.important_title = QLabel("Важные задачи")
        self.important_title.setObjectName("sectionTitle")
        left_layout.addWidget(self.important_title)
        self.important_list = QListWidget()
        self.important_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.important_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.important_list.itemClicked.connect(self.on_task_clicked)
        self.important_list.itemDoubleClicked.connect(self.edit_task_dialog) 
        self.important_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.important_list.customContextMenuRequested.connect(self.show_task_context_menu)
        left_layout.addWidget(self.important_list, 2) 
        contacts_header = QHBoxLayout()
        self.contacts_title = QLabel("Контакты")
        self.contacts_title.setObjectName("sectionTitle")
        contacts_header.addWidget(self.contacts_title)
        contacts_header.addStretch()
        btn_add_contact = QPushButton("+")
        btn_add_contact.setObjectName("iconBtn")
        btn_add_contact.setCursor(Qt.PointingHandCursor)
        btn_add_contact.clicked.connect(self.add_contact_dialog)
        contacts_header.addWidget(btn_add_contact)
        left_layout.addLayout(contacts_header)
        self.contacts_list = QListWidget()
        self.contacts_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.contacts_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contacts_list.itemDoubleClicked.connect(self.edit_contact_dialog)
        self.contacts_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contacts_list.customContextMenuRequested.connect(self.show_contact_context_menu)
        left_layout.addWidget(self.contacts_list, 1) 
        client_files_header = QHBoxLayout()
        self.client_files_title = QLabel("Файлы клиента")
        self.client_files_title.setObjectName("sectionTitle")
        client_files_header.addWidget(self.client_files_title)
        client_files_header.addStretch()
        btn_add_client_file = QPushButton("+")
        btn_add_client_file.setObjectName("iconBtn")
        btn_add_client_file.setCursor(Qt.PointingHandCursor)
        btn_add_client_file.clicked.connect(self.add_client_file)
        client_files_header.addWidget(btn_add_client_file)
        left_layout.addLayout(client_files_header)
        self.client_files_list = QListWidget()
        self.client_files_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.client_files_list.setFixedHeight(250) 
        self.client_files_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.client_files_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.client_files_list.customContextMenuRequested.connect(self.show_file_context_menu)
        left_layout.addWidget(self.client_files_list)
        left_scroll.setWidget(left_widget)

        center_widget = QWidget()
        center_widget.setObjectName("centerPanel")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(20, 20, 20, 20)
        self.task_title = QLabel("Выберите задачу слева")
        self.task_title.setObjectName("activeTaskTitle")
        center_layout.addWidget(self.task_title)
        posts_area = QScrollArea()
        posts_area.setWidgetResizable(True)
        posts_area.setStyleSheet("background-color: transparent; border: none;")
        posts_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        posts_widget = QWidget()
        self.posts_layout = QVBoxLayout(posts_widget)
        self.posts_layout.setContentsMargins(5, 5, 5, 5)
        self.posts_layout.setSpacing(15)
        self.posts_layout.addStretch()
        posts_area.setWidget(posts_widget)
        center_layout.addWidget(posts_area, 1) 
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 10, 0, 0)
        self.post_input = QTextEdit()
        self.post_input.setPlaceholderText("Нажмите здесь, чтобы добавить пост...")
        self.post_input.setObjectName("postInput")
        self.post_input.setMaximumHeight(80)
        self.post_input.setEnabled(False)
        input_layout.addWidget(self.post_input)
        buttons_layout = QHBoxLayout()
        self.btn_attach = QPushButton("📎 Прикрепить файлы к посту")
        self.btn_attach.setObjectName("textBtn")
        self.btn_attach.setCursor(Qt.PointingHandCursor)
        self.btn_attach.setEnabled(False)
        self.btn_attach.clicked.connect(self.attach_files_to_post)
        self.btn_send = QPushButton("Отправить")
        self.btn_send.setObjectName("primaryBtn")
        self.btn_send.setCursor(Qt.PointingHandCursor)
        self.btn_send.setEnabled(False)
        self.btn_send.clicked.connect(self.send_post)
        buttons_layout.addWidget(self.btn_attach)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_send)
        input_layout.addLayout(buttons_layout)
        center_layout.addWidget(input_container)

        right_widget = QWidget()
        right_widget.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        task_files_header = QHBoxLayout()
        self.task_files_title = QLabel("Файлы задачи")
        self.task_files_title.setObjectName("sectionTitle")
        task_files_header.addWidget(self.task_files_title)
        task_files_header.addStretch()
        btn_add_task_file = QPushButton("+")
        btn_add_task_file.setObjectName("iconBtn")
        btn_add_task_file.setCursor(Qt.PointingHandCursor)
        btn_add_task_file.clicked.connect(self.add_task_file)
        task_files_header.addWidget(btn_add_task_file)
        right_layout.addLayout(task_files_header)
        self.task_files_list = QListWidget()
        self.task_files_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.task_files_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_files_list.customContextMenuRequested.connect(self.show_file_context_menu)
        right_layout.addWidget(self.task_files_list, 1) 
        calendar_header = QHBoxLayout()
        self.calendar_title = QLabel("Календарь клиента")
        self.calendar_title.setObjectName("sectionTitle")
        calendar_header.addWidget(self.calendar_title)
        calendar_header.addStretch()
        self.btn_today = QPushButton("Сегодня")
        self.btn_today.setObjectName("primaryBtn")
        self.btn_today.setCursor(Qt.PointingHandCursor)
        self.btn_today.clicked.connect(self.go_to_today)
        self.btn_today.setStyleSheet("padding: 4px 12px; font-size: 12px;") 
        calendar_header.addWidget(self.btn_today)
        right_layout.addLayout(calendar_header)
        self.calendar = CustomCalendar()
        self.calendar.clicked.connect(self.on_calendar_clicked)
        self.calendar.activated.connect(self.on_calendar_double_clicked) 
        self.calendar.setStyleSheet("QCalendarWidget QWidget { background-color: #ffffff; } QCalendarWidget QToolButton { color: #3c4043; background-color: transparent; border: none; padding: 5px; } QCalendarWidget QAbstractItemView:enabled { background-color: #ffffff; color: #3c4043; }")
        right_layout.addWidget(self.calendar)
        splitter.addWidget(left_scroll)
        splitter.addWidget(center_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 760, 260])
        client_page_layout.addWidget(splitter)
        self.stacked_widget.addWidget(self.client_page)

        # ================= СТРАНИЦА 2: АРХИВ ЗАДАЧ =================
        self.archive_page = QWidget()
        arch_layout = QVBoxLayout(self.archive_page)
        arch_layout.setContentsMargins(20, 20, 20, 20)
        arch_header = QHBoxLayout()
        self.arch_title = QLabel("Архив задач")
        self.arch_title.setObjectName("sectionTitle")
        arch_header.addWidget(self.arch_title)
        arch_header.addStretch()
        self.btn_delete_all_arch = QPushButton("Удалить всё")
        self.btn_delete_all_arch.setObjectName("deleteBtn")
        self.btn_delete_all_arch.setCursor(Qt.PointingHandCursor)
        self.btn_delete_all_arch.clicked.connect(self.delete_all_archived)
        arch_header.addWidget(self.btn_delete_all_arch)
        self.btn_delete_selected_arch = QPushButton("Удалить выделенное")
        self.btn_delete_selected_arch.setObjectName("deleteBtn")
        self.btn_delete_selected_arch.setCursor(Qt.PointingHandCursor)
        self.btn_delete_selected_arch.clicked.connect(self.delete_selected_archived)
        arch_header.addWidget(self.btn_delete_selected_arch)
        arch_layout.addLayout(arch_header)
        self.archive_list = QListWidget()
        self.archive_list.setStyleSheet("QListWidget { border: 1px solid #dadce0; border-radius: 8px; background-color: #ffffff; } QListWidget::item { border-bottom: 1px solid #f1f3f4; padding: 0px; }")
        arch_layout.addWidget(self.archive_list)
        self.stacked_widget.addWidget(self.archive_page)

        # ================= СТРАНИЦА 3: ВСЕ КЛИЕНТЫ =================
        self.all_clients_page = QWidget()
        all_clients_layout = QVBoxLayout(self.all_clients_page)
        all_clients_layout.setContentsMargins(20, 20, 20, 20)
        ac_header = QHBoxLayout()
        self.ac_title = QLabel("Все клиенты")
        self.ac_title.setObjectName("sectionTitle")
        ac_header.addWidget(self.ac_title)
        ac_header.addStretch()
        self.btn_delete_selected_clients = QPushButton("Удалить выделенное")
        self.btn_delete_selected_clients.setObjectName("deleteBtn")
        self.btn_delete_selected_clients.setCursor(Qt.PointingHandCursor)
        self.btn_delete_selected_clients.clicked.connect(self.delete_selected_clients)
        self.btn_delete_selected_clients.hide()
        ac_header.addWidget(self.btn_delete_selected_clients)
        self.btn_archive_selected_clients = QPushButton("В архив")
        self.btn_archive_selected_clients.setObjectName("primaryBtn")
        self.btn_archive_selected_clients.setCursor(Qt.PointingHandCursor)
        self.btn_archive_selected_clients.clicked.connect(self.archive_selected_clients)
        self.btn_archive_selected_clients.hide()
        ac_header.addWidget(self.btn_archive_selected_clients)
        all_clients_layout.addLayout(ac_header)
        search_layout = QHBoxLayout()
        self.client_search_input = QLineEdit()
        self.client_search_input.setPlaceholderText("Поиск по клиентам...")
        self.client_search_input.setStyleSheet("QLineEdit { border: 1px solid #dadce0; border-radius: 4px; padding: 8px; background-color: #ffffff; font-size: 14px; } QLineEdit:focus { border: 1px solid #1a73e8; }")
        self.client_search_input.textChanged.connect(self.on_client_search)
        search_layout.addWidget(self.client_search_input)
        self.btn_clear_client_search = QPushButton("✖ Снять фильтр")
        self.btn_clear_client_search.setStyleSheet("color: #c5221f; font-weight: bold; border: none; background: transparent;")
        self.btn_clear_client_search.setCursor(Qt.PointingHandCursor)
        self.btn_clear_client_search.clicked.connect(self.clear_client_search)
        self.btn_clear_client_search.hide()
        search_layout.addWidget(self.btn_clear_client_search)
        all_clients_layout.addLayout(search_layout)
        self.all_clients_list = QListWidget()
        self.all_clients_list.setStyleSheet("QListWidget { border: 1px solid #dadce0; border-radius: 8px; background-color: #ffffff; } QListWidget::item { border-bottom: 1px solid #f1f3f4; padding: 0px; }")
        self.all_clients_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.all_clients_list.customContextMenuRequested.connect(self.show_all_clients_item_context_menu)
        all_clients_layout.addWidget(self.all_clients_list)
        pag_layout = QHBoxLayout()
        self.btn_prev_page = QPushButton("◀ Назад")
        self.btn_prev_page.clicked.connect(self.prev_clients_page)
        self.btn_next_page = QPushButton("Вперед ▶")
        self.btn_next_page.clicked.connect(self.next_clients_page)
        self.lbl_page = QLabel("Стр. 1")
        self.lbl_page.setAlignment(Qt.AlignCenter)
        pag_layout.addWidget(self.btn_prev_page)
        pag_layout.addWidget(self.lbl_page)
        pag_layout.addWidget(self.btn_next_page)
        all_clients_layout.addLayout(pag_layout)
        self.stacked_widget.addWidget(self.all_clients_page)

        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(30)
        bottom_bar.setStyleSheet("background-color: #ffffff; border-top: 1px solid #dadce0;")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(10, 0, 10, 0)
        bottom_layout.setSpacing(10)
        btn_help = QPushButton("?")
        btn_help.setFixedSize(20, 20)
        btn_help.setCursor(Qt.PointingHandCursor)
        btn_help.setStyleSheet("QPushButton { background-color: transparent; color: #888; border: 1px solid #ccc; border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0px; } QPushButton:hover { background-color: #f1f3f4; color: #333; }")
        btn_help.clicked.connect(self.show_about_dialog)
        bottom_layout.addWidget(btn_help)
        self.btn_lang = QPushButton("RU")
        self.btn_lang.setFixedSize(30, 20)
        self.btn_lang.setCursor(Qt.PointingHandCursor)
        self.btn_lang.setStyleSheet("QPushButton { background-color: transparent; color: #888; border: 1px solid #ccc; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 0px; } QPushButton:hover { background-color: #f1f3f4; color: #333; }")
        self.btn_lang.clicked.connect(self.toggle_language)
        bottom_layout.addWidget(self.btn_lang)

        # Жёлтая кнопка напоминаний
        self.btn_reminders = QPushButton("!")
        self.btn_reminders.setFixedSize(24, 20)
        self.btn_reminders.setCursor(Qt.PointingHandCursor)
        self.btn_reminders.setToolTip("Напоминания")
        self.btn_reminders.setStyleSheet(
            "QPushButton { background-color: #fbbc04; color: #202124; border: none; "
            "border-radius: 10px; font-size: 14px; font-weight: bold; padding: 0px; } "
            "QPushButton:hover { background-color: #f9ab00; }"
        )
        self.btn_reminders.clicked.connect(self.show_reminder_popup)
        self.btn_reminders.hide()
        bottom_layout.addWidget(self.btn_reminders)

        bottom_layout.addStretch()
        self.main_layout.addWidget(bottom_bar)
        self.clients_scroll.horizontalScrollBar().rangeChanged.connect(self.update_scroll_buttons)
        self.clients_scroll.horizontalScrollBar().valueChanged.connect(self.update_scroll_buttons)
        self.load_clients()
        self.build_general_calendar()
        self.show_general_view()
        QTimer.singleShot(100, self.scroll_to_current_month)

        # --- Система напоминаний ---
        self.reminder_popup = ReminderPopup(self)
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(2 * 60 * 60 * 1000)  # каждые 2 часа
        QTimer.singleShot(1500, self.check_reminders)   # первичная проверка после старта

    # ================== РАБОТА С НАПОМИНАНИЯМИ ==================

    def check_reminders(self):
        """Проверка дедлайнов активных задач + очистка старых напоминаний."""
        if self.reminder_popup is None:
            return
        now = datetime.now()
        max_past = now - timedelta(days=90)
        new_pending_created = False

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.id, t.client_id, t.title, t.deadline, t.recurrence
            FROM tasks t JOIN clients c ON t.client_id = c.id
            WHERE t.is_archived = 0 AND c.is_archived = 0 AND c.name != 'Общий'
        """)
        tasks = cursor.fetchall()

        for task_id, client_id, title, deadline_str, recurrence in tasks:
            if not deadline_str:
                continue
            try:
                d, m, y = map(int, deadline_str.split('.'))
                base = datetime(y, m, d)
            except Exception:
                continue

            occurrences = []
            if recurrence == 'none' or not recurrence:
                if max_past <= base <= now:
                    occurrences.append(base)
            else:
                current = base
                while current <= now:
                    if current >= max_past:
                        occurrences.append(current)
                    if recurrence == 'weekly':
                        current += timedelta(days=7)
                    elif recurrence == 'monthly':
                        current = add_months(current, 1)
                    elif recurrence == 'yearly':
                        current = add_months(current, 12)
                    else:
                        break

            for occ in occurrences:
                occ_str = occ.strftime("%d.%m.%Y")
                cursor.execute(
                    "SELECT id, status, snooze_until FROM reminders WHERE task_id = ? AND occurrence_date = ?",
                    (task_id, occ_str)
                )
                existing = cursor.fetchone()
                if existing:
                    rid, status, snooze_until = existing
                    if status == 'cleared':
                        continue
                    if status == 'snoozed' and snooze_until:
                        try:
                            su = datetime.strptime(snooze_until, "%d.%m.%Y %H:%M")
                            if su > now:
                                continue
                        except Exception:
                            pass
                        cursor.execute(
                            "UPDATE reminders SET status='pending', snooze_until=NULL WHERE id=?",
                            (rid,)
                        )
                else:
                    cursor.execute(
                        "INSERT INTO reminders (task_id, occurrence_date, status, snooze_until) "
                        "VALUES (?, ?, 'pending', NULL)",
                        (task_id, occ_str)
                    )
                    new_pending_created = True

        # Очистка записей старше 3 месяцев
        cutoff = now - timedelta(days=90)
        cursor.execute("SELECT id, occurrence_date FROM reminders")
        for rid, occ_str in cursor.fetchall():
            try:
                occ_date = datetime.strptime(occ_str, "%d.%m.%Y")
                if occ_date < cutoff:
                    cursor.execute("DELETE FROM reminders WHERE id = ?", (rid,))
            except Exception:
                pass

        conn.commit()
        conn.close()

        if new_pending_created:
            self.reminder_popup_dismissed = False

        self.load_active_reminders()

    def load_active_reminders(self):
        if self.reminder_popup is None:
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.task_id, t.client_id, t.title, c.name, r.occurrence_date, r.status
            FROM reminders r
            JOIN tasks t ON r.task_id = t.id
            JOIN clients c ON t.client_id = c.id
            WHERE r.status = 'pending' AND t.is_archived = 0 AND c.is_archived = 0
            ORDER BY r.occurrence_date DESC
        """)
        reminders = cursor.fetchall()
        conn.close()

        if not reminders:
            self.btn_reminders.hide()
            self.reminder_popup.hide()
            return

        self.reminder_popup.refresh(reminders)
        if self.reminder_popup_dismissed:
            self.btn_reminders.show()
            self.reminder_popup.hide()
        else:
            self.btn_reminders.hide()
            self.position_reminder_popup()
            self.reminder_popup.show()
            self.reminder_popup.raise_()

    def position_reminder_popup(self):
        if self.reminder_popup is None:
            return
        self.reminder_popup.adjustSize()
        max_h = max(200, self.height() - 130)
        if self.reminder_popup.height() > max_h:
            self.reminder_popup.resize(self.reminder_popup.width(), max_h)
        x = 15
        y = self.height() - self.reminder_popup.height() - 45
        if y < 80:
            y = 80
        self.reminder_popup.move(x, y)

    def show_reminder_popup(self):
        self.reminder_popup_dismissed = False
        self.load_active_reminders()
        self.btn_reminders.hide()

    def hide_reminder_popup(self):
        self.reminder_popup_dismissed = True
        self.load_active_reminders()

    def mark_reminder_cleared(self, reminder_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET status='cleared' WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
        self.load_active_reminders()

    def snooze_reminder(self, reminder_id):
        tomorrow = datetime.now() + timedelta(days=1)
        snooze_until = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reminders SET status='snoozed', snooze_until=? WHERE id = ?",
            (snooze_until.strftime("%d.%m.%Y %H:%M"), reminder_id)
        )
        conn.commit()
        conn.close()
        self.load_active_reminders()

    def reminder_go_to_task(self, client_id, task_id):
        self.reminder_popup_dismissed = True
        self.load_active_reminders()
        self.jump_to_task(client_id, task_id)
        self.raise_()
        self.activateWindow()

    # ================== СТАНДАРТНЫЕ МЕТОДЫ ==================

    def show_message(self, title, text, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("ОК" if self.current_lang == "RU" else "OK")
        msg_box.exec()

    def ask_confirmation(self, title, text, icon=QMessageBox.Question):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_yes = msg_box.button(QMessageBox.Yes)
        btn_no = msg_box.button(QMessageBox.No)
        btn_yes.setText("Да" if self.current_lang == "RU" else "Yes")
        btn_no.setText("Нет" if self.current_lang == "RU" else "No")
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.exec()
        return msg_box.clickedButton() == btn_yes

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scroll_buttons()
        if self.reminder_popup is not None and self.reminder_popup.isVisible():
            self.position_reminder_popup()

    def scroll_clients_left(self):
        hbar = self.clients_scroll.horizontalScrollBar()
        hbar.setValue(hbar.value() - 200)

    def scroll_clients_right(self):
        hbar = self.clients_scroll.horizontalScrollBar()
        hbar.setValue(hbar.value() + 200)

    def update_scroll_buttons(self):
        hbar = self.clients_scroll.horizontalScrollBar()
        if hbar.maximum() == 0:
            self.btn_scroll_left.hide()
            self.btn_scroll_right.hide()
        else:
            self.btn_scroll_left.show()
            self.btn_scroll_right.show()
            self.btn_scroll_left.setEnabled(hbar.value() > hbar.minimum())
            self.btn_scroll_right.setEnabled(hbar.value() < hbar.maximum())

    def changeEvent(self, event):
        if event.type() == QEvent.WindowDeactivate:
            if self.search_popup.isVisible(): self.search_popup.hide()
        super().changeEvent(event)

    def mousePressEvent(self, event):
        if self.search_popup.isVisible(): self.search_popup.hide()
        super().mousePressEvent(event)

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, title TEXT, created_at TEXT, deadline TEXT, is_important INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, date TEXT, text TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, name TEXT, description TEXT, phone1 TEXT, phone2 TEXT, phone3 TEXT, email1 TEXT, email2 TEXT, email3 TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, task_id INTEGER, post_id INTEGER, file_name TEXT, file_path TEXT, description TEXT)''')
        # Таблица напоминаний
        cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            occurrence_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            snooze_until TEXT
        )''')
        cursor.execute("PRAGMA table_info(clients)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'description' not in cols: cursor.execute("ALTER TABLE clients ADD COLUMN description TEXT")
        if 'is_pinned' not in cols: cursor.execute("ALTER TABLE clients ADD COLUMN is_pinned INTEGER DEFAULT 0")
        if 'is_archived' not in cols: cursor.execute("ALTER TABLE clients ADD COLUMN is_archived INTEGER DEFAULT 0")
        cursor.execute("PRAGMA table_info(tasks)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'is_archived' not in cols: cursor.execute("ALTER TABLE tasks ADD COLUMN is_archived INTEGER DEFAULT 0")
        if 'recurrence' not in cols: cursor.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT DEFAULT 'none'")
        cursor.execute("SELECT COUNT(*) FROM clients")
        if cursor.fetchone()[0] == 0: cursor.execute("INSERT INTO clients (name) VALUES ('Общий')")
        conn.commit()
        conn.close()

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "RU" else "RU"
        self.btn_lang.setText(self.current_lang) 
        new_locale = QLocale("en_US") if self.current_lang == "EN" else QLocale("ru_RU")
        self.calendar.setLocale(new_locale)
        self.build_general_calendar()
        self.load_general_data()
        self.retranslate_ui()

    def retranslate_ui(self):
        t = TRANSLATIONS[self.current_lang]
        self.btn_add_client.setText(t["add_client"])
        self.btn_archive.setText(t["archive_tasks"])
        self.btn_all_clients.setText(t["all_clients"])
        self.gen_tasks_title.setText(t["all_tasks"])
        self.gen_cal_title.setText(t["gen_cal"])
        self.btn_gen_today.setText(t["today"])
        self.search_input.setPlaceholderText(t["search_placeholder"])
        self.client_search_input.setPlaceholderText(t["search_clients_placeholder"])
        self.btn_clear_client_search.setText(t["clear_search"])
        self.tasks_title.setText(t["tasks"])
        self.important_title.setText(t["important"])
        self.contacts_title.setText(t["contacts"])
        self.client_files_title.setText(t["client_files"])
        self.reset_filter_btn.setText(t["reset_filter"])
        self.arch_title.setText(t["archive_title"])
        self.ac_title.setText(t["all_clients_title"])
        self.btn_delete_all_arch.setText(t["delete_all"])
        self.btn_delete_selected_arch.setText(t["delete_selected"])
        self.btn_delete_selected_clients.setText(t["delete_selected"])
        self.btn_archive_selected_clients.setText(t["to_archive"])
        if not self.current_task_id: self.task_title.setText(t["select_task"])
        self.btn_attach.setText(t["attach"])
        self.btn_send.setText(t["send"])
        self.post_input.setPlaceholderText(t["post_placeholder"])
        self.task_files_title.setText(t["task_files"])
        self.calendar_title.setText(t["calendar"])
        self.btn_today.setText(t["today"])
        if self.reminder_popup is not None:
            self.reminder_popup.update_title()
            self.btn_reminders.setToolTip(t["reminders_tooltip"])
            self.load_active_reminders()
        self.load_clients()
        self.load_archive_tasks() 
        if self.stacked_widget.currentIndex() == 1 and self.current_client_id:
            for i in range(self.clients_layout.count()):
                widget = self.clients_layout.itemAt(i).widget()
                if widget and widget.property("client_id") == self.current_client_id:
                    self.apply_client_btn_style(widget, True)
                    break
        if self.stacked_widget.currentIndex() == 3:
            self.load_all_clients()

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS[self.current_lang]["about_title"])
        dialog.resize(600, 550) 
        layout = QVBoxLayout(dialog)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        title_ru = QLabel("<h3>UlianaCRM (Ульяна СУВК)</h3>")
        text_ru = QLabel("""
        <p><b>Спроектировано:</b> Дмитрий Анохин, 2026 год.<br>
        <b>Контакты:</b> <a href="mailto:d.anokhine@yandex.ru" style="color: #1a73e8;">d.anokhine@yandex.ru</a><br>
        <b>При участии:</b> ИИ-ассистент DeepSeek (инструмент генерации кода).</p>
        <p style="color: #666; font-size: 12px;">
        <b>Конфиденциальность и локальное хранение:</b><br>
        Программа не передает персональные данные на сторонние серверы. Вся информация (база данных, файлы) хранится исключительно локально на устройстве пользователя. Автор программы не имеет технического доступа к данным и не осуществляет их сбор или обработку. Пользователь самостоятельно несёт ответственность за сохранность своих данных и обязан делать резервные копии.
        </p>
        <p style="color: #666; font-size: 12px;">
        <b>Отказ от ответственности:</b><br>
        Данное программное обеспечение предоставляется «как есть» (as is), без каких-либо гарантий, явных или подразумеваемых, включая, но не ограничиваясь, гарантиями товарной пригодности, соответствия конкретному назначению и отсутствия нарушений прав. 
        Разработчик и лица, распространяющие программу, ни при каких обстоятельствах не несут ответственности за любые прямые, косвенные, случайные, особые, штрафные или последующие убытки (включая, но не ограничиваясь, убытки от потери прибыли, прерывания деятельности, потери деловой информации или любые другие материальные убытки), возникшие в результате использования или невозможности использования данного программного обеспечения, даже если разработчик был уведомлен о возможности таких убытков. 
        Пользователь берет на себя полную ответственность за любые риски, связанные с использованием, включая, но не ограничиваясь, потерей данных или повреждением оборудования.
        </p>
        <hr>
        """)
        title_ru.setWordWrap(True)
        text_ru.setWordWrap(True)
        text_ru.setOpenExternalLinks(True)
        content_layout.addWidget(title_ru)
        content_layout.addWidget(text_ru)
        title_en = QLabel("<h3>UlianaCRM (Ulyana SUVK)</h3>")
        text_en = QLabel("""
        <p><b>Designed by:</b> Dmitry Anokhin, 2026.<br>
        <b>Contact:</b> <a href="mailto:d.anokhine@yandex.ru" style="color: #1a73e8;">d.anokhine@yandex.ru</a><br>
        <b>With the assistance of:</b> DeepSeek AI assistant (code generation tool).</p>
        <p style="color: #666; font-size: 12px;">
        <b>Privacy & Local Storage:</b><br>
        The software does not transfer personal data to third-party servers. All information (database, files) is stored exclusively locally on the user's device. The author has no technical access to the data and does not collect or process it. The user is solely responsible for the safety of their data and must create backups.
        </p>
        <p style="color: #666; font-size: 12px;">
        <b>Disclaimer:</b><br>
        THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
        IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
        The user assumes full responsibility for any risks associated with its use, including, but not limited to, data loss or hardware damage.
        </p>
        """)
        title_en.setWordWrap(True)
        text_en.setWordWrap(True)
        text_en.setOpenExternalLinks(True)
        content_layout.addWidget(title_en)
        content_layout.addWidget(text_en)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        btn_close = QPushButton("ОК" if self.current_lang == "RU" else "OK")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
        dialog.exec()

    def on_contact_search(self, text):
        search_text = text.strip()
        if not search_text:
            self.search_popup.hide()
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT c.id, c.name, cl.id, cl.name, c.phone1, c.phone2, c.phone3, c.email1, c.email2, c.email3 FROM contacts c JOIN clients cl ON c.client_id = cl.id")
        all_contacts = cursor.fetchall()
        conn.close()
        needle = search_text.lower()
        results = []
        for row in all_contacts:
            contact_id, contact_name, client_id, client_name = row[0], row[1], row[2], row[3]
            searchable = [contact_name, client_name, row[4], row[5], row[6], row[7], row[8], row[9]]
            if any(needle in (f or '').lower() for f in searchable):
                results.append((contact_id, contact_name, client_id, client_name))
                if len(results) >= 10:
                    break
        self.search_popup.clear()
        if not results:
            self.search_popup.hide()
            return
        for contact_id, contact_name, client_id, client_name in results:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, client_id)
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(15, 10, 15, 10) 
            layout.setSpacing(4) 
            lbl_name = QLabel(contact_name)
            lbl_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #202124;")
            lbl_client = QLabel(client_name)
            lbl_client.setStyleSheet("font-size: 12px; color: #5f6368;")
            layout.addWidget(lbl_name)
            layout.addWidget(lbl_client)
            item.setSizeHint(QSize(0, 70)) 
            self.search_popup.addItem(item)
            self.search_popup.setItemWidget(item, widget)
        input_pos = self.search_input.mapTo(self, QPoint(0, 0))
        row_height = 70 
        num_items = min(len(results), 5)
        popup_height = num_items * row_height + 4 
        popup_width = max(self.search_input.width(), 400)
        self.search_popup.setFixedWidth(popup_width)
        self.search_popup.setFixedHeight(popup_height)
        x = input_pos.x()
        y = input_pos.y() - popup_height - 5
        if y < 0: y = input_pos.y() + self.search_input.height() + 5
        self.search_popup.move(x, y)
        self.search_popup.raise_() 
        self.search_popup.show()

    def on_search_result_clicked(self, item):
        client_id = item.data(Qt.UserRole)
        self.search_popup.hide()
        self.search_input.clear()
        if client_id: self.select_client_and_switch(client_id)

    def show_general_view(self):
        self.stacked_widget.setCurrentIndex(0)
        self.current_client_id = None 
        self.load_general_data()
        t = TRANSLATIONS[self.current_lang]
        for i in range(self.clients_layout.count()):
            widget = self.clients_layout.itemAt(i).widget()
            if widget and widget.text() == t["general"]:
                widget.setStyleSheet("QPushButton { background-color: #e8f0fe; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; }")
            elif widget and widget.property("client_id") is not None:
                self.apply_client_btn_style(widget, False)

    def load_general_data(self):
        self.general_tasks_list.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT t.id, t.title, t.is_important, c.id, c.name, t.created_at, t.deadline, t.recurrence FROM tasks t JOIN clients c ON t.client_id = c.id WHERE c.name != 'Общий' AND c.is_archived = 0 AND t.is_archived = 0 ORDER BY (t.recurrence = 'none' OR t.recurrence IS NULL) DESC, t.id DESC")
        tasks = cursor.fetchall()
        max_date = datetime.now() + timedelta(days=365*5)
        dates_set = set()
        t_dict = TRANSLATIONS[self.current_lang]
        for task_id, title, is_important, client_id, client_name, created_at, deadline, recurrence in tasks:
            star = "⭐ " if is_important else ""
            display_title = title if len(title) < 40 else title[:40] + "..."
            recur_text = ""
            if recurrence == 'weekly': recur_text = f" ({t_dict['recur_weekly_short']})"
            elif recurrence == 'monthly': recur_text = f" ({t_dict['recur_monthly_short']})"
            elif recurrence == 'yearly': recur_text = f" ({t_dict['recur_yearly_short']})"
            item_text = f"{star}{display_title}\n📅 {created_at}  ➔  {deadline}{recur_text}\n👤 {client_name}"
            item = self.general_tasks_list.addItem(item_text)
            self.general_tasks_list.item(self.general_tasks_list.count() - 1).setData(Qt.UserRole, (task_id, client_id))
            for occ in get_all_occurrences(deadline, recurrence, max_date):
                dates_set.add(QDate(occ.year, occ.month, occ.day))
        conn.close()
        for mini_cal in self.mini_calendars: mini_cal.set_task_dates(dates_set)

    def on_general_task_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data: self.jump_to_task(data[1], data[0])

    def build_general_calendar(self):
        while self.calendar_grid_layout.count():
            item = self.calendar_grid_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
        self.mini_calendars = []
        current_date = QDate.currentDate()
        start_date = current_date.addYears(-3)
        row = 0; col = 0
        month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        month_names_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        for i in range(73):
            target_date = start_date.addMonths(i)
            year, month = target_date.year(), target_date.month()
            month_container = QWidget()
            month_layout = QVBoxLayout(month_container)
            month_layout.setContentsMargins(0, 0, 0, 0)
            month_layout.setAlignment(Qt.AlignTop)
            m_name = month_names[month-1] if self.current_lang == "RU" else month_names_en[month-1]
            title_label = QLabel(f"{m_name} {year}")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px; color: #202124;")
            month_layout.addWidget(title_label)
            mini_cal = MiniCalendar()
            mini_cal.setLocale(QLocale("en_US") if self.current_lang == "EN" else QLocale("ru_RU"))
            self.mini_calendars.append(mini_cal)
            mini_cal.setCurrentPage(year, month)
            mini_cal.setFixedHeight(180) 
            mini_cal.clicked.connect(self.on_general_calendar_clicked)
            mini_cal.setStyleSheet("QCalendarWidget QWidget { background-color: #ffffff; } QCalendarWidget QAbstractItemView:enabled { background-color: #ffffff; color: #3c4043; }")
            month_layout.addWidget(mini_cal)
            self.calendar_grid_layout.addWidget(month_container, row, col)
            if year == current_date.year() and month == current_date.month(): self.today_month_widget = month_container
            col += 1
            if col > 2: col = 0; row += 1
        self.calendar_grid_layout.setRowStretch(row + 1, 1)

    def scroll_to_current_month(self):
        if self.today_month_widget: self.general_calendar_scroll.ensureWidgetVisible(self.today_month_widget)

    def on_general_calendar_clicked(self, date):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT t.id, t.title, c.id, c.name, t.deadline, t.recurrence FROM tasks t JOIN clients c ON t.client_id = c.id WHERE c.name != 'Общий' AND c.is_archived = 0 AND t.is_archived = 0")
        all_tasks = cursor.fetchall()
        conn.close()
        matched = [ (t[0], t[1], t[2], t[3]) for t in all_tasks if is_task_on_date(t[4], t[5], date) ]
        if not matched: return 
        date_str = date.toString("dd.MM.yyyy")
        if len(matched) == 1: self.jump_to_task(matched[0][2], matched[0][0])
        else:
            items = [f"{t[1]} ({t[3]})" for t in matched]
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Выбор задачи" if self.current_lang == "RU" else "Select Task")
            dialog.setLabelText(f"На {date_str} найдено несколько задач.\nВыберите нужную:" if self.current_lang == "RU" else f"Found multiple tasks on {date_str}.\nSelect one:")
            dialog.setComboBoxItems(items)
            dialog.setOkButtonText("ОК" if self.current_lang == "RU" else "OK")
            dialog.setCancelButtonText("Отмена" if self.current_lang == "RU" else "Cancel")
            if dialog.exec() == QDialog.Accepted:
                item = dialog.textValue()
                if item:
                    idx = items.index(item)
                    self.jump_to_task(matched[idx][2], matched[idx][0])

    def jump_to_task(self, client_id, task_id):
        self.search_popup.hide() 
        self.stacked_widget.setCurrentIndex(1)
        self.select_client(client_id)
        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            if item.data(Qt.UserRole) == task_id:
                self.tasks_list.setCurrentItem(item)
                self.on_task_clicked(item)
                break

    def load_clients(self):
        while self.clients_layout.count():
            item = self.clients_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.spacerItem(): del item
        t = TRANSLATIONS[self.current_lang]
        btn_general = QPushButton(t["general"])
        btn_general.setCursor(Qt.PointingHandCursor)
        btn_general.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_general.clicked.connect(self.show_general_view)
        btn_general.setStyleSheet("QPushButton { background-color: #f1f3f4; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; } QPushButton:hover { background-color: #e8eaed; }")
        self.clients_layout.addWidget(btn_general)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, is_pinned FROM clients WHERE name != 'Общий' AND is_archived = 0 ORDER BY is_pinned DESC, id DESC")
        clients = cursor.fetchall()
        conn.close()
        for client_id, client_name, is_pinned in clients:
            display_name = (t["pinned"] if is_pinned else "") + client_name
            btn = QPushButton(display_name)
            btn.setProperty("client_id", client_id)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
            self.apply_client_btn_style(btn, False)
            btn.clicked.connect(lambda checked, cid=client_id: self.select_client_and_switch(cid))
            btn.customContextMenuRequested.connect(lambda pos, cid=client_id, cname=client_name, b=btn: self.show_client_context_menu(pos, cid, cname, b))
            self.clients_layout.addWidget(btn)
        self.clients_layout.addStretch()
        QTimer.singleShot(100, self.update_scroll_buttons)

    def select_client_and_switch(self, client_id):
        self.search_popup.hide() 
        self.stacked_widget.setCurrentIndex(1)
        self.select_client(client_id)

    def apply_client_btn_style(self, btn, is_active):
        if is_active:
            btn.setStyleSheet("QPushButton { background-color: #e8f0fe; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; } QPushButton:hover { background-color: #d2e3fc; }")
        else:
            btn.setStyleSheet("QPushButton { background-color: #f1f3f4; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; } QPushButton:hover { background-color: #e8eaed; }")

    def select_client(self, client_id):
        self.current_client_id = client_id
        self.current_task_id = None
        self.pending_post_files = []
        self.filter_date = None
        self.reset_filter_btn.hide()
        t = TRANSLATIONS[self.current_lang]
        self.btn_attach.setText(t["attach"])
        self.task_title.setText(t["select_task"])
        for i in range(self.clients_layout.count()):
            widget = self.clients_layout.itemAt(i).widget()
            if widget and widget.property("client_id") is not None:
                self.apply_client_btn_style(widget, widget.property("client_id") == client_id)
            elif widget and widget.text() == t["general"]:
                widget.setStyleSheet("QPushButton { background-color: #f1f3f4; color: #202124; font-weight: bold; border-radius: 8px; padding: 8px 16px; border: none; font-size: 13px; } QPushButton:hover { background-color: #e8eaed; }")
        self.post_input.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.btn_attach.setEnabled(False)
        self.clear_posts()
        self.load_tasks()
        self.load_contacts()
        self.load_client_files()

    def show_client_context_menu(self, pos, client_id, client_name, btn):
        menu = QMenu()
        t = TRANSLATIONS[self.current_lang]
        action_edit = menu.addAction(t["edit_client"])
        action_delete = menu.addAction(t["delete_client"])
        action = menu.exec(btn.mapToGlobal(pos))
        if action == action_edit: self.edit_client_dialog(client_id)
        elif action == action_delete: self.delete_client(client_id, client_name)

    def add_client_dialog(self):
        dialog = ClientDialog(self)
        dialog.setWindowTitle(TRANSLATIONS[self.current_lang]["add_client"])
        if dialog.exec() == QDialog.Accepted:
            name = dialog.name_input.text().strip()
            desc = dialog.desc_input.toPlainText().strip()
            is_pinned = 1 if dialog.pin_checkbox.isChecked() else 0
            if name:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO clients (name, description, is_pinned) VALUES (?, ?, ?)", (name, desc, is_pinned))
                conn.commit()
                conn.close()
                self.load_clients()
                if self.stacked_widget.currentIndex() == 3:
                    self.load_all_clients()

    def edit_client_dialog(self, client_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, is_pinned FROM clients WHERE id = ?", (client_id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            dialog = ClientDialog(self, client_data=data)
            if dialog.exec() == QDialog.Accepted:
                new_name = dialog.name_input.text().strip()
                new_desc = dialog.desc_input.toPlainText().strip()
                new_pin = 1 if dialog.pin_checkbox.isChecked() else 0
                if new_name:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE clients SET name = ?, description = ?, is_pinned = ? WHERE id = ?", (new_name, new_desc, new_pin, client_id))
                    conn.commit()
                    conn.close()
                    self.load_clients()
                    if self.stacked_widget.currentIndex() == 3:
                        self.load_all_clients()

    def delete_client(self, client_id, client_name):
        msg1 = f"Вы уверены, что хотите удалить клиента '{client_name}'?" if self.current_lang == "RU" else f"Are you sure you want to delete client '{client_name}'?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Будут удалены все задачи, контакты и файлы этого клиента.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! All tasks, contacts and files of this client will be deleted.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM files WHERE client_id = ?", (client_id,))
                for (fpath,) in cursor.fetchall():
                    if os.path.exists(fpath):
                        try: os.remove(fpath)
                        except: pass
                cursor.execute("DELETE FROM files WHERE client_id = ?", (client_id,))
                cursor.execute("DELETE FROM contacts WHERE client_id = ?", (client_id,))
                cursor.execute("SELECT id FROM tasks WHERE client_id = ?", (client_id,))
                task_ids = [row[0] for row in cursor.fetchall()]
                for tid in task_ids: cursor.execute("DELETE FROM posts WHERE task_id = ?", (tid,))
                cursor.execute("DELETE FROM tasks WHERE client_id = ?", (client_id,))
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
                conn.commit()
                conn.close()
                app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                client_dir = os.path.join(app_dir, "data_files", str(client_id))
                if os.path.exists(client_dir):
                    try: shutil.rmtree(client_dir)
                    except: pass
                self.load_clients()
                self.load_archive_tasks()
                if self.stacked_widget.currentIndex() == 3:
                    self.load_all_clients()
                else:
                    self.show_general_view()

    def load_tasks(self):
        self.tasks_list.clear()
        self.important_list.clear()
        if not self.current_client_id: return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = "SELECT id, title, created_at, deadline, is_important, recurrence FROM tasks WHERE client_id = ? AND is_archived = 0 ORDER BY (recurrence = 'none' OR recurrence IS NULL) DESC, id DESC"
        cursor.execute(query, (self.current_client_id,))
        tasks = cursor.fetchall()
        conn.close()
        max_date = datetime.now() + timedelta(days=365*5)
        dates_set = set()
        t_dict = TRANSLATIONS[self.current_lang]
        filter_qdate = QDate.fromString(self.filter_date, "dd.MM.yyyy") if self.filter_date else None
        for task_id, title, created_at, deadline, is_important, recurrence in tasks:
            display_title = title if len(title) < 30 else title[:30] + "..."
            if filter_qdate and not is_task_on_date(deadline, recurrence, filter_qdate): continue
            recur_text = ""
            if recurrence == 'weekly': recur_text = f" ({t_dict['recur_weekly_short']})"
            elif recurrence == 'monthly': recur_text = f" ({t_dict['recur_monthly_short']})"
            elif recurrence == 'yearly': recur_text = f" ({t_dict['recur_yearly_short']})"
            item_text = f"{display_title}\n📅 {created_at}  ➔  {deadline}{recur_text}"
            item = self.tasks_list.addItem(item_text)
            last_item = self.tasks_list.item(self.tasks_list.count() - 1)
            last_item.setData(Qt.UserRole, task_id)
            last_item.setData(Qt.UserRole + 1, title)
            if is_important:
                self.important_list.addItem(item_text)
                imp_item = self.important_list.item(self.important_list.count() - 1)
                imp_item.setData(Qt.UserRole, task_id)
                imp_item.setData(Qt.UserRole + 1, title)
            for occ in get_all_occurrences(deadline, recurrence, max_date):
                dates_set.add(QDate(occ.year, occ.month, occ.day))
        self.calendar.set_task_dates(dates_set)
        self.load_task_files()

    def on_calendar_clicked(self, date):
        self.filter_date = date.toString("dd.MM.yyyy")
        self.reset_filter_btn.show()
        self.load_tasks()

    def on_calendar_double_clicked(self, date):
        if not self.current_client_id:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Сначала выберите клиента!" if self.current_lang == "RU" else "Select a client first!", QMessageBox.Warning)
            return
        self.add_task_dialog(default_qdate=date)

    def go_to_today(self):
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.calendar.setCurrentPage(today.year(), today.month())

    def reset_date_filter(self):
        self.filter_date = None
        self.reset_filter_btn.hide()
        self.calendar.setSelectedDate(QDate.currentDate())
        self.load_tasks()

    def add_task_dialog(self, default_qdate=None):
        if not self.current_client_id:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Сначала выберите клиента!" if self.current_lang == "RU" else "Select a client first!", QMessageBox.Warning)
            return
        dialog = TaskDialog(self, default_qdate=default_qdate)
        dialog.setWindowTitle("Новая задача" if self.current_lang == "RU" else "New Task")
        if dialog.exec() == QDialog.Accepted:
            title = dialog.title_input.text().strip()
            deadline = dialog.deadline_input.date().toString("dd.MM.yyyy")
            recurrence = dialog.get_recurrence()
            if title:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                today = datetime.now().strftime("%d.%m.%Y")
                cursor.execute("INSERT INTO tasks (client_id, title, created_at, deadline, recurrence) VALUES (?, ?, ?, ?, ?)", (self.current_client_id, title, today, deadline, recurrence))
                conn.commit()
                conn.close()
                self.load_tasks()

    def edit_task_dialog(self, item):
        task_id = item.data(Qt.UserRole)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, deadline, recurrence FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            current_title, current_deadline, recurrence = result
            dialog = TaskDialog(self, title_text=current_title, default_qdate=QDate.fromString(current_deadline, "dd.MM.yyyy"), recurrence=recurrence)
            dialog.setWindowTitle("Редактировать задачу" if self.current_lang == "RU" else "Edit Task")
            if dialog.exec() == QDialog.Accepted:
                new_title = dialog.title_input.text().strip()
                new_deadline = dialog.deadline_input.date().toString("dd.MM.yyyy")
                new_recurrence = dialog.get_recurrence()
                if new_title:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tasks SET title = ?, deadline = ?, recurrence = ? WHERE id = ?", (new_title, new_deadline, new_recurrence, task_id))
                    conn.commit()
                    conn.close()
                    self.load_tasks()
                    if self.current_task_id == task_id: self.task_title.setText(new_title)

    def on_task_clicked(self, item):
        task_id = item.data(Qt.UserRole)
        full_task_title = item.data(Qt.UserRole + 1) 
        self.current_task_id = task_id
        self.task_title.setText(full_task_title)
        self.pending_post_files = []
        self.btn_attach.setText(TRANSLATIONS[self.current_lang]["attach"])
        self.post_input.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.btn_attach.setEnabled(True)
        self.load_posts()
        self.load_task_files()

    def show_task_context_menu(self, pos):
        widget = self.sender()
        item = widget.itemAt(pos)
        if not item: return
        task_id = item.data(Qt.UserRole)
        menu = QMenu()
        action_important = menu.addAction("⭐ Отметить как важную / Снять важность" if self.current_lang == "RU" else "⭐ Mark as important / Unmark")
        action_archive = menu.addAction(TRANSLATIONS[self.current_lang]["to_archive"])
        action = menu.exec(widget.mapToGlobal(pos))
        if action == action_important:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET is_important = 1 - is_important WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            self.load_tasks()
        elif action == action_archive: self.archive_task(task_id)

    def archive_task(self, task_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_archived = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        if self.current_task_id == task_id:
            self.current_task_id = None
            self.task_title.setText(TRANSLATIONS[self.current_lang]["select_task"])
            self.post_input.setEnabled(False)
            self.btn_send.setEnabled(False)
            self.btn_attach.setEnabled(False)
            self.clear_posts()
            self.task_files_list.clear()
        self.load_tasks()
        self.load_general_data()

    def restore_task(self, task_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_archived = 0 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        self.load_archive_tasks()
        self.load_tasks() 
        self.load_general_data()

    def show_archive_view(self):
        self.stacked_widget.setCurrentIndex(2)
        self.current_client_id = None
        self.load_archive_tasks()
        for i in range(self.clients_layout.count()):
            widget = self.clients_layout.itemAt(i).widget()
            if widget: self.apply_client_btn_style(widget, False)

    def load_archive_tasks(self):
        self.archive_list.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT t.id, t.title, c.name, t.created_at, t.deadline FROM tasks t JOIN clients c ON t.client_id = c.id WHERE t.is_archived = 1 ORDER BY t.id DESC")
        tasks = cursor.fetchall()
        conn.close()
        for task_id, title, client_name, created_at, deadline in tasks:
            item = QListWidgetItem(self.archive_list)
            w = QWidget()
            h = QHBoxLayout(w)
            h.setContentsMargins(15, 10, 15, 10) 
            h.setSpacing(15)
            cb = QCheckBox()
            cb.setProperty("task_id", task_id)
            h.addWidget(cb, alignment=Qt.AlignVCenter)
            text_container = QWidget()
            text_layout = QVBoxLayout(text_container)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2) 
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #202124;")
            lbl_title.setMinimumHeight(22)
            lbl_info = QLabel(f"👤 {client_name} | 📅 {created_at} ➔ {deadline}")
            lbl_info.setStyleSheet("color: #5f6368; font-size: 12px;")
            lbl_info.setMinimumHeight(18)
            text_layout.addWidget(lbl_title)
            text_layout.addWidget(lbl_info)
            h.addWidget(text_container, 1)
            btn = QPushButton(TRANSLATIONS[self.current_lang]["restore"])
            btn.setObjectName("primaryBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, tid=task_id: self.restore_task(tid))
            h.addWidget(btn, alignment=Qt.AlignVCenter)
            item.setSizeHint(QSize(0, 100)) 
            self.archive_list.addItem(item)
            self.archive_list.setItemWidget(item, w)

    def delete_all_archived(self):
        msg1 = "Вы уверены, что хотите удалить ВСЕ задачи из архива?" if self.current_lang == "RU" else "Are you sure you want to delete ALL tasks from the archive?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Все архивные задачи, их посты и файлы будут удалены безвозвратно.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! All archived tasks, their posts and files will be permanently deleted.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM files WHERE task_id IN (SELECT id FROM tasks WHERE is_archived = 1)")
                for (fpath,) in cursor.fetchall():
                    if os.path.exists(fpath):
                        try: os.remove(fpath)
                        except: pass
                cursor.execute("DELETE FROM files WHERE task_id IN (SELECT id FROM tasks WHERE is_archived = 1)")
                cursor.execute("DELETE FROM posts WHERE task_id IN (SELECT id FROM tasks WHERE is_archived = 1)")
                cursor.execute("SELECT id, client_id FROM tasks WHERE is_archived = 1")
                tasks_to_delete = cursor.fetchall()
                cursor.execute("DELETE FROM tasks WHERE is_archived = 1")
                conn.commit()
                conn.close()
                app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                for tid, cid in tasks_to_delete:
                    task_dir = os.path.join(app_dir, "data_files", str(cid), str(tid))
                    if os.path.exists(task_dir):
                        try: shutil.rmtree(task_dir)
                        except: pass
                self.load_archive_tasks()

    def delete_selected_archived(self):
        selected_tasks = []
        for i in range(self.archive_list.count()):
            item = self.archive_list.item(i)
            widget = self.archive_list.itemWidget(item)
            if widget:
                cb = widget.findChild(QCheckBox)
                if cb and cb.isChecked(): selected_tasks.append(cb.property("task_id"))
        if not selected_tasks:
            self.show_message("Информация" if self.current_lang == "RU" else "Info", "Не выбрано ни одной задачи." if self.current_lang == "RU" else "No tasks selected.", QMessageBox.Information)
            return
        msg1 = f"Вы уверены, что хотите удалить {len(selected_tasks)} задач(и)?" if self.current_lang == "RU" else f"Are you sure you want to delete {len(selected_tasks)} task(s)?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Выбранные задачи, их посты и файлы будут удалены безвозвратно.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! Selected tasks, their posts and files will be permanently deleted.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(selected_tasks))
                cursor.execute(f"SELECT file_path FROM files WHERE task_id IN ({placeholders})", selected_tasks)
                for (fpath,) in cursor.fetchall():
                    if os.path.exists(fpath):
                        try: os.remove(fpath)
                        except: pass
                cursor.execute(f"DELETE FROM files WHERE task_id IN ({placeholders})", selected_tasks)
                cursor.execute(f"DELETE FROM posts WHERE task_id IN ({placeholders})", selected_tasks)
                cursor.execute(f"SELECT id, client_id FROM tasks WHERE id IN ({placeholders})", selected_tasks)
                tasks_to_delete = cursor.fetchall()
                cursor.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", selected_tasks)
                conn.commit()
                conn.close()
                app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                for tid, cid in tasks_to_delete:
                    task_dir = os.path.join(app_dir, "data_files", str(cid), str(tid))
                    if os.path.exists(task_dir):
                        try: shutil.rmtree(task_dir)
                        except: pass
                self.load_archive_tasks()
    def show_all_clients_view(self):
        self.stacked_widget.setCurrentIndex(3)
        self.current_client_id = None
        self.all_clients_filter = ""
        self.client_search_input.clear()
        self.btn_clear_client_search.hide()
        self.all_clients_page_num = 1
        self.load_all_clients()
        for i in range(self.clients_layout.count()):
            widget = self.clients_layout.itemAt(i).widget()
            if widget: self.apply_client_btn_style(widget, False)

    def on_client_search(self, text):
        self.all_clients_filter = text.strip()
        self.all_clients_page_num = 1
        if self.all_clients_filter: self.btn_clear_client_search.show()
        else: self.btn_clear_client_search.hide()
        self.load_all_clients()

    def clear_client_search(self):
        self.client_search_input.clear()
        self.btn_clear_client_search.hide()
        self.all_clients_page_num = 1
        self.load_all_clients()

    def load_all_clients(self):
        self.all_clients_list.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, is_pinned, is_archived FROM clients WHERE name != 'Общий' ORDER BY is_archived ASC, is_pinned DESC, id DESC")
        all_clients = cursor.fetchall()
        conn.close()

        # Регистронезависимый поиск (работает и для кириллицы)
        if self.all_clients_filter:
            needle = self.all_clients_filter.lower()
            clients = [c for c in all_clients
                       if needle in (c[1] or '').lower()
                       or needle in (c[2] or '').lower()]
        else:
            clients = all_clients

        total_clients = len(clients)
        total_pages = max(1, (total_clients + self.all_clients_per_page - 1) // self.all_clients_per_page)
        if self.all_clients_page_num > total_pages: self.all_clients_page_num = total_pages
        offset = (self.all_clients_page_num - 1) * self.all_clients_per_page
        page_clients = clients[offset:offset + self.all_clients_per_page]

        self.lbl_page.setText(f"Стр. {self.all_clients_page_num} из {total_pages}")
        self.btn_prev_page.setEnabled(self.all_clients_page_num > 1)
        self.btn_next_page.setEnabled(self.all_clients_page_num < total_pages)

        for client_id, name, desc, is_pinned, is_archived in page_clients:
            item = QListWidgetItem(self.all_clients_list)
            w = QWidget()
            h = QHBoxLayout(w)
            h.setContentsMargins(15, 10, 15, 10)
            h.setSpacing(10)
            cb = QCheckBox()
            cb.setProperty("client_id", client_id)
            cb.stateChanged.connect(self.on_client_checkbox_changed)
            h.addWidget(cb, alignment=Qt.AlignVCenter)

            display_name = (TRANSLATIONS[self.current_lang]["pinned"] if is_pinned else "") + name
            lbl_name = QLabel(f"<b>{display_name}</b>")
            lbl_name.setStyleSheet("font-size: 14px; color: #202124;")
            lbl_name.setMinimumWidth(150)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            text_layout.addWidget(lbl_name)

            # Описание через MultiLineElidedLabel (макс. 5 строк с "...")
            if desc:
                lbl_desc = MultiLineElidedLabel(desc)
                text_layout.addWidget(lbl_desc)

            if is_archived:
                lbl_arch = QLabel(TRANSLATIONS[self.current_lang]["in_archive"])
                lbl_arch.setStyleSheet("color: #d93025; font-size: 12px; font-weight: bold;")
                text_layout.addWidget(lbl_arch)
                w.setStyleSheet("background-color: #f1f3f4;")
                cb.setEnabled(False)

            h.addLayout(text_layout, 1)

            if not is_archived:
                btn_go = QPushButton(TRANSLATIONS[self.current_lang]["go_to_client"])
                btn_go.setObjectName("primaryBtn")
                btn_go.setCursor(Qt.PointingHandCursor)
                btn_go.clicked.connect(lambda checked=False, cid=client_id: self.select_client_and_switch(cid))
                h.addWidget(btn_go, alignment=Qt.AlignVCenter)
            else:
                btn_restore = QPushButton(TRANSLATIONS[self.current_lang]["restore"])
                btn_restore.setObjectName("primaryBtn")
                btn_restore.setCursor(Qt.PointingHandCursor)
                btn_restore.clicked.connect(lambda checked=False, cid=client_id: self.restore_client(cid))
                h.addWidget(btn_restore, alignment=Qt.AlignVCenter)

            # Динамическая высота: 150px с описанием, 60px без
            item.setSizeHint(QSize(0, 150 if desc else 60))
            item.setData(Qt.UserRole, client_id)
            item.setData(Qt.UserRole + 1, is_archived)
            self.all_clients_list.addItem(item)
            self.all_clients_list.setItemWidget(item, w)

    def show_all_clients_item_context_menu(self, pos):
        item = self.all_clients_list.itemAt(pos)
        if not item:
            return
        widget = self.all_clients_list.itemWidget(item)
        if not widget:
            return
        # Проверка чекбокса: если клик пришёлся на него — меню не показываем
        cb = widget.findChild(QCheckBox)
        if cb and cb.isEnabled():
            cb_rect = cb.rect()
            cb_rect.moveTopLeft(cb.mapTo(self.all_clients_list.viewport(), QPoint(0, 0)))
            if cb_rect.contains(pos):
                return
        client_id = item.data(Qt.UserRole)
        is_archived = item.data(Qt.UserRole + 1)
        if client_id is None:
            return
        menu = QMenu()
        t = TRANSLATIONS[self.current_lang]
        action_edit = menu.addAction(t["edit_client"])
        action_delete = None
        if not is_archived:
            menu.addSeparator()
            action_delete = menu.addAction(t["delete_client"])
        action = menu.exec(self.all_clients_list.mapToGlobal(pos))
        if action == action_edit:
            self.edit_client_dialog(client_id)
        elif action_delete is not None and action == action_delete:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.delete_client(client_id, row[0])

    def on_client_checkbox_changed(self):
        any_checked = False
        for i in range(self.all_clients_list.count()):
            item = self.all_clients_list.item(i)
            widget = self.all_clients_list.itemWidget(item)
            if widget:
                cb = widget.findChild(QCheckBox)
                if cb and cb.isChecked():
                    any_checked = True
                    break
        if any_checked:
            self.btn_delete_selected_clients.show()
            self.btn_archive_selected_clients.show()
        else:
            self.btn_delete_selected_clients.hide()
            self.btn_archive_selected_clients.hide()

    def prev_clients_page(self):
        if self.all_clients_page_num > 1:
            self.all_clients_page_num -= 1
            self.load_all_clients()

    def next_clients_page(self):
        self.all_clients_page_num += 1
        self.load_all_clients()

    def archive_selected_clients(self):
        selected = []
        for i in range(self.all_clients_list.count()):
            item = self.all_clients_list.item(i)
            widget = self.all_clients_list.itemWidget(item)
            if widget:
                cb = widget.findChild(QCheckBox)
                if cb and cb.isChecked(): selected.append(cb.property("client_id"))
        if not selected: return
        msg1 = f"Вы уверены, что хотите переместить {len(selected)} клиентов в архив?" if self.current_lang == "RU" else f"Are you sure you want to archive {len(selected)} client(s)?"
        if self.ask_confirmation('Архивация' if self.current_lang == "RU" else 'Archive', msg1, QMessageBox.Question):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            placeholders = ','.join(['?'] * len(selected))
            cursor.execute(f"UPDATE clients SET is_archived = 1 WHERE id IN ({placeholders})", selected)
            conn.commit()
            conn.close()
            self.btn_delete_selected_clients.hide()
            self.btn_archive_selected_clients.hide()
            self.load_all_clients()
            self.load_clients()
            self.load_general_data()

    def restore_client(self, client_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE clients SET is_archived = 0 WHERE id = ?", (client_id,))
        conn.commit()
        conn.close()
        self.load_all_clients()
        self.load_clients()
        self.load_general_data()

    def delete_selected_clients(self):
        selected = []
        for i in range(self.all_clients_list.count()):
            item = self.all_clients_list.item(i)
            widget = self.all_clients_list.itemWidget(item)
            if widget:
                cb = widget.findChild(QCheckBox)
                if cb and cb.isChecked(): selected.append(cb.property("client_id"))
        if not selected: return
        msg1 = f"Вы уверены, что хотите БЕЗВОЗВРАТНО удалить {len(selected)} клиентов?" if self.current_lang == "RU" else f"Are you sure you want to PERMANENTLY delete {len(selected)} client(s)?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Все их задачи, контакты и файлы будут удалены навсегда.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! All their tasks, contacts and files will be permanently deleted.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                for cid in selected:
                    cursor.execute("SELECT file_path FROM files WHERE client_id = ?", (cid,))
                    for (fpath,) in cursor.fetchall():
                        if os.path.exists(fpath):
                            try: os.remove(fpath)
                            except: pass
                    cursor.execute("DELETE FROM files WHERE client_id = ?", (cid,))
                    cursor.execute("DELETE FROM contacts WHERE client_id = ?", (cid,))
                    cursor.execute("SELECT id FROM tasks WHERE client_id = ?", (cid,))
                    task_ids = [row[0] for row in cursor.fetchall()]
                    for tid in task_ids: cursor.execute("DELETE FROM posts WHERE task_id = ?", (tid,))
                    cursor.execute("DELETE FROM tasks WHERE client_id = ?", (cid,))
                    cursor.execute("DELETE FROM clients WHERE id = ?", (cid,))
                    client_dir = os.path.join(app_dir, "data_files", str(cid))
                    if os.path.exists(client_dir):
                        try: shutil.rmtree(client_dir)
                        except: pass
                conn.commit()
                conn.close()
                self.btn_delete_selected_clients.hide()
                self.btn_archive_selected_clients.hide()
                self.load_all_clients()
                self.load_clients()
                self.load_general_data()

    def load_contacts(self):
        self.contacts_list.clear()
        if not self.current_client_id: return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM contacts WHERE client_id = ? ORDER BY name", (self.current_client_id,))
        contacts = cursor.fetchall()
        conn.close()
        for contact_id, name, desc in contacts:
            short_desc = desc if desc else ""
            if len(short_desc) > 40: short_desc = short_desc[:40] + "..."
            item_text = f"👤  {name}"
            if short_desc: item_text += f"\n{short_desc}"
            item = self.contacts_list.addItem(item_text)
            self.contacts_list.item(self.contacts_list.count() - 1).setData(Qt.UserRole, contact_id)

    def add_contact_dialog(self):
        if not self.current_client_id:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Сначала выберите клиента!" if self.current_lang == "RU" else "Select a client first!", QMessageBox.Warning)
            return
        dialog = ContactDialog(self)
        dialog.setWindowTitle("Новый контакт" if self.current_lang == "RU" else "New Contact")
        if dialog.exec() == QDialog.Accepted:
            name = dialog.name_input.text().strip()
            if not name:
                self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Поле 'Имя' обязательно для заполнения!" if self.current_lang == "RU" else "Name field is required!", QMessageBox.Warning)
                return
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO contacts (client_id, name, description, phone1, phone2, phone3, email1, email2, email3) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (self.current_client_id, name, dialog.desc_input.toPlainText().strip(),
                            dialog.phone1.text().strip(), dialog.phone2.text().strip(), dialog.phone3.text().strip(),
                            dialog.email1.text().strip(), dialog.email2.text().strip(), dialog.email3.text().strip()))
            conn.commit()
            conn.close()
            self.load_contacts()

    def edit_contact_dialog(self, item):
        contact_id = item.data(Qt.UserRole)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, description, phone1, phone2, phone3, email1, email2, email3 FROM contacts WHERE id = ?", (contact_id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            dialog = ContactDialog(self, contact_data=data)
            dialog.setWindowTitle("Редактировать контакт" if self.current_lang == "RU" else "Edit Contact")
            if dialog.exec() == QDialog.Accepted:
                new_name = dialog.name_input.text().strip()
                if not new_name:
                    self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Поле 'Имя' обязательно для заполнения!" if self.current_lang == "RU" else "Name field is required!", QMessageBox.Warning)
                    return
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''UPDATE contacts SET name=?, description=?, phone1=?, phone2=?, phone3=?, email1=?, email2=?, email3=? 
                                  WHERE id = ?''', 
                               (new_name, dialog.desc_input.toPlainText().strip(),
                                dialog.phone1.text().strip(), dialog.phone2.text().strip(), dialog.phone3.text().strip(),
                                dialog.email1.text().strip(), dialog.email2.text().strip(), dialog.email3.text().strip(),
                                contact_id))
                conn.commit()
                conn.close()
                self.load_contacts()

    def show_contact_context_menu(self, pos):
        widget = self.sender()
        item = widget.itemAt(pos)
        if not item: return
        contact_id = item.data(Qt.UserRole)
        contact_name = item.text().split('\n')[0].replace("👤", "").strip()
        menu = QMenu()
        action_delete = menu.addAction(f"❌ Удалить контакт '{contact_name}'" if self.current_lang == "RU" else f"❌ Delete contact '{contact_name}'")
        action = menu.exec(widget.mapToGlobal(pos))
        if action == action_delete: self.delete_contact(contact_id, contact_name)

    def delete_contact(self, contact_id, contact_name):
        msg1 = f"Вы уверены, что хотите удалить контакт '{contact_name}'?" if self.current_lang == "RU" else f"Are you sure you want to delete contact '{contact_name}'?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Данные контакта будут удалены навсегда.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! Contact data will be permanently deleted.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
                conn.commit()
                conn.close()
                self.load_contacts()

    def add_client_file(self):
        if not self.current_client_id:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Сначала выберите клиента!" if self.current_lang == "RU" else "Select a client first!", QMessageBox.Warning)
            return
        title_dialog = "Выберите файл для прикрепления к клиенту" if self.current_lang == "RU" else "Select file to attach to client"
        file_path, _ = QFileDialog.getOpenFileName(self, title_dialog)
        if not file_path: return
        title_desc = "Описание файла" if self.current_lang == "RU" else "File description"
        label_desc = "Введите описание (необязательно):" if self.current_lang == "RU" else "Enter description (optional):"
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title_desc)
        dialog.setLabelText(label_desc)
        dialog.setOkButtonText("ОК" if self.current_lang == "RU" else "OK")
        dialog.setCancelButtonText("Отмена" if self.current_lang == "RU" else "Cancel")
        if dialog.exec() != QDialog.Accepted: return
        description = dialog.textValue()
        app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(app_dir, "data_files", str(self.current_client_id), "general")
        os.makedirs(base_dir, exist_ok=True)
        orig_name = os.path.basename(file_path)
        dest_path = os.path.join(base_dir, orig_name)
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(orig_name)
            dest_path = os.path.join(base_dir, f"{name}_{int(datetime.now().timestamp())}{ext}")
        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", f"Не удалось скопировать файл:\n{e}" if self.current_lang == "RU" else f"Failed to copy file:\n{e}", QMessageBox.Critical)
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (client_id, task_id, post_id, file_name, file_path, description) VALUES (?, ?, ?, ?, ?, ?)",
                       (self.current_client_id, None, None, orig_name, dest_path, description))
        conn.commit()
        conn.close()
        self.load_client_files()

    def add_task_file(self):
        if not self.current_task_id:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Сначала выберите задачу!" if self.current_lang == "RU" else "Select a task first!", QMessageBox.Warning)
            return
        title_dialog = "Выберите файл для прикрепления" if self.current_lang == "RU" else "Select file to attach"
        file_path, _ = QFileDialog.getOpenFileName(self, title_dialog)
        if not file_path: return
        title_desc = "Описание файла" if self.current_lang == "RU" else "File description"
        label_desc = "Введите описание (необязательно):" if self.current_lang == "RU" else "Enter description (optional):"
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title_desc)
        dialog.setLabelText(label_desc)
        dialog.setOkButtonText("ОК" if self.current_lang == "RU" else "OK")
        dialog.setCancelButtonText("Отмена" if self.current_lang == "RU" else "Cancel")
        if dialog.exec() != QDialog.Accepted: return
        description = dialog.textValue()
        app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(app_dir, "data_files", str(self.current_client_id), str(self.current_task_id))
        os.makedirs(base_dir, exist_ok=True)
        orig_name = os.path.basename(file_path)
        dest_path = os.path.join(base_dir, orig_name)
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(orig_name)
            dest_path = os.path.join(base_dir, f"{name}_{int(datetime.now().timestamp())}{ext}")
        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            self.show_message("Ошибка" if self.current_lang == "RU" else "Error", f"Не удалось скопировать файл:\n{e}" if self.current_lang == "RU" else f"Failed to copy file:\n{e}", QMessageBox.Critical)
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (client_id, task_id, post_id, file_name, file_path, description) VALUES (?, ?, ?, ?, ?, ?)",
                       (self.current_client_id, self.current_task_id, None, orig_name, dest_path, description))
        conn.commit()
        conn.close()
        self.load_task_files()
        self.load_client_files()

    def load_task_files(self):
        self.task_files_list.clear()
        if not self.current_task_id: return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_name, file_path, description FROM files WHERE task_id = ? ORDER BY id DESC", (self.current_task_id,))
        files = cursor.fetchall()
        conn.close()
        for file_id, name, path, desc in files:
            item_text = f"📄 {name}"
            if desc: item_text += f"\n{desc}"
            item = self.task_files_list.addItem(item_text)
            self.task_files_list.item(self.task_files_list.count() - 1).setData(Qt.UserRole, file_id)
            self.task_files_list.item(self.task_files_list.count() - 1).setData(Qt.UserRole + 1, path)

    def load_client_files(self):
        self.client_files_list.clear()
        if not self.current_client_id: return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_name, file_path, description FROM files WHERE client_id = ? ORDER BY id DESC", (self.current_client_id,))
        files = cursor.fetchall()
        conn.close()
        for file_id, name, path, desc in files:
            item_text = f"📄 {name}"
            if desc: item_text += f"\n{desc}"
            item = self.client_files_list.addItem(item_text)
            self.client_files_list.item(self.client_files_list.count() - 1).setData(Qt.UserRole, file_id)
            self.client_files_list.item(self.client_files_list.count() - 1).setData(Qt.UserRole + 1, path)

    def show_file_context_menu(self, pos):
        widget = self.sender()
        item = widget.itemAt(pos)
        if not item: return
        file_id = item.data(Qt.UserRole)
        file_path = item.data(Qt.UserRole + 1)
        menu = QMenu()
        action_open = menu.addAction("📂 Открыть" if self.current_lang == "RU" else "📂 Open")
        action_save = menu.addAction("💾 Сохранить как..." if self.current_lang == "RU" else "💾 Save as...")
        menu.addSeparator()
        action_delete = menu.addAction("❌ Удалить файл" if self.current_lang == "RU" else "❌ Delete file")
        action = menu.exec(widget.mapToGlobal(pos))
        if action == action_open:
            if os.path.exists(file_path):
                try: os.startfile(file_path)
                except Exception as e: self.show_message("Ошибка" if self.current_lang == "RU" else "Error", f"Не удалось открыть файл:\n{e}" if self.current_lang == "RU" else f"Failed to open file:\n{e}", QMessageBox.Warning)
            else: self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Файл не найден на диске!" if self.current_lang == "RU" else "File not found on disk!", QMessageBox.Warning)
        elif action == action_save:
            if os.path.exists(file_path):
                title_save = "Сохранить файл как" if self.current_lang == "RU" else "Save file as"
                save_path, _ = QFileDialog.getSaveFileName(self, title_save, os.path.basename(file_path))
                if save_path:
                    try: shutil.copy2(file_path, save_path)
                    except Exception as e: self.show_message("Ошибка" if self.current_lang == "RU" else "Error", f"Не удалось сохранить файл:\n{e}" if self.current_lang == "RU" else f"Failed to save file:\n{e}", QMessageBox.Critical)
            else: self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Файл не найден на диске!" if self.current_lang == "RU" else "File not found on disk!", QMessageBox.Warning)
        elif action == action_delete: self.delete_file(file_id, file_path)

    def delete_file(self, file_id, file_path):
        msg1 = "Вы уверены, что хотите удалить этот файл?" if self.current_lang == "RU" else "Are you sure you want to delete this file?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Файл будет удален с диска безвозвратно.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! The file will be permanently deleted from disk.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
                conn.commit()
                conn.close()
                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass
                self.load_task_files()
                self.load_client_files()
                self.load_posts() 

    def clear_posts(self):
        while self.posts_layout.count():
            item = self.posts_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
            else: del item

    def load_posts(self):
        self.clear_posts()
        if not self.current_task_id:
            self.posts_layout.addStretch()
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, text FROM posts WHERE task_id = ? ORDER BY id DESC", (self.current_task_id,))
        posts = cursor.fetchall()
        conn.close()
        for post_id, date_str, text in posts:
            post_frame = QFrame() 
            post_frame.setObjectName("postCard")
            post_frame.setAttribute(Qt.WA_StyledBackground, True) 
            post_frame.setStyleSheet("QFrame#postCard { background-color: #ffffff; border: 1px solid #dadce0; border-radius: 8px; }")
            layout = QVBoxLayout(post_frame)
            layout.setContentsMargins(15, 15, 15, 15)
            date_label = QLabel(date_str)
            date_label.setStyleSheet("color: #5f6368; font-size: 12px; font-weight: bold;")
            layout.addWidget(date_label)
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred) 
            text_label.setStyleSheet("font-size: 14px; margin-top: 5px;")
            layout.addWidget(text_label)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, file_name, file_path FROM files WHERE post_id = ?", (post_id,))
            post_files = cursor.fetchall()
            conn.close()
            if post_files:
                files_layout = QGridLayout()
                files_layout.setContentsMargins(0, 10, 0, 0)
                files_layout.setSpacing(5)
                for index, (f_id, f_name, f_path) in enumerate(post_files):
                    display_name = f_name if len(f_name) <= 30 else f_name[:27] + "..."
                    btn_file = QPushButton(f"📎 {display_name}")
                    btn_file.setToolTip(f_name)
                    btn_file.setStyleSheet("color: #1a73e8; background: transparent; border: none; text-align: left; text-decoration: underline; padding: 2px;")
                    btn_file.setCursor(Qt.PointingHandCursor)
                    btn_file.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred) 
                    btn_file.clicked.connect(lambda checked, p=f_path: self.open_file(p))
                    row, col = index // 2, index % 2
                    files_layout.addWidget(btn_file, row, col)
                files_layout.setColumnStretch(0, 1)
                files_layout.setColumnStretch(1, 1)
                layout.addLayout(files_layout)
            btn_del = QPushButton("Удалить" if self.current_lang == "RU" else "Delete")
            btn_del.setObjectName("deleteBtn")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda checked, pid=post_id: self.delete_post(pid))
            layout.addWidget(btn_del, alignment=Qt.AlignRight)
            self.posts_layout.addWidget(post_frame)
        self.posts_layout.addStretch()

    def open_file(self, path):
        if os.path.exists(path):
            try: os.startfile(path)
            except Exception as e: self.show_message("Ошибка" if self.current_lang == "RU" else "Error", f"Не удалось открыть файл:\n{e}" if self.current_lang == "RU" else f"Failed to open file:\n{e}", QMessageBox.Warning)
        else: self.show_message("Ошибка" if self.current_lang == "RU" else "Error", "Файл не найден на диске!" if self.current_lang == "RU" else "File not found on disk!", QMessageBox.Warning)

    def attach_files_to_post(self):
        if not self.current_task_id: return
        title_dialog = "Выберите файлы для прикрепления к посту" if self.current_lang == "RU" else "Select files to attach to post"
        file_paths, _ = QFileDialog.getOpenFileNames(self, title_dialog)
        if file_paths:
            self.pending_post_files.extend(file_paths)
            if self.current_lang == "RU": self.btn_attach.setText(f"📎 Прикреплено файлов: {len(self.pending_post_files)}")
            else: self.btn_attach.setText(f"📎 Files attached: {len(self.pending_post_files)}")

    def send_post(self):
        if not self.current_task_id: return
        text = self.post_input.toPlainText().strip()
        if not text and not self.pending_post_files: return
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (task_id, date, text) VALUES (?, ?, ?)", (self.current_task_id, date_str, text))
        post_id = cursor.lastrowid
        app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(app_dir, "data_files", str(self.current_client_id), str(self.current_task_id))
        os.makedirs(base_dir, exist_ok=True)
        for file_path in self.pending_post_files:
            orig_name = os.path.basename(file_path)
            dest_path = os.path.join(base_dir, orig_name)
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(orig_name)
                dest_path = os.path.join(base_dir, f"{name}_{int(datetime.now().timestamp())}{ext}")
            try:
                shutil.copy2(file_path, dest_path)
                cursor.execute("INSERT INTO files (client_id, task_id, post_id, file_name, file_path, description) VALUES (?, ?, ?, ?, ?, ?)",
                               (self.current_client_id, self.current_task_id, post_id, orig_name, dest_path, ""))
            except Exception as e: print(f"Error copying {orig_name}: {e}")
        conn.commit()
        conn.close()
        self.post_input.clear()
        self.pending_post_files = []
        self.btn_attach.setText(TRANSLATIONS[self.current_lang]["attach"])
        self.load_posts()
        self.load_task_files()
        self.load_client_files()

    def delete_post(self, post_id):
        msg1 = "Вы уверены, что хотите удалить этот пост?" if self.current_lang == "RU" else "Are you sure you want to delete this post?"
        if self.ask_confirmation('Удаление' if self.current_lang == "RU" else 'Delete', msg1, QMessageBox.Question):
            msg2 = "ВНИМАНИЕ! Если к посту были прикреплены файлы, они тоже будут удалены.\nТочно продолжить?" if self.current_lang == "RU" else "WARNING! If files were attached to the post, they will also be deleted.\nProceed?"
            if self.ask_confirmation('ВНИМАНИЕ!' if self.current_lang == "RU" else 'WARNING!', msg2, QMessageBox.Warning):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM files WHERE post_id = ?", (post_id,))
                for (fpath,) in cursor.fetchall():
                    if os.path.exists(fpath):
                        try: os.remove(fpath)
                        except: pass
                cursor.execute("DELETE FROM files WHERE post_id = ?", (post_id,))
                cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                conn.commit()
                conn.close()
                self.load_posts()
                self.load_task_files()
                self.load_client_files()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(get_resource_path("app.ico")))
    app.setStyleSheet("""
        QWidget { font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 13px; color: #3c4043; }
        #leftPanel { background-color: #f8f9fa; border: none; }
        #centerPanel, #rightPanel { background-color: #ffffff; }
        #topPanel { background-color: #ffffff; }
        QPushButton { background-color: transparent; border: 1px solid transparent; border-radius: 18px; padding: 8px 16px; font-weight: 500; color: #3c4043; }
        QPushButton:hover { background-color: #f1f3f4; }
        #primaryBtn { background-color: #1a73e8; color: #ffffff; border-radius: 4px; padding: 8px 24px; font-weight: bold; }
        #primaryBtn:hover { background-color: #1557b0; }
        #primaryBtn:disabled { background-color: #dadce0; color: #80868b; }
        #deleteBtn { background-color: #fce8e6; color: #c5221f; border-radius: 4px; padding: 4px 12px; }
        #deleteBtn:hover { background-color: #fad2cf; }
        #iconBtn { border-radius: 12px; padding: 2px 8px; font-size: 18px; color: #5f6368; }
        #textBtn { color: #1a73e8; background-color: transparent; border: none; text-align: left; padding: 5px; }
        #textBtn:hover { background-color: #f1f3f4; }
        #sectionTitle { font-size: 15px; font-weight: bold; color: #202124; padding-top: 5px; }
        QListWidget { border: none; background-color: transparent; outline: none; }
        QListWidget::item { padding: 8px; border-radius: 4px; color: #3c4043; }
        QListWidget::item:hover { background-color: #f1f3f4; }
        QListWidget::item:selected { background-color: #e8f0fe; color: #1967d2; }
        #activeTaskTitle { background-color: #e8f0fe; color: #202124; padding: 12px; border-radius: 6px; font-size: 13px; font-weight: bold; }
        #postInput { border: 1px solid #dadce0; border-radius: 8px; background-color: #f8f9fa; padding: 10px; font-size: 14px; }
        #postInput:focus { background-color: #ffffff; border: 1px solid #1a73e8; }
        #postInput:disabled { background-color: #f1f3f4; border: 1px solid #e8eaed; }
        QLineEdit, QTextEdit, QDateEdit { border: 1px solid #dadce0; border-radius: 4px; padding: 5px; background-color: #ffffff; }
        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus { border: 1px solid #1a73e8; }
        QScrollBar:vertical { border: none; background: transparent; width: 10px; margin: 0px; }
        QScrollBar::handle:vertical { background: #dadce0; min-height: 20px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #bdc1c6; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """)
    window = MainWindow()
    window.showMaximized() 
    sys.exit(app.exec())
