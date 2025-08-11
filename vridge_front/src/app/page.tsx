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
              
            </Link>
            <Link
              href="/signup"
              className="btn-primary px-4 py-2 text-sm"
            >
              
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30">
        <div className="container mx-auto px-4 py-24">
          <div className="text-center">
            <h1 className="mb-6 text-5xl font-bold leading-tight text-gray-900">
                
              <br />
              <span className="text-gradient-brand">  </span>
            </h1>
            <p className="mx-auto mb-8 max-w-2xl text-xl text-gray-600">
               , VideoPlanet        .
            </p>
            <div className="flex items-center justify-center gap-4">
              <Link
                href="/signup"
                className="btn-primary inline-flex items-center gap-2 px-8 py-4 text-lg"
              >
                 
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="/demo"
                className="btn-secondary px-8 py-4 text-lg"
              >
                 
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
                  ?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                      .
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card p-8 text-center card-hover">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Video className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">AI  </h3>
              <p className="text-gray-600">
                AI        .
              </p>
            </div>

            <div className="card p-8 text-center card-hover">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4"> </h3>
              <p className="text-gray-600">
                      .
              </p>
            </div>

            <div className="card p-8 text-center card-hover">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4"> </h3>
              <p className="text-gray-600">
                  ,      .
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-brand-primary to-brand-primary-dark">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
             
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
               VideoPlanet   .
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 bg-white text-brand-primary px-8 py-4 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
          >
              
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
                      ,
                     .
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4"></h3>
              <ul className="space-y-2">
                <li><Link href="/features" className="hover:text-white"></Link></li>
                <li><Link href="/pricing" className="hover:text-white"></Link></li>
                <li><Link href="/demo" className="hover:text-white"></Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4"></h3>
              <ul className="space-y-2">
                <li><Link href="/help" className="hover:text-white"></Link></li>
                <li><Link href="/contact" className="hover:text-white"></Link></li>
                <li><Link href="/privacy" className="hover:text-white"></Link></li>
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