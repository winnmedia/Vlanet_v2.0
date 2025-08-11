#!/bin/bash

# GitHub 배포 자동화 스크립트
# 작성자: Emily (CI/CD Engineer)
# 생성일: 2025-08-11
# 목적: GitHub Actions를 통한 완전 자동화 배포

set -e  # 에러 발생 시 스크립트 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🚀 $1${NC}"
}

# 배너 출력
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    GitHub 배포 자동화                        ║"
    echo "║                VideoPlanet CI/CD Pipeline                   ║"
    echo "║                                                              ║"
    echo "║  Frontend: Vercel    Backend: Railway    DB: PostgreSQL     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 스크립트 시작
print_banner

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
log_info "현재 브랜치: $CURRENT_BRANCH"

# 브랜치별 배포 전략 안내
if [[ "$CURRENT_BRANCH" == "main" ]]; then
    log_step "프로덕션 환경으로 배포됩니다"
    ENVIRONMENT="production"
elif [[ "$CURRENT_BRANCH" == "develop" ]]; then
    log_step "스테이징 환경으로 배포됩니다"
    ENVIRONMENT="staging"
else
    log_info "Feature 브랜치입니다. PR을 통한 배포를 권장합니다."
    ENVIRONMENT="feature"
fi

# 1. Git 상태 확인
log_step "1단계: Git 상태 확인"
if [[ -n $(git status --porcelain) ]]; then
    log_error "커밋되지 않은 변경사항이 있습니다:"
    git status --porcelain
    echo ""
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "배포가 취소되었습니다."
        exit 1
    fi
fi
log_success "Git 상태 확인 완료"

# 2. 원격 저장소 동기화
log_step "2단계: 원격 저장소와 동기화"
git fetch origin
if [[ $(git rev-list --count HEAD..origin/$CURRENT_BRANCH) -gt 0 ]]; then
    log_warning "원격 브랜치가 앞서있습니다. Pull이 필요합니다."
    git pull origin $CURRENT_BRANCH
fi
log_success "원격 저장소 동기화 완료"

# 3. 환경 변수 검증
log_step "3단계: GitHub Secrets 확인"
required_secrets=(
    "RAILWAY_TOKEN"
    "VERCEL_TOKEN" 
    "VERCEL_ORG_ID"
    "VERCEL_PROJECT_ID"
)

missing_secrets=()
echo "필수 GitHub Secrets:"
for secret in "${required_secrets[@]}"; do
    echo "  - $secret: 설정 필요"
done

log_warning "GitHub 저장소 설정에서 다음 Secrets가 설정되었는지 확인하세요"
echo ""

# 4. 로컬 사전 검증
log_step "4단계: 로컬 사전 검증"

# 백엔드 검증
if [[ -d "vridge_back" ]]; then
    log_info "백엔드 검증 중..."
    cd vridge_back
    
    if [[ -f "requirements.txt" ]]; then
        log_success "requirements.txt 존재"
    else
        log_error "requirements.txt가 없습니다"
        exit 1
    fi
    
    if [[ -f "manage.py" ]]; then
        log_success "Django manage.py 존재"
    else
        log_error "Django manage.py가 없습니다"
        exit 1
    fi
    
    if [[ -f "railway.json" ]]; then
        log_success "Railway 설정 존재"
    else
        log_warning "railway.json이 없습니다. Railway 배포가 실패할 수 있습니다."
    fi
    
    cd ..
fi

# 프론트엔드 검증
if [[ -d "vridge_front" ]]; then
    log_info "프론트엔드 검증 중..."
    cd vridge_front
    
    if [[ -f "package.json" ]]; then
        log_success "package.json 존재"
        
        # 필수 스크립트 확인
        if grep -q '"build"' package.json; then
            log_success "빌드 스크립트 존재"
        else
            log_error "빌드 스크립트가 없습니다"
            exit 1
        fi
    else
        log_error "package.json이 없습니다"
        exit 1
    fi
    
    if [[ -f "vercel.json" ]]; then
        log_success "Vercel 설정 존재"
    else
        log_warning "vercel.json이 없습니다. 기본 설정으로 배포됩니다."
    fi
    
    cd ..
fi

