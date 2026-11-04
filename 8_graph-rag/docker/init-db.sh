#!/bin/bash
# 볼륨이 비어 있고 이미지에 덤프가 있으면 neo4j DB로 적재한 뒤 원래 entrypoint를 실행한다.
# 이미 데이터가 있는 볼륨이면 적재하지 않으므로, 실습 중 바꾼 데이터는 재시작해도 남는다.
set -e

if [ -f /dumps/neo4j.dump ] && [ ! -d /data/databases/neo4j ]; then
    echo "init-db: /dumps/neo4j.dump 를 neo4j DB로 적재합니다"
    neo4j-admin database load neo4j --from-path=/dumps --overwrite-destination=true
fi

exec /startup/docker-entrypoint.sh "$@"
