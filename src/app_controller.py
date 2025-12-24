import os
import shutil
from concurrent.futures import ThreadPoolExecutor

# Import your existing modules
# Assuming ingestion logic exists or we wrap it here
from src.ingestion.ingestor import ingest_pdf
from src.graph.graph import app as rag_graph


class AppController:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.upload_dir = "data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def submit_query(self, query, callback):
        """Runs the LangGraph pipeline in a background thread."""

        def task():
            try:
                result = rag_graph.invoke({"query": query})
                return result.get("answer", "No answer generated.")
            except Exception as e:
                return f"Error: {str(e)}"

        future = self.executor.submit(task)
        future.add_done_callback(lambda f: callback(f.result()))

    def upload_file(self, file_path, callback):
        """Copies file and triggers ingestion."""

        def task():
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.upload_dir, filename)
                shutil.copy(file_path, dest_path)

                # Trigger your ingestion logic here
                ingest_pdf(dest_path)

                return f"Successfully ingested: {filename}"
            except Exception as e:
                return f"Upload Failed: {str(e)}"

        future = self.executor.submit(task)
        future.add_done_callback(lambda f: callback(f.result()))