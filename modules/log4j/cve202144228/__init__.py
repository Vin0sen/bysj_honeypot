import time
import os
from terminable_thread import threading
from core.FileMonitor import FileMonitor
from core.exit_helper import terminate_thread


class ModuleProcessor:
    def __init__(self):
        self.kill_flag = False
        self.dirToWatch = os.getcwd() + "/tmp/ohp_log4j_2021/"
        self.module_name = "log4j/cve202144228"

    def processor(self):
        newFileHandler = FileMonitor(self.dirToWatch)
        newFileHandler.module_name = self.module_name

        thread = threading.Thread(target=newFileHandler.run, args=(), name="log4j_2021_processor")
        thread.start()
        while not self.kill_flag:
            try:
                time.sleep(0.1)
            except Exception:
                pass
        newFileHandler.stop()
        terminate_thread(thread)
        

def module_configuration():
    return {
        "extra_docker_options": [
            f"--volume {os.getcwd()}/tmp/ohp_log4j_2021/.bash_history:/root/.bash_history:z"
        ],
        "module_processor": ModuleProcessor()
    }
