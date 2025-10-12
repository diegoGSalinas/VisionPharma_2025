import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

# Ajuste de ruta: VisionPharma_2025/src/data/
LOG_FILE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'data', 'inspection_logs.json'
))

class LocalStorage:
    """Maneja el almacenamiento y recuperación de registros de inspección usando JSON local."""

    def __init__(self):
        self._ensure_file_integrity()

    def _ensure_file_integrity(self):
        """Verifica la existencia del archivo de logs y lo inicializa si es necesario."""
        log_dir = os.path.dirname(LOG_FILE_PATH)
        os.makedirs(log_dir, exist_ok=True)
        
        if not os.path.exists(LOG_FILE_PATH) or os.path.getsize(LOG_FILE_PATH) == 0:
            with open(LOG_FILE_PATH, 'w') as f:
                json.dump([], f)
            print(f"INFO: Archivo de logs local creado en: {LOG_FILE_PATH}")

    def _read_all_logs(self) -> List[Dict[str, Any]]:
        """Lee todos los registros guardados en el archivo JSON."""
        try:
            with open(LOG_FILE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_inspection_batch(self, results: List[Dict[str, Any]]):
        """
        Guarda los resultados de un lote (frame) de inspección en el archivo JSON.
        """
        batch_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        new_records = []
        
        for result in results:
            status = 'DEFECTO' if result['status'] != 'Aprobado' else 'OK'
            defect_type = result['status'] if result['status'] != 'Aprobado' else 'N/A'
            
            new_records.append({
                'batch_id': batch_id,
                'timestamp': timestamp,
                'contour_id': result['id'],
                'area_px': result['area'],
                'circularity': result['circularity'],
                'status': status,
                'defect_type': defect_type
            })

        all_logs = self._read_all_logs()
        all_logs.extend(new_records)

        try:
            with open(LOG_FILE_PATH, 'w') as f:
                json.dump(all_logs, f, indent=4)
            print(f"INFO: Lote de inspección '{batch_id}' guardado ({len(results)} registros).")
        except Exception as e:
            print(f"ERROR: No se pudo escribir en el archivo JSON: {e}")
            
    def get_all_records(self) -> List[Dict[str, Any]]:
        """Función utilitaria para el Dashboard."""
        return self._read_all_logs()