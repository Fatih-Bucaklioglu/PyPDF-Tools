#!/usr/bin/env python3
"""
Otomasyon Sistemi - Klasör izleme ve otomatik işlem başlatma
Akıllı PDF işleme otomasyonu ve trigger sistemi
"""

import os
import time
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QFileSystemWatcher
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QComboBox, QSpinBox, 
    QCheckBox, QTextEdit, QListWidget, QListWidgetItem,
    QGroupBox, QTabWidget, QLabel, QFileDialog,
    QMessageBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter
)

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Trigger türleri"""
    FILE_ADDED = "file_added"
    FILE_MODIFIED = "file_modified"
    FILE_SIZE = "file_size"
    TIME_SCHEDULED = "time_scheduled"
    TIME_INTERVAL = "time_interval"
    BATCH_SIZE = "batch_size"
    SYSTEM_IDLE = "system_idle"


class ActionType(Enum):
    """Aksiyon türleri"""
    MERGE_PDFS = "merge_pdfs"
    SPLIT_PDF = "split_pdf"
    COMPRESS_PDF = "compress_pdf"
    CONVERT_TO_PDF = "convert_to_pdf"
    CONVERT_FROM_PDF = "convert_from_pdf"
    OCR_PROCESS = "ocr_process"
    MOVE_FILE = "move_file"
    COPY_FILE = "copy_file"
    DELETE_FILE = "delete_file"
    RUN_SCRIPT = "run_script"
    SEND_EMAIL = "send_email"


@dataclass
class AutomationRule:
    """Otomasyon kuralı"""
    id: str
    name: str
    description: str
    enabled: bool
    
    # Trigger ayarları
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    
    # Condition ayarları
    conditions: List[Dict[str, Any]]
    
    # Action ayarları
    action_type: ActionType
    action_config: Dict[str, Any]
    
    # Metadata
    created_at: datetime
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary'ye çevir"""
        data = asdict(self)
        data['trigger_type'] = self.trigger_type.value
        data['action_type'] = self.action_type.value
        data['created_at'] = self.created_at.isoformat()
        if self.last_executed:
            data['last_executed'] = self.last_executed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationRule':
        """Dictionary'den oluştur"""
        data['trigger_type'] = TriggerType(data['trigger_type'])
        data['action_type'] = ActionType(data['action_type'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_executed'):
            data['last_executed'] = datetime.fromisoformat(data['last_executed'])
        return cls(**data)


class AutomationEngine(QObject):
    """Ana otomasyon motoru"""
    
    rule_triggered = pyqtSignal(str, str)  # rule_id, file_path
    action_started = pyqtSignal(str, str, str)  # rule_id, action, file_path
    action_completed = pyqtSignal(str, bool, str)  # rule_id, success, message
    rule_error = pyqtSignal(str, str)  # rule_id, error_message
    
    def __init__(self, config_dir: str = None):
        super().__init__()
        
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "automation"
        self.config_dir.mkdir(exist_ok=True)
        
        self.rules_file = self.config_dir / "rules.json"
        self.logs_dir = self.config_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.rules: Dict[str, AutomationRule] = {}
        self.watchers: Dict[str, QFileSystemWatcher] = {}
        self.timers: Dict[str, QTimer] = {}
        self.is_running = False
        
        self._load_rules()
        self._setup_system_monitoring()
    
    def _setup_system_monitoring(self):
        """Sistem izleme kurulumu"""
        # Ana timer - her 30 saniyede kontrol
        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self._check_scheduled_rules)
        self.main_timer.setInterval(30000)  # 30 saniye
    
    def start(self):
        """Otomasyon sistemini başlat"""
        self.is_running = True
        self.main_timer.start()
        self._setup_file_watchers()
        logger.info("Automation engine started")
    
    def stop(self):
        """Otomasyon sistemini durdur"""
        self.is_running = False
        self.main_timer.stop()
        
        # Tüm watcher'ları durdur
        for watcher in self.watchers.values():
            watcher.deleteLater()
        self.watchers.clear()
        
        # Tüm timer'ları durdur
        for timer in self.timers.values():
            timer.stop()
            timer.deleteLater()
        self.timers.clear()
        
        logger.info("Automation engine stopped")
    
    def add_rule(self, rule: AutomationRule) -> bool:
        """Yeni kural ekle"""
        try:
            self.rules[rule.id] = rule
            self._save_rules()
            
            if self.is_running and rule.enabled:
                self._setup_rule_monitoring(rule)
            
            logger.info(f"Rule added: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add rule: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """Kuralı kaldır"""
        try:
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                
                # Monitoring'i durdur
                self._stop_rule_monitoring(rule_id)
                
                # Kuralı sil
                del self.rules[rule_id]
                self._save_rules()
                
                logger.info(f"Rule removed: {rule.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove rule: {e}")
            return False
    
    def enable_rule(self, rule_id: str, enabled: bool = True) -> bool:
        """Kuralı aktif/pasif et"""
        try:
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                rule.enabled = enabled
                
                if self.is_running:
                    if enabled:
                        self._setup_rule_monitoring(rule)
                    else:
                        self._stop_rule_monitoring(rule_id)
                
                self._save_rules()
                logger.info(f"Rule {'enabled' if enabled else 'disabled'}: {rule.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to toggle rule: {e}")
            return False
    
    def get_rules(self) -> List[AutomationRule]:
        """Tüm kuralları döndür"""
        return list(self.rules.values())
    
    def get_rule(self, rule_id: str) -> Optional[AutomationRule]:
        """Belirli kuralı döndür"""
        return self.rules.get(rule_id)
    
    def _setup_file_watchers(self):
        """Dosya izleyicilerini kur"""
        for rule in self.rules.values():
            if rule.enabled and rule.trigger_type in [TriggerType.FILE_ADDED, TriggerType.FILE_MODIFIED]:
                self._setup_rule_monitoring(rule)
    
    def _setup_rule_monitoring(self, rule: AutomationRule):
        """Belirli kural için izleme kur"""
        try:
            if rule.trigger_type in [TriggerType.FILE_ADDED, TriggerType.FILE_MODIFIED]:
                self._setup_file_watcher(rule)
            elif rule.trigger_type == TriggerType.TIME_SCHEDULED:
                self._setup_scheduled_timer(rule)
            elif rule.trigger_type == TriggerType.TIME_INTERVAL:
                self._setup_interval_timer(rule)
                
        except Exception as e:
            logger.error(f"Failed to setup monitoring for rule {rule.name}: {e}")
    
    def _setup_file_watcher(self, rule: AutomationRule):
        """Dosya watcher'ı kur"""
        watch_path = rule.trigger_config.get('watch_path')
        if not watch_path or not os.path.exists(watch_path):
            logger.warning(f"Invalid watch path for rule {rule.name}: {watch_path}")
            return
        
        watcher = QFileSystemWatcher()
        watcher.addPath(watch_path)
        
        # Recursive izleme
        if rule.trigger_config.get('recursive', False):
            for root, dirs, _ in os.walk(watch_path):
                watcher.addPath(root)
        
        # Sinyal bağlantıları
        if rule.trigger_type == TriggerType.FILE_ADDED:
            watcher.directoryChanged.connect(lambda path: self._on_directory_changed(rule.id, path))
        elif rule.trigger_type == TriggerType.FILE_MODIFIED:
            watcher.fileChanged.connect(lambda path: self._on_file_changed(rule.id, path))
        
        self.watchers[rule.id] = watcher
        logger.info(f"File watcher setup for rule {rule.name}: {watch_path}")
    
    def _setup_scheduled_timer(self, rule: AutomationRule):
        """Zamanlanmış timer kur"""
        schedule_time = rule.trigger_config.get('schedule_time')
        if not schedule_time:
            return
        
        # Günlük tekrar için timer kur
        timer = QTimer()
        timer.timeout.connect(lambda: self._execute_rule(rule.id, ""))
        
        # Bir sonraki çalışma zamanını hesapla
        now = datetime.now()
        target_time = datetime.strptime(schedule_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        
        if target_time <= now:
            target_time += timedelta(days=1)
        
        # İlk çalışma için delay
        delay_ms = int((target_time - now).total_seconds() * 1000)
        timer.setSingleShot(True)
        timer.start(delay_ms)
        
        self.timers[rule.id] = timer
        logger.info(f"Scheduled timer setup for rule {rule.name}: {schedule_time}")
    
    def _setup_interval_timer(self, rule: AutomationRule):
        """Interval timer kur"""
    def _setup_interval_timer(self, rule: AutomationRule):
        """Interval timer kur"""
        interval_minutes = rule.trigger_config.get('interval_minutes', 60)
        
        timer = QTimer()
        timer.timeout.connect(lambda: self._execute_rule(rule.id, ""))
        timer.start(interval_minutes * 60 * 1000)  # Dakikayı milisaniyeye çevir
        
        self.timers[rule.id] = timer
        logger.info(f"Interval timer setup for rule {rule.name}: {interval_minutes} minutes")
    
    def _stop_rule_monitoring(self, rule_id: str):
        """Kural izlemeyi durdur"""
        # File watcher'ı durdur
        if rule_id in self.watchers:
            self.watchers[rule_id].deleteLater()
            del self.watchers[rule_id]
        
        # Timer'ı durdur
        if rule_id in self.timers:
            self.timers[rule_id].stop()
            self.timers[rule_id].deleteLater()
            del self.timers[rule_id]
    
    def _on_directory_changed(self, rule_id: str, path: str):
        """Dizin değişikliği algılandığında"""
        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return
        
        # Yeni dosyaları kontrol et
        watch_path = Path(path)
        file_pattern = rule.trigger_config.get('file_pattern', '*.pdf')
        
        try:
            # Son 10 saniye içinde eklenen dosyaları bul
            current_time = time.time()
            for file_path in watch_path.glob(file_pattern):
                if file_path.stat().st_mtime > current_time - 10:
                    if self._check_conditions(rule, str(file_path)):
                        self._execute_rule(rule_id, str(file_path))
                        
        except Exception as e:
            logger.error(f"Error checking directory changes: {e}")
    
    def _on_file_changed(self, rule_id: str, file_path: str):
        """Dosya değişikliği algılandığında"""
        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return
        
        if self._check_conditions(rule, file_path):
            self._execute_rule(rule_id, file_path)
    
    def _check_scheduled_rules(self):
        """Zamanlanmış kuralları kontrol et"""
        current_time = datetime.now()
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if rule.trigger_type == TriggerType.TIME_SCHEDULED:
                schedule_time = rule.trigger_config.get('schedule_time')
                if schedule_time:
                    target_time = datetime.strptime(schedule_time, "%H:%M").time()
                    if (current_time.time().hour == target_time.hour and 
                        current_time.time().minute == target_time.minute):
                        
                        # Günlük sadece bir kez çalışsın
                        if (not rule.last_executed or 
                            rule.last_executed.date() < current_time.date()):
                            self._execute_rule(rule.id, "")
    
    def _check_conditions(self, rule: AutomationRule, file_path: str) -> bool:
        """Koşulları kontrol et"""
        if not rule.conditions:
            return True
        
        try:
            path = Path(file_path)
            
            for condition in rule.conditions:
                condition_type = condition.get('type')
                condition_value = condition.get('value')
                
                if condition_type == 'file_extension':
                    if not path.suffix.lower() == condition_value.lower():
                        return False
                
                elif condition_type == 'file_size_min':
                    if path.stat().st_size < int(condition_value) * 1024 * 1024:  # MB
                        return False
                
                elif condition_type == 'file_size_max':
                    if path.stat().st_size > int(condition_value) * 1024 * 1024:  # MB
                        return False
                
                elif condition_type == 'file_name_contains':
                    if condition_value.lower() not in path.name.lower():
                        return False
                
                elif condition_type == 'file_name_regex':
                    import re
                    if not re.search(condition_value, path.name):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conditions: {e}")
            return False
    
    def _execute_rule(self, rule_id: str, file_path: str):
        """Kuralı çalıştır"""
        rule = self.rules.get(rule_id)
        if not rule:
            return
        
        try:
            self.rule_triggered.emit(rule_id, file_path)
            logger.info(f"Executing rule: {rule.name} for {file_path}")
            
            # Action'ı çalıştır
            success = self._execute_action(rule, file_path)
            
            # İstatistikleri güncelle
            rule.last_executed = datetime.now()
            rule.execution_count += 1
            self._save_rules()
            
            message = "İşlem başarıyla tamamlandı" if success else "İşlem başarısız"
            self.action_completed.emit(rule_id, success, message)
            
        except Exception as e:
            error_msg = f"Rule execution failed: {e}"
            logger.error(error_msg)
            self.rule_error.emit(rule_id, error_msg)
    
    def _execute_action(self, rule: AutomationRule, file_path: str) -> bool:
        """Action'ı çalıştır"""
        try:
            action_type = rule.action_type
            config = rule.action_config
            
            self.action_started.emit(rule.id, action_type.value, file_path)
            
            if action_type == ActionType.COMPRESS_PDF:
                return self._action_compress_pdf(file_path, config)
            
            elif action_type == ActionType.MOVE_FILE:
                return self._action_move_file(file_path, config)
            
            elif action_type == ActionType.COPY_FILE:
                return self._action_copy_file(file_path, config)
            
            elif action_type == ActionType.OCR_PROCESS:
                return self._action_ocr_process(file_path, config)
            
            elif action_type == ActionType.RUN_SCRIPT:
                return self._action_run_script(file_path, config)
            
            elif action_type == ActionType.SEND_EMAIL:
                return self._action_send_email(file_path, config)
            
            else:
                logger.warning(f"Unsupported action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return False
    
    def _action_compress_pdf(self, file_path: str, config: Dict[str, Any]) -> bool:
        """PDF sıkıştırma action'ı"""
        try:
            from ..core.pdf_processor import PDFProcessor
            
            output_dir = config.get('output_dir', str(Path(file_path).parent / "compressed"))
            quality = config.get('quality', 'medium')
            
            Path(output_dir).mkdir(exist_ok=True)
            output_file = Path(output_dir) / f"compressed_{Path(file_path).name}"
            
            processor = PDFProcessor()
            return processor.compress_pdf(file_path, str(output_file), quality=quality)
            
        except ImportError:
            # Mock implementation for development
            logger.info(f"Mock: Compressing {file_path}")
            return True
        except Exception as e:
            logger.error(f"PDF compression failed: {e}")
            return False
    
    def _action_move_file(self, file_path: str, config: Dict[str, Any]) -> bool:
        """Dosya taşıma action'ı"""
        try:
            import shutil
            
            target_dir = config.get('target_dir')
            if not target_dir:
                return False
            
            Path(target_dir).mkdir(exist_ok=True)
            target_path = Path(target_dir) / Path(file_path).name
            
            shutil.move(file_path, str(target_path))
            logger.info(f"File moved: {file_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"File move failed: {e}")
            return False
    
    def _action_copy_file(self, file_path: str, config: Dict[str, Any]) -> bool:
        """Dosya kopyalama action'ı"""
        try:
            import shutil
            
            target_dir = config.get('target_dir')
            if not target_dir:
                return False
            
            Path(target_dir).mkdir(exist_ok=True)
            target_path = Path(target_dir) / Path(file_path).name
            
            shutil.copy2(file_path, str(target_path))
            logger.info(f"File copied: {file_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"File copy failed: {e}")
            return False
    
    def _action_ocr_process(self, file_path: str, config: Dict[str, Any]) -> bool:
        """OCR işleme action'ı"""
        try:
            from ..core.ocr_processor import OCRProcessor
            
            output_dir = config.get('output_dir', str(Path(file_path).parent / "ocr_processed"))
            language = config.get('language', 'tur')
            
            Path(output_dir).mkdir(exist_ok=True)
            output_file = Path(output_dir) / f"searchable_{Path(file_path).name}"
            
            processor = OCRProcessor()
            return processor.process_pdf(
                input_file=file_path,
                output_file=str(output_file),
                language=language
            )
            
        except ImportError:
            # Mock implementation for development
            logger.info(f"Mock: OCR processing {file_path}")
            return True
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return False
    
    def _action_run_script(self, file_path: str, config: Dict[str, Any]) -> bool:
        """Script çalıştırma action'ı"""
        try:
            import subprocess
            
            script_path = config.get('script_path')
            if not script_path or not os.path.exists(script_path):
                return False
            
            # Script'i file_path parametresi ile çalıştır
            result = subprocess.run([
                'python', script_path, file_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Script executed successfully: {script_path}")
                return True
            else:
                logger.error(f"Script execution failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return False
    
    def _action_send_email(self, file_path: str, config: Dict[str, Any]) -> bool:
        """E-posta gönderme action'ı"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication
            
            smtp_server = config.get('smtp_server')
            smtp_port = config.get('smtp_port', 587)
            username = config.get('username')
            password = config.get('password')
            to_email = config.get('to_email')
            subject = config.get('subject', f"Automated processing: {Path(file_path).name}")
            
            if not all([smtp_server, username, password, to_email]):
                logger.error("Email configuration incomplete")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            body = f"Dosya otomatik olarak işlendi: {file_path}"
            msg.attach(MIMEText(body, 'plain'))
            
            # Dosyayı ekle
            if config.get('attach_file', False):
                with open(file_path, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=Path(file_path).name)
                    msg.attach(attachment)
            
            # E-posta gönder
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _load_rules(self):
        """Kuralları yükle"""
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for rule_data in data:
                    rule = AutomationRule.from_dict(rule_data)
                    self.rules[rule.id] = rule
                
                logger.info(f"Loaded {len(self.rules)} automation rules")
            
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
    
    def _save_rules(self):
        """Kuralları kaydet"""
        try:
            data = [rule.to_dict() for rule in self.rules.values()]
            
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("Rules saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save rules: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        total_rules = len(self.rules)
        enabled_rules = sum(1 for rule in self.rules.values() if rule.enabled)
        total_executions = sum(rule.execution_count for rule in self.rules.values())
        
        return {
            'total_rules': total_rules,
            'enabled_rules': enabled_rules,
            'disabled_rules': total_rules - enabled_rules,
            'total_executions': total_executions,
            'is_running': self.is_running
        }


class AutomationRuleBuilder:
    """Otomasyon kuralı oluşturma yardımcısı"""
    
    @staticmethod
    def create_compress_on_add_rule(
        name: str,
        watch_directory: str,
        output_directory: str,
        file_pattern: str = "*.pdf",
        quality: str = "medium"
    ) -> AutomationRule:
        """Dosya eklendiğinde sıkıştırma kuralı"""
        rule_id = f"compress_on_add_{int(time.time())}"
        
        return AutomationRule(
            id=rule_id,
            name=name,
            description=f"PDF dosyaları {watch_directory} klasörüne eklendiğinde otomatik sıkıştır",
            enabled=True,
            trigger_type=TriggerType.FILE_ADDED,
            trigger_config={
                'watch_path': watch_directory,
                'file_pattern': file_pattern,
                'recursive': False
            },
            conditions=[
                {'type': 'file_extension', 'value': '.pdf'}
            ],
            action_type=ActionType.COMPRESS_PDF,
            action_config={
                'output_dir': output_directory,
                'quality': quality
            },
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_scheduled_backup_rule(
        name: str,
        source_directory: str,
        backup_directory: str,
        schedule_time: str = "02:00"
    ) -> AutomationRule:
        """Zamanlanmış yedekleme kuralı"""
        rule_id = f"scheduled_backup_{int(time.time())}"
        
        return AutomationRule(
            id=rule_id,
            name=name,
            description=f"Her gün {schedule_time} zamanında PDF dosyalarını yedekle",
            enabled=True,
            trigger_type=TriggerType.TIME_SCHEDULED,
            trigger_config={
                'schedule_time': schedule_time
            },
            conditions=[],
            action_type=ActionType.COPY_FILE,
            action_config={
                'source_dir': source_directory,
                'target_dir': backup_directory
            },
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_ocr_batch_rule(
        name: str,
        watch_directory: str,
        output_directory: str,
        language: str = "tur"
    ) -> AutomationRule:
        """Toplu OCR kuralı"""
        rule_id = f"ocr_batch_{int(time.time())}"
        
        return AutomationRule(
            id=rule_id,
            name=name,
            description=f"Taranmış PDF'lere otomatik OCR uygula",
            enabled=True,
            trigger_type=TriggerType.FILE_ADDED,
            trigger_config={
                'watch_path': watch_directory,
                'file_pattern': "*.pdf",
                'recursive': True
            },
            conditions=[
                {'type': 'file_extension', 'value': '.pdf'},
                {'type': 'file_name_contains', 'value': 'scanned'}
            ],
            action_type=ActionType.OCR_PROCESS,
            action_config={
                'output_dir': output_directory,
                'language': language
            },
            created_at=datetime.now()
        )


if __name__ == "__main__":
    # Test için örnek kullanım
    logging.basicConfig(level=logging.INFO)
    
    engine = AutomationEngine()
    
    # Örnek kural oluştur
    rule = AutomationRuleBuilder.create_compress_on_add_rule(
        name="Auto Compress Downloads",
        watch_directory=str(Path.home() / "Downloads"),
        output_directory=str(Path.home() / "Documents" / "Compressed"),
        quality="medium"
    )
    
    engine.add_rule(rule)
    engine.start()
    
    print(f"Automation engine started with {len(engine.get_rules())} rules")
    print("Statistics:", engine.get_statistics())
