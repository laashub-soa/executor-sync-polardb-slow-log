部署

```
docker stop executor-sync-polardb-slow-log && docker rm executor-sync-polardb-slow-log
docker rmi tanshilindocker/laasops

mkdir -p /data/tristan/soa/executor-sync-polardb-slow-log/config && chmod 777 /data/tristan/soa/executor-sync-polardb-slow-log/config

docker run -d --restart=always --name executor-sync-polardb-slow-log \
  -v /etc/timezone:/etc/timezone \
  -v /etc/localtime:/etc/localtime \
  -v /data/tristan/soa/executor-sync-polardb-slow-log/config:/usr/src/app/configs \
  laashubsoa/executor-sync-polardb-slow-log:0.0.13

docker logs -f --tail 100 executor-sync-polardb-slow-log

docker exec -it executor-sync-polardb-slow-log bash
```

