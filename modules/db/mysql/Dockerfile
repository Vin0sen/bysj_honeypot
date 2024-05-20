FROM phusion/baseimage:jammy-1.0.1
RUN apt-get update && apt-get install -y mysql-server

# 将 SQL 脚本复制到镜像中当前工作目录
COPY files/fulldb.sql files/useinit.sql ./

# 在 RUN 指令中，确保 MySQL 服务启动成功后再执行导入操作
RUN sudo service mysql start && \
    mysql -u root -e "source useinit.sql;source fulldb.sql;" && \
    rm useinit.sql fulldb.sql

# 定义容器启动时运行的命令
ENTRYPOINT sudo service mysql restart && tail
