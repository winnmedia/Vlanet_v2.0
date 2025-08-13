# VideoPlanet 회원가입 시스템 API 문서

## 개요
VideoPlanet 회원가입 시스템의 개선된 API 엔드포인트 명세서입니다.

## 도메인 아키텍처

### Bounded Context: User Management
- **Aggregates**: User (Root), UserProfile
- **Value Objects**: Email, PhoneNumber, CompanyInfo
- **Domain Services**: EmailVerificationDomainService, UserRegistrationDomainService

## API 엔드포인트

### 1. 이메일 중복 체크 + 인증 코드 발송
**POST** `/api/auth/check-email-verify/`

#### Request
```json
{
    "email": "user@example.com"
}
```

#### Response (성공 - 사용 가능)
```json
{
    "success": true,
    "available": true,
    "verified": false,
    "message": "인증 코드가 이메일로 발송되었습니다.",
    "action": "verify",
    "expires_in": 600
}
```

#### Response (이미 등록됨)
```json
{
    "success": false,
    "available": false,
    "message": "이미 등록된 이메일입니다.",
    "action": "none"
}
```

### 2. 이메일 인증 코드 확인
**POST** `/api/auth/verify-email-code/`

#### Request
```json
{
    "email": "user@example.com",
    "code": "123456"
}
```

#### Response (성공)
```json
{
    "success": true,
    "message": "이메일 인증이 완료되었습니다."
}
```

#### Response (실패)
```json
{
    "success": false,
    "message": "잘못된 인증 코드입니다."
}
```

### 3. 닉네임 중복 체크
**POST** `/api/auth/check-nickname/`

#### Request
```json
{
    "nickname": "cooluser"
}
```

#### Response
```json
{
    "success": true,
    "available": true,
    "nickname": "cooluser",
    "message": "사용 가능한 닉네임입니다."
}
```

### 4. 개선된 회원가입 (추가 정보 포함)
**POST** `/api/auth/signup-enhanced/`

#### Request
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "nickname": "cooluser",
    "full_name": "홍길동",
    "company": "ABC Company",
    "position": "개발자",
    "phone": "010-1234-5678",
    "bio": "안녕하세요",
    "terms_agreed": true,
    "privacy_agreed": true,
    "marketing_agreed": false
}
```

#### Response (성공)
```json
{
    "success": true,
    "message": "회원가입이 완료되었습니다.",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "nickname": "cooluser",
        "full_name": "홍길동"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 5. 인증 코드 재발송
**POST** `/api/auth/resend-verification/`

#### Request
```json
{
    "email": "user@example.com"
}
```

#### Response
```json
{
    "success": true,
    "message": "인증 코드가 재발송되었습니다.",
    "expires_in": 600
}
```

## 에러 코드

| 코드 | 설명 | HTTP Status |
|------|------|-------------|
| INVALID_REQUEST | 잘못된 요청 형식 | 400 |
| VALIDATION_ERROR | 유효성 검사 실패 | 400 |
| USER_ALREADY_EXISTS | 이미 존재하는 사용자 | 200 (변경됨) |
| INVALID_CREDENTIALS | 잘못된 인증 정보 | 401 |
| ACCOUNT_INACTIVE | 비활성화된 계정 | 403 |
| SERVER_ERROR | 서버 내부 오류 | 500 |

## Rate Limiting

- 이메일 인증: 3 requests/minute/IP
- 로그인: 5 requests/minute/IP
- 회원가입: 10 requests/hour/IP

## 보안 고려사항

1. **비밀번호 정책**
   - 최소 8자 이상
   - 영문 + 숫자 필수
   - 특수문자 권장

2. **이메일 인증**
   - 6자리 숫자 코드
   - 10분 만료
   - 최대 5회 시도

3. **세션 관리**
   - JWT 토큰 사용
   - Access Token: 60분
   - Refresh Token: 30일

## 마이그레이션 가이드

### 1. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations users
python manage.py migrate users
```

### 2. 환경 변수 설정
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@videoplanet.com
```

### 3. URL 라우팅 추가
```python
# config/urls.py
urlpatterns += [
    path('api/auth/', include('users.urls_enhanced')),
]
```

## 테스트 시나리오

### 시나리오 1: 정상 회원가입 플로우
1. 이메일 중복 체크 → 사용 가능
2. 인증 코드 발송
3. 인증 코드 입력
4. 닉네임 중복 체크
5. 회원가입 완료

### 시나리오 2: 중복 이메일 처리
1. 이메일 중복 체크 → 이미 존재
2. 다른 이메일로 재시도

### 시나리오 3: 인증 코드 만료
1. 인증 코드 발송
2. 10분 경과
3. 인증 실패
4. 재발송 요청