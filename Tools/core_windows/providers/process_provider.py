import psutil
from typing import List, Optional
from Tools.core_windows.models.windows_models import ProcessInfo

class ProcessProvider:
    SYSTEM_PROCESSES = {
        'explorer.exe', 'svchost.exe', 'csrss.exe', 'smss.exe', 
        'wininit.exe', 'services.exe', 'lsass.exe', 'system', 'registry'
    }

    def list_processes(self) -> List[ProcessInfo]:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                p_info = proc.info
                exe = None
                memory_mb = 0.0
                try:
                    exe = proc.exe()
                    memory_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    pass

                processes.append(ProcessInfo(
                    pid=p_info['pid'],
                    name=p_info['name'],
                    exe=exe,
                    status=p_info['status'],
                    memory_mb=memory_mb
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes

    def get_process(self, pid: int) -> Optional[ProcessInfo]:
        try:
            proc = psutil.Process(pid)
            exe = None
            memory_mb = 0.0
            try:
                exe = proc.exe()
                memory_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
            except psutil.AccessDenied:
                pass
            
            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                exe=exe,
                status=proc.status(),
                memory_mb=memory_mb
            )
        except psutil.NoSuchProcess:
            return None

    # TỐI ƯU HÓA: Hàm tra cứu siêu tốc (Chỉ lọc name, bỏ qua exe và memory)
    def check_process_by_name(self, exe_name: str) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def terminate_process(self, pid: int) -> bool:
        try:
            proc = psutil.Process(pid)
            if proc.name().lower() in self.SYSTEM_PROCESSES:
                return False
                
            proc.terminate()
            proc.wait(timeout=3)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            return False