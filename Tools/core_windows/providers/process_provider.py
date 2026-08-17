import psutil
from typing import List, Optional
from Tools.core_windows.models.windows_models import ProcessInfo

class ProcessProvider:
    SYSTEM_PROCESSES = {
        'explorer.exe', 'svchost.exe', 'csrss.exe', 'smss.exe', 
        'wininit.exe', 'services.exe', 'lsass.exe', 'system', 'registry',
        'winlogon.exe', 'dwm.exe', 'spoolsv.exe', 'taskmgr.exe', 'conhost.exe'
    }

    def is_system_process(self, process_name: str) -> bool:
        return process_name.lower() in self.SYSTEM_PROCESSES

    def list_processes(self, name_filter: str = "") -> List[ProcessInfo]:
        processes = []
        name_filter_lower = name_filter.lower()
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                p_name = proc.info.get('name', '')
                if not p_name or (name_filter_lower and name_filter_lower not in p_name.lower()):
                    continue

                exe = None
                memory_mb = 0.0
                try:
                    exe = proc.exe()
                    memory_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    pass

                processes.append(ProcessInfo(
                    pid=proc.info['pid'], name=p_name, exe=exe,
                    status=proc.info['status'], memory_mb=memory_mb
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes

    def get_process(self, pid: int) -> ProcessInfo:
        """Bắn thẳng Exception để tầng Tool chuẩn hóa mã lỗi."""
        try:
            proc = psutil.Process(pid)
            exe = None
            memory_mb = 0.0
            try:
                exe = proc.exe()
                memory_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
            except (psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
            return ProcessInfo(
                pid=proc.pid, name=proc.name(), exe=exe,
                status=proc.status(), memory_mb=memory_mb
            )
        except psutil.AccessDenied:
            raise PermissionError("ACCESS_DENIED")
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            raise ProcessLookupError("NOT_FOUND")

    def get_pids_by_name(self, exe_name: str) -> List[int]:
        pids = []
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                    pids.append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return pids