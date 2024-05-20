import time
import os
from terminable_thread import threading
from core.FileMonitor import FileMonitor
from core.exit_helper import terminate_thread


class ModuleProcessor:
    def __init__(self):
        self.kill_flag = False
        self.dirToWatch = os.getcwd() + "/tmp/ohp_thinkphp_v5rce/"
        self.module_name = "thinkphp/v5rce"

    def processor(self):
        newFileHandler = FileMonitor(self.dirToWatch)
        newFileHandler.module_name = self.module_name

        thread = threading.Thread(target=newFileHandler.run, args=(), name="thinkphp5_processor")
        thread.start()  # Start the execution
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
            f"--volume {os.getcwd()}/tmp/ohp_thinkphp_v5rce/.bash_history:/root/.bash_history:z"
        ],
        "module_processor": ModuleProcessor()
    }