# 5. GitHub Actions 워크플로우 확인
log_step "5단계: GitHub Actions 워크플로우 확인"
if [[ -d ".github/workflows" ]]; then
    workflow_files=(
        "backend-ci.yml"
        "frontend-ci.yml" 
        "code-quality.yml"
    )
    
    for workflow in "${workflow_files[@]}"; do
        if [[ -f ".github/workflows/$workflow" ]]; then
            log_success "$workflow 존재"
        else
            log_warning "$workflow가 없습니다"
        fi
    done
else
    log_error "GitHub Actions 워크플로우 디렉토리가 없습니다"
    exit 1
fi

# 6. 배포 시작
log_step "6단계: GitHub Actions 배포 트리거"

if [[ "$ENVIRONMENT" == "production" ]] || [[ "$ENVIRONMENT" == "staging" ]]; then
    log_info "푸시를 통해 자동 배포를 시작합니다..."
    
    # 마지막 확인
    echo -e "${YELLOW}⚠️  다음 설정으로 배포됩니다:${NC}"
    echo "  - 브랜치: $CURRENT_BRANCH"
    echo "  - 환경: $ENVIRONMENT"
    echo "  - 백엔드: Railway"
    echo "  - 프론트엔드: Vercel"
    echo ""
    
    read -p "배포를 진행하시겠습니까? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_step "Git Push를 실행하여 배포를 시작합니다..."
        git push origin $CURRENT_BRANCH
        
        log_success "배포가 시작되었습니다!"
        
        # GitHub Actions 모니터링 링크 제공
        REPO_URL=$(git remote get-url origin | sed 's/\.git$//')
        if [[ $REPO_URL == git@github.com:* ]]; then
            REPO_URL=$(echo $REPO_URL | sed 's|git@github.com:|https://github.com/|')
        fi
        
        echo ""
        log_info "배포 진행 상황을 확인하세요:"
        echo "  🔗 GitHub Actions: $REPO_URL/actions"
        echo "  📊 워크플로우 상태:"
        echo "    - Backend CI/CD: $REPO_URL/actions/workflows/backend-ci.yml"
        echo "    - Frontend CI/CD: $REPO_URL/actions/workflows/frontend-ci.yml"
        echo "    - Code Quality: $REPO_URL/actions/workflows/code-quality.yml"
        
    else
        log_warning "배포가 취소되었습니다."
        exit 0
    fi
    
else
    # Feature 브랜치의 경우 PR 생성 안내
    log_info "Feature 브랜치 배포 프로세스:"
    echo "1. 현재 브랜치를 푸시합니다"
    echo "2. GitHub에서 Pull Request를 생성합니다"
    echo "3. 코드 리뷰 후 develop 브랜치로 머지합니다"
    echo ""
    
    read -p "현재 브랜치를 푸시하시겠습니까? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin $CURRENT_BRANCH
        log_success "브랜치가 푸시되었습니다."
        echo "GitHub에서 Pull Request를 생성하세요: $REPO_URL/compare"
    fi
fi

# 7. 배포 후 안내사항
echo ""
log_step "7단계: 배포 후 확인사항"
echo "배포가 완료되면 다음을 확인하세요:"
echo ""
echo "📋 체크리스트:"
echo "  □ GitHub Actions 워크플로우 모두 성공"
echo "  □ 백엔드 헬스체크 통과"
echo "  □ 프론트엔드 페이지 로드 확인"  
echo "  □ 주요 기능 동작 테스트"
echo "  □ 에러 로그 없음 확인"
echo ""

echo "🔗 모니터링 링크:"
echo "  - GitHub Actions: $REPO_URL/actions"
echo "  - Railway 대시보드: https://railway.app/dashboard"
echo "  - Vercel 대시보드: https://vercel.com/dashboard"
echo ""

echo "🚨 문제 발생 시:"
echo "  1. GitHub Actions 로그 확인"
echo "  2. 서비스 대시보드에서 로그 확인"  
echo "  3. ./scripts/emergency-rollback.sh 실행 (긴급 롤백)"
echo "  4. Slack #deployments 채널에 문의"
echo ""

log_success "GitHub 배포 스크립트가 완료되었습니다!"
echo -e "${CYAN}Happy Coding! 🚀${NC}"