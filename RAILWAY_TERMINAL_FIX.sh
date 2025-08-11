#!/bin/bash

echo "==========================================
🚨 Railway 터미널 긴급 수정 스크립트
==========================================

이 스크립트를 Railway 대시보드의 Shell에서 실행하세요.

1. https://railway.app 접속
2. VideoPlane 프로젝트 선택
3. Settings → Shell 클릭
4. 아래 명령어 복사하여 실행:
"

echo "
# Python 스크립트 실행
python emergency_railway_fix.py

# 또는 Django shell에서 직접 실행
python manage.py shell << EOF
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"ALTER TABLE users_user ALTER COLUMN deletion_reason SET DEFAULT ''\")
    cursor.execute(\"UPDATE users_user SET deletion_reason = '' WHERE deletion_reason IS NULL\")
print('Database fixed!')
EOF

# 서비스 재시작 (Railway 대시보드에서)
# Deploy 탭 → Restart 클릭
"

echo "
==========================================
🔍 로그 확인 방법
==========================================

Railway 대시보드에서:
1. Observability → Logs
2. 빨간색 에러 메시지 확인
3. 'deletion_reason' 에러가 없어졌는지 확인

==========================================
⚠️ Rate Limit 문제 해결
==========================================

Railway 로그에 'Rate limit of 500 logs/sec reached' 메시지가 표시되면:

1. 환경 변수 추가 (Variables 탭):
   DJANGO_LOG_LEVEL=ERROR
   DEBUG=False

2. 서비스 재시작

==========================================
"