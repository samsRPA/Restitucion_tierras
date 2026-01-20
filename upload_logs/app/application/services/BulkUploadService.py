

import concurrent
from pathlib import Path
import shutil
from app.domain.interfaces.IBulkUploadService import IBulkUploadService

import os
import json

import math  
import logging
import datetime
from app.domain.interfaces.IS3Manager import IS3Manager



class BulkUploadService(IBulkUploadService):

    def __init__(self, s3_manager: IS3Manager):
        self.s3_manager = s3_manager
        self.logger = logging.getLogger(__name__)


    def upload_folders(self, base_path: str) -> None:
        self.logger.info(f"🚀 Iniciando subida de capturas")
        self.upload_capturas_folder( base_path)
        self.upload_logs_folder(base_path)


        self.limpiar_output(base_path)
    
        
        




    def upload_capturas_folder(self, base_path) -> None:
        """
        Sube recursivamente todos los archivos dentro de base_path/capturas a S3
        de forma concurrente, preservando toda la estructura de carpetas.
        Ignora la carpeta correspondiente a la fecha actual (ej: 03-11-2025).
        Una vez subida una carpeta completa, la elimina localmente.
        """
        base_path = str(base_path)
        capturas_path = os.path.join(base_path, "img/estados")

        if not os.path.exists(capturas_path):
            self.logger.error(f"La ruta {capturas_path} no existe.")
            return
        
        self.logger.info(f"🚀 Iniciando subida recursiva (paralela) de carpeta: {capturas_path}")

        hoy = datetime.datetime.now().strftime("%d-%m-%Y")

        # Recolectar todos los archivos a subir (excepto los de la fecha actual)
        upload_tasks = []
        for root, _, files in os.walk(capturas_path):
           
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_path)
                s3_key = f"{self.s3_manager.prefix}/{relative_path}".replace("\\", "/")
                upload_tasks.append((file_path, s3_key))

        total_files = len(upload_tasks)
        if total_files == 0:
            self.logger.info(f"📁 No hay archivos para subir (todas las carpetas corresponden al {hoy}).")
            return

        self.logger.info(f"📦 Total de archivos a subir (excluyendo {hoy}): {total_files}")

        # Subida concurrente con ThreadPoolExecutor
        uploaded_success = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            future_to_file = {
                executor.submit(self.s3_manager.uploadFile, f, k): (f, k)
                for f, k in upload_tasks
            }

            for future in concurrent.futures.as_completed(future_to_file):
                file_path, s3_key = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        self.logger.info(f"✅ Subido correctamente: {file_path}")
                        uploaded_success.append(file_path)
                    else:
                        self.logger.error(f"❌ Falló la subida: {file_path}")
                except Exception as e:
                    self.logger.error(f"💥 Error inesperado subiendo {file_path}: {e}")

        self.logger.info("🎯 Subida completa de todos los archivos de 'capturas' (excepto la fecha actual).")

        # Eliminar carpetas subidas (excepto la del día actual)
        self.logger.info("🧹 Limpiando carpetas subidas...")
        for root, dirs, _ in os.walk(capturas_path, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    shutil.rmtree(dir_path)
                    self.logger.info(f"🗑️ Carpeta eliminada: {dir_path}")
                except Exception as e:
                    self.logger.error(f"⚠️ No se pudo eliminar {dir_path}: {e}")

        

    def upload_logs_folder(self, base_path) -> None:
        """
        Sube los archivos del directorio base_path/logs a S3.
        - Si el archivo es .csv → va a la carpeta /logs/ en S3
        - Si el archivo es .json → va a la carpeta /resumen/ en S3
        - Ignora los archivos que correspondan a la fecha actual (según su nombre).
        - Elimina localmente los archivos subidos con éxito (excepto los del día actual).
        """
        base_path = str(base_path)
        logs_path = os.path.join(base_path, "logs")

        if not os.path.exists(logs_path):
            self.logger.error(f"La ruta {logs_path} no existe.")
            return

        self.logger.info(f"🗂️ Iniciando subida de carpeta de logs: {logs_path}")

        # Fecha actual (para detectar archivos del día)
        hoy = datetime.datetime.now().strftime("%d-%m-%Y")

        # Contadores para resumen
        subidos = 0
        errores = 0
        ignorados = 0

        for file_name in os.listdir(logs_path):
            file_path = os.path.join(logs_path, file_name)

            if not os.path.isfile(file_path):
                continue

            # Ignorar archivos del día actual
            if hoy in file_name:
                self.logger.info(f"⏩ Ignorando archivo del día actual: {file_name}")
                ignorados += 1
                continue

            # Detectar tipo de archivo
            extension = os.path.splitext(file_name)[1].lower()

            if extension == ".csv":
                s3_folder = "logs"
           
            else:
                self.logger.warning(f"⚠️ Tipo de archivo no soportado: {file_name}")
                continue

            s3_key = f"{self.s3_manager.prefix}/{s3_folder}/{file_name}".replace("\\", "/")

            self.logger.info(f"📤 Subiendo {file_path} → s3://{self.s3_manager.bucketName}/{s3_key}")

            try:
                success = self.s3_manager.uploadFile(file_path, s3_key)

                if success:
                    self.logger.info(f"✅ Subido correctamente: {file_name}")
                    subidos += 1
                    # Eliminar el archivo después de subirlo exitosamente
                    try:
                        os.remove(file_path)
                        self.logger.info(f"🗑️ Archivo eliminado localmente: {file_name}")
                    except Exception as e:
                        self.logger.error(f"⚠️ No se pudo eliminar {file_name}: {e}")
                else:
                    self.logger.error(f"❌ Falló la subida: {file_name}")
                    errores += 1

            except Exception as e:
                self.logger.error(f"💥 Error inesperado subiendo {file_name}: {e}")
                errores += 1

        self.logger.info(
            f"🎯 Subida completa de 'logs': "
            f"{subidos} subidos y eliminados, {errores} errores, {ignorados} ignorados ({hoy})."
        )

    def limpiar_output(self, base_path: str) -> None:
        """
        Elimina todo el contenido dentro de:
        - output/estados/*
        - output/img/*
        """
        base_path = str(base_path)
        rutas = [
            os.path.join(base_path,  "estados"),
            os.path.join(base_path,  "img")
        ]

        for ruta in rutas:
            if not os.path.exists(ruta):
                self.logger.warning(f"⚠️ La ruta no existe: {ruta}")
                continue

            for item in os.listdir(ruta):
                item_path = os.path.join(ruta, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)

                    self.logger.info(f"🗑️ Eliminado: {item_path}")

                except Exception as e:
                    self.logger.error(f"❌ No se pudo eliminar {item_path}: {e}")

        self.logger.info("🧹 Limpieza de output/estados y output/img completada")
