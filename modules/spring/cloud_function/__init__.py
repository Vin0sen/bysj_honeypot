import time
import os
from terminable_thread import threading
from core.FileMonitor import FileMonitor
from core.exit_helper import terminate_thread


class ModuleProcessor:
    def __init__(self):
        self.kill_flag = False
        self.dirToWatch = os.getcwd() + "/tmp/ohp_spring_cloud/"
        self.module_name = "spring/cloud_function"

    def processor(self):
        newFileHandler = FileMonitor(self.dirToWatch)
        newFileHandler.module_name = self.module_name

        thread = threading.Thread(target=newFileHandler.run, args=(), name="spring_cloud_processor")
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
            f"--volume {os.getcwd()}/tmp/ohp_spring_cloud:/root:z"
        ],
        "module_processor": ModuleProcessor()
    }
