import time
import os
from terminable_thread import threading
from core.FileMonitor import FileMonitor
from core.exit_helper import terminate_thread


class ModuleProcessor:
    def __init__(self):
        self.kill_flag = False
        self.dirToWatch = os.getcwd() + "/tmp/ohp_mysqlserver/"
        self.ignoreFile = ["mysqld.cnf"]
        self.module_name = "db/mysql"

    def processor(self):
        newFileHandler = FileMonitor(self.dirToWatch, self.ignoreFile)
        newFileHandler.module_name = self.module_name

        thread = threading.Thread(target=newFileHandler.run, args=(), name="mysql_processor")
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
            f"--volume {os.getcwd()}/tmp/ohp_mysqlserver/.mysql_history:/root/.mysql_history:z",
            f"-v {os.getcwd()}/tmp/ohp_mysqlserver/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf"
        ],
        "module_processor": ModuleProcessor()
    }
