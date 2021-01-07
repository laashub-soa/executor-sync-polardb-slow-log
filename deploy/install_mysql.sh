echo "清理原来的mysql容器"
docker stop mymysql
docker rm   mymysql

echo "拉取docker镜像"
docker pull mysql:8.0.22

echo "准备文件夹"
rm -rf /data/tristan/mysql/data
mkdir -p /data/tristan/mysql/data

echo "准备binlog"
sudo tee /data/tristan/mysql/mysql.cnf <<-'EOF'
[mysql]
[mysqld]
log-bin=binlog
server-id=1
sql_mode=STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
EOF
chmod 644 /data/tristan/mysql/mysql.cnf

echo "运行mysql容器"
docker run --name  mymysql -p 3306:3306 --restart=always --privileged=true \
    -v /etc/localtime:/etc/localtime:ro \
    -v /data/tristan/mysql/mysql.cnf:/etc/mysql/conf.d/mysql.cnf \
    -v /data/tristan/mysql/data:/var/lib/mysql \
    -e TZ=Asia/Shanghai \
    -e MYSQL_ROOT_PASSWORD=tristan123 \
    -e MYSQL_DATABASE=tristan \
    -e MYSQL_USER=tristan \
    -e MYSQL_PASSWORD=tristan123 \
    -d mysql:8.0.22  \
    --character-set-server=utf8mb4  \
    --collation-server=utf8mb4_unicode_ci

echo "查看容器运行情况"
docker ps|grep mymysql

sleep 3;
echo "查看日志"
docker logs -f --tail 100 mymysql
