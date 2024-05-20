import time
import os
from terminable_thread import threading
from core.FileMonitor import FileMonitor
from core.exit_helper import terminate_thread


class ModuleProcessor:
    def __init__(self):
        self.kill_flag = False
        self.dirToWatch = os.getcwd() + "/tmp/ohp_tomcat_weak/"
        self.module_name = "tomcat/weak_password"

    def processor(self):
        newFileHandler = FileMonitor(self.dirToWatch)
        newFileHandler.module_name = self.module_name

        thread = threading.Thread(target=newFileHandler.run, args=(), name="tomcat_weak_processor")
        thread.start()
        while not self.kill_flag:
            try:
                time.sleep(0.1)
            except Exception:
                pass
        newFileHandler.stop()
        terminate_thread(thread)
        

def module_configuration():
    volume_path = os.getcwd()+'/modules/tomcat/weak_password/files'
    return {
        "extra_docker_options": [
            f"--volume {os.getcwd()}/tmp/ohp_tomcat_weak/.bash_history:/root/.bash_history:z",
            f"-v {volume_path}/tomcat-users.xml:/usr/local/tomcat/conf/tomcat-users.xml",
            f"-v {volume_path}/context.xml:/usr/local/tomcat/webapps/manager/META-INF/context.xml",
            f"-v {volume_path}/context.xml:/usr/local/tomcat/webapps/host-manager/META-INF/context.xml"
        ],
        "module_processor": ModuleProcessor()
    }
