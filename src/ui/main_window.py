import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFileDialog, QListWidget,
    QTabWidget, QProgressBar
)
from PyQt5.QtGui import QFontDatabase  # ✅ REQUIRED
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from src.app_controller import AppController
from qt_material import apply_stylesheet


# Signal helper to update UI from background threads safely
class WorkerSignals(QObject):
    update_chat = pyqtSignal(str, str)  # sender, message
    update_status = pyqtSignal(str)


class RAGApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = AppController()
        self.signals = WorkerSignals()

        # Connect signals
        self.signals.update_chat.connect(self.append_message)
        self.signals.update_status.connect(self.update_status_label)

        self.setWindowTitle("RAG Knowledge Assistant")
        self.setGeometry(100, 100, 900, 700)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_chat_tab(), "💬 Chat")
        tabs.addTab(self.create_kb_tab(), "📂 Knowledge Base")
        layout.addWidget(tabs)

        # Status Bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def create_chat_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Chat History
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask a question about your documents...")
        self.input_field.returnPressed.connect(self.handle_send)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.handle_send)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

        return tab

    def create_kb_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("<h2>Upload Documents</h2>"))
        layout.addWidget(QLabel("Add PDFs to the knowledge base here."))

        # Upload Button
        upload_btn = QPushButton("Select PDF")
        upload_btn.clicked.connect(self.handle_upload)
        layout.addWidget(upload_btn)

        # Ingestion Progress (Visual only for now)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Log area
        self.log_display = QListWidget()
        layout.addWidget(self.log_display)

        return tab

    # --- Logic ---

    def handle_send(self):
        query = self.input_field.text().strip()
        if not query:
            return

        self.append_message("You", query)
        self.input_field.clear()
        self.status_label.setText("Thinking...")

        # Call backend
        self.controller.submit_query(query, self.on_query_complete)

    def on_query_complete(self, answer):
        self.signals.update_chat.emit("Bot", answer)
        self.signals.update_status.emit("Ready")

    def append_message(self, sender, text):
        color = "#4caf50" if sender == "Bot" else "#2196f3"
        formatted = f'<div style="margin-bottom: 10px;"><b><span style="color:{color};">{sender}:</span></b><br>{text}</div>'
        self.chat_display.append(formatted)
        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_display.setTextCursor(cursor)

    def update_status_label(self, text):
        self.status_label.setText(text)

    def handle_upload(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open PDF', '/home', "PDF Files (*.pdf)")
        if fname:
            self.log_display.addItem(f"Uploading: {fname}...")
            self.progress.setValue(20)
            self.status_label.setText("Ingesting...")
            self.controller.upload_file(fname, self.on_upload_complete)

    def on_upload_complete(self, message):
        self.log_display.addItem(message)
        self.progress.setValue(100)
        self.signals.update_status.emit("Ready")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply a modern dark theme
    apply_stylesheet(app, theme='dark_teal.xml')

    window = RAGApp()
    window.show()
    sys.exit(app.exec_())