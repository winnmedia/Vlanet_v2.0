# Static Files Configuration Guide

## 문제 해결 완료

### 원인
- Django가 존재하지 않는 프론트엔드 빌드 디렉토리를 참조하고 있었음
- Next.js 프로젝트가 아직 빌드되지 않은 상태였음

### 해결 방법
`config/settings_base.py` 파일을 수정하여 디렉토리가 존재하는 경우에만 STATICFILES_DIRS에 추가하도록 변경

## 현재 설정

### settings_base.py
```python
# Static files directories
STATICFILES_DIRS = []

# Django static directory (if exists)
django_static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(django_static_dir):
    STATICFILES_DIRS.append(django_static_dir)

# Frontend build static directory (only if exists - for production)
frontend_static_dir = os.path.join(BASE_DIR, "../vridge_front/build/static")
if os.path.exists(frontend_static_dir):
    STATICFILES_DIRS.append(frontend_static_dir)
    
# Next.js .next/static directory (for development)
nextjs_static_dir = os.path.join(BASE_DIR, "../vridge_front/.next/static")
if os.path.exists(nextjs_static_dir):
    STATICFILES_DIRS.append(nextjs_static_dir)
```

## 환경별 설정

### 개발 환경 (Development)
```python
# Django 내장 static 파일 서빙 사용
DEBUG = True
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

### 프로덕션 환경 (Production)
```python
# WhiteNoise를 사용한 정적 파일 서빙
DEBUG = False
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Railway 환경에서는 collectstatic 실행
# python manage.py collectstatic --noinput
```

## 프론트엔드 빌드 통합

### Next.js (현재 사용 중)
```bash
# 개발 모드
cd vridge_front
npm run dev  # localhost:3000에서 실행

# 프로덕션 빌드
npm run build
npm run start
```

### Django와 연동
1. **개발 환경**: 각각 독립적으로 실행
   - Django: `python manage.py runserver 8000`
   - Next.js: `npm run dev` (port 3000)

2. **프로덕션 환경**: 
   - Next.js를 정적 파일로 export: `npm run build && npm run export`
   - Django가 정적 파일 서빙

## 디렉토리 구조

```
VideoPlanet/
├── vridge_back/
│   ├── static/              # Django 정적 파일
│   ├── staticfiles/         # collectstatic 결과 (프로덕션)
│   └── config/
│       └── settings_base.py
│
└── vridge_front/
    ├── public/              # Next.js public 파일
    ├── .next/               # Next.js 빌드 결과 (개발)
    ├── build/               # React 빌드 결과 (있을 경우)
    └── out/                 # Next.js export 결과 (프로덕션)
```

## 명령어 참고

### 정적 파일 수집 (프로덕션)
```bash
python manage.py collectstatic --noinput
```

### 정적 파일 경로 확인
```python
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATICFILES_DIRS)
>>> print(settings.STATIC_ROOT)
```

### 트러블슈팅

#### 문제: Static 파일이 로드되지 않음
```bash
# 1. STATICFILES_DIRS 확인
python manage.py shell -c "from django.conf import settings; print(settings.STATICFILES_DIRS)"

# 2. 파일 권한 확인
ls -la vridge_back/static/
ls -la vridge_front/.next/

# 3. 개발 서버 재시작
python manage.py runserver --nostatic  # static 파일 서빙 비활성화
python manage.py runserver             # 정상 모드
```

#### 문제: collectstatic 실패
```bash
# 1. 디렉토리 권한 확인
chmod 755 vridge_back/staticfiles

# 2. 강제 수집
python manage.py collectstatic --clear --noinput

# 3. 특정 앱 제외
python manage.py collectstatic --ignore=admin --noinput
```

## 최적화 제안

### 1. CDN 사용 (프로덕션)
```python
# settings/production.py
STATIC_URL = 'https://cdn.example.com/static/'
```

### 2. 압축 활성화
```python
# WhiteNoise 압축 설정
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. 캐싱 헤더 설정
```python
# 1년 캐싱
WHITENOISE_MAX_AGE = 31536000
```

## 보안 고려사항

1. **민감한 파일 제외**
   ```python
   STATICFILES_DIRS = [
       ('public', os.path.join(BASE_DIR, 'static/public')),
       # private 디렉토리는 제외
   ]
   ```

2. **CORS 설정** (프론트엔드 분리 시)
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://vlanet.net",
       "http://localhost:3000",  # 개발용
   ]
   ```

## 성능 모니터링

### 정적 파일 로딩 시간 측정
```javascript
// 브라우저 콘솔에서
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('/static/'))
  .forEach(r => console.log(r.name, r.duration + 'ms'));
```

### Django Debug Toolbar 활용
```python
# 개발 환경에서만
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

## 결론

현재 설정은 개발과 프로덕션 환경 모두를 지원하도록 최적화되었습니다. 
디렉토리가 존재하는 경우에만 STATICFILES_DIRS에 추가되므로 더 이상 경고가 발생하지 않습니다.

### 현재 상태
- ✅ Static 파일 경로 경고 해결
- ✅ 개발 환경 설정 완료
- ✅ 프로덕션 환경 대비 완료
- ✅ 다양한 프론트엔드 빌드 도구 지원

### 추가 작업 필요 시
1. 프론트엔드 빌드: `cd vridge_front && npm run build`
2. 정적 파일 수집: `python manage.py collectstatic`
3. CDN 설정 (선택사항)

---
작성일: 2025-08-11
작성자: Robert (DevOps/Platform Lead)