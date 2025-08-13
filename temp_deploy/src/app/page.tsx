import { ArrowRight, Users, Zap, Video } from 'lucide-react';
import Link from 'next/link';
import { Logo } from '@/components/ui/Logo';

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Logo size="md" variant="default" />
          <nav className="flex items-center gap-6">
            <Link
              href="/login"
              className="text-sm font-medium text-gray-600 hover:text-gray-900"
            >
              로그인
            </Link>
            <Link
              href="/signup"
              className="btn-primary px-4 py-2 text-sm"
            >
              시작하기
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30">
        <div className="container mx-auto px-4 py-24">
          <div className="text-center">
            <h1 className="mb-6 text-5xl font-bold leading-tight text-gray-900">
              영상 제작을 위한
              <br />
              <span className="text-gradient-brand">완벽한 협업 플랫폼</span>
            </h1>
            <p className="mx-auto mb-8 max-w-2xl text-xl text-gray-600">
              기획부터 완성까지, VideoPlanet과 함께 더욱 효율적이고 창의적인 영상 제작 경험을 시작하세요.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Link
                href="/signup"
                className="btn-primary inline-flex items-center gap-2 px-8 py-4 text-lg"
              >
                무료로 시작하기
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="/demo"
                className="btn-secondary px-8 py-4 text-lg"
              >
                데모 보기
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              영상 제작이 이렇게 쉬워도 되나요?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              복잡한 영상 제작 과정을 단순하고 직관적으로 관리할 수 있습니다.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card p-8 text-center card-hover">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Video className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">AI 기반 기획</h3>
              <p className="text-gray-600">
                AI가 도와주는 스마트한 영상 기획으로 창의적 아이디어를 현실로 만들어보세요.
              </p>
            </div>

            <div className="card p-8 text-center card-hover">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">실시간 협업</h3>
              <p className="text-gray-600">
                팀원들과 실시간으로 피드백을 주고받으며 완벽한 결과물을 만들어가세요.
              </p>
            </div>

            <div className="card p-8 text-center card-hover">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">자동화 시스템</h3>
              <p className="text-gray-600">
                반복적인 작업은 자동화하고, 창작에만 집중할 수 있는 환경을 제공합니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-brand-primary to-brand-primary-dark">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            지금 시작해보세요
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            무료로 계정을 만들고 VideoPlanet의 강력한 기능들을 체험해보세요.
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 bg-white text-brand-primary px-8 py-4 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
          >
            무료 계정 만들기
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <Logo variant="white" size="lg" className="mb-4" />
              <p className="text-gray-400 max-w-md">
                영상 제작자들을 위한 통합 프로젝트 관리 플랫폼으로,
                창의적인 협업과 효율적인 제작 환경을 제공합니다.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">제품</h3>
              <ul className="space-y-2">
                <li><Link href="/features" className="hover:text-white">기능</Link></li>
                <li><Link href="/pricing" className="hover:text-white">요금제</Link></li>
                <li><Link href="/demo" className="hover:text-white">데모</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">지원</h3>
              <ul className="space-y-2">
                <li><Link href="/help" className="hover:text-white">도움말</Link></li>
                <li><Link href="/contact" className="hover:text-white">문의하기</Link></li>
                <li><Link href="/privacy" className="hover:text-white">개인정보처리방침</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500">
            <p>&copy; 2025 VideoPlanet. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}