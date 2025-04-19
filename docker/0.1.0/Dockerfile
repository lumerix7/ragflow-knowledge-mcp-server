FROM python:3.13.3-slim

ENV LANG=en_US.utf8
ENV TZ=Asia/Shanghai

ARG EXTRA_INDEX_URL
ARG EXTRA_INDEX_HOST

RUN pip install ragflow-knowledge-mcp-server --no-cache-dir --extra-index-url $EXTRA_INDEX_URL --trusted-host=$EXTRA_INDEX_HOST

EXPOSE 41106
WORKDIR /root

CMD ["ragflow-knowledge-mcp-server"]
