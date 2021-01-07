```
# 进入容器内部:
docker exec -it mymysql /bin/bash

# 连接mysql
mysql -uroot -p

# 修改访问设置
ALTER USER 'tristan'@'%' IDENTIFIED WITH mysql_native_password BY 'tristan123';

# 刷新权限
FLUSH PRIVILEGES;
```