# 🆘 Railway 수동 명령어

## Railway 대시보드에서 직접 실행

1. https://railway.app 접속
2. VideoPlane 프로젝트 선택
3. **Settings** 탭 클릭

## Deploy 섹션에서 변경

**Start Command** 필드에 다음 중 하나 입력:

### 옵션 1: 가장 단순한 서버
```
python server_simple.py
```

### 옵션 2: Python 내장 서버
```
python -m http.server $PORT
```

### 옵션 3: 직접 Python 코드 실행
```
python -c "from http.server import HTTPServer, BaseHTTPRequestHandler; import os; port=int(os.environ.get('PORT',8000)); class H(BaseHTTPRequestHandler): def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b'OK'); def log_message(self,*a): pass; HTTPServer(('0.0.0.0',port),H).serve_forever()"
```

### 옵션 4: Echo 서버
```
while true; do echo -e "HTTP/1.1 200 OK\n\nOK" | nc -l -p $PORT; done
```

## Variables 탭에서 추가

```
PORT=8000
PYTHONUNBUFFERED=1
```

## 배포

1. **Save** 클릭
2. **Deploy** 탭 → **Restart** 클릭

## 테스트

```bash
curl https://videoplanet.up.railway.app/
```

응답이 "OK"면 성공!