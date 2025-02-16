# Python 3.10 이미지를 기반으로 합니다
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 필요한 파일들을 컨테이너로 복사
COPY requirements.txt .
COPY app.py .
COPY config.json .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 보안을 위해 비특권 사용자 생성 및 전환
RUN useradd -m -r -u 1000 streamlit
RUN chown -R streamlit:streamlit /app
USER streamlit

# 포트 설정
EXPOSE 8501

# 환경 변수 설정
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 실행 명령
CMD ["streamlit", "run", "app.py"] 