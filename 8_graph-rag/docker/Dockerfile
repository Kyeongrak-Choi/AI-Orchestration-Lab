# GraphRAG 실습용 Neo4j 이미지 (Neo4j 5.26 LTS + APOC)
#
# DUMP_URL을 주면 덤프 파일을 이미지에 넣어 두고, 빈 볼륨으로 처음 시작할 때 자동으로 적재한다.
# DUMP_URL이 없으면 빈 DB로 시작한다.
FROM neo4j:5.26

# APOC core는 이미지의 labs 폴더에 들어 있다. plugins로 옮겨 두면 시작할 때 인터넷 없이 켜진다.
# LangChain의 Neo4jGraph는 연결할 때 APOC(apoc.meta.*)로 스키마를 읽는다.
RUN cp /var/lib/neo4j/labs/apoc-*-core.jar /var/lib/neo4j/plugins/
ENV NEO4J_dbms_security_procedures_unrestricted=apoc.* \
    NEO4J_dbms_security_procedures_allowlist=apoc.*

ARG DUMP_URL=
RUN mkdir -p /dumps \
 && if [ -n "$DUMP_URL" ]; then wget -q -O /dumps/neo4j.dump "$DUMP_URL"; fi

# Windows에서 편집해 CRLF가 들어가도 실행되도록 줄 끝을 정리한다.
COPY init-db.sh /startup/init-db.sh
RUN sed -i 's/\r$//' /startup/init-db.sh && chmod +x /startup/init-db.sh

ENTRYPOINT ["tini", "-g", "--", "/startup/init-db.sh"]
CMD ["neo4j"]
