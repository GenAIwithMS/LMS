import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Clock,
  FileText,
  TrendingUp,
  Bell,
  Bot,
  Shield,
  Lock,
  CheckCircle,
  ArrowRight,
  GraduationCap,
  Menu,
  X,
} from 'lucide-react';

const Homepage: React.FC = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    {
      icon: Users,
      title: 'Student & Teacher Management',
      description: 'Comprehensive user management system for admins to organize and manage all users efficiently.',
    },
    {
      icon: Clock,
      title: 'Attendance Tracking',
      description: 'Real-time attendance monitoring with detailed records and analytics for better student engagement.',
    },
    {
      icon: FileText,
      title: 'Assignments & Submissions',
      description: 'Streamlined assignment creation, distribution, and submission tracking for seamless workflow.',
    },
    {
      icon: TrendingUp,
      title: 'Results & Performance Analytics',
      description: 'Track student performance with detailed analytics and comprehensive result management.',
    },
    {
      icon: Bell,
      title: 'Announcements & Events',
      description: 'Keep everyone informed with targeted announcements and event management capabilities.',
    },
    {
      icon: Bot,
      title: 'Built-in AI Assistant',
      description: 'Get instant help with an intelligent AI assistant that understands your academic needs.',
    },
  ];

  const roles = [
    {
      title: 'Admins',
      icon: Shield,
      features: [
        'Manage users',
        'Control permissions',
        'Oversee institution',
      ],
    },
    {
      title: 'Teachers',
      icon: GraduationCap,
      features: [
        'Manage classes',
        'Assign work',
        'Record results & attendance',
      ],
    },
    {
      title: 'Students',
      icon: Users,
      features: [
        'Submit assignments',
        'View results',
        'Track progress',
      ],
    },
  ];

  const currentYear = new Date().getFullYear();

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="bg-white bg-opacity-70 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <GraduationCap className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">EduCore AI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button
                onClick={() => {
                  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Features
              </button>
              <button
                onClick={() => {
                  document.getElementById('roles')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Roles
              </button>
              <button
                onClick={() => {
                  document.getElementById('security')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Security
              </button>
            </div>
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-700 hover:text-primary-600"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
          {mobileMenuOpen && (
            <div className="md:hidden py-4 space-y-3 border-t">
              <button
                onClick={() => {
                  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                  setMobileMenuOpen(false);
                }}
                className="block w-full text-left text-gray-700 hover:text-primary-600 font-medium py-2"
              >
                Features
              </button>
              <button
                onClick={() => {
                  document.getElementById('roles')?.scrollIntoView({ behavior: 'smooth' });
                  setMobileMenuOpen(false);
                }}
                className="block w-full text-left text-gray-700 hover:text-primary-600 font-medium py-2"
              >
                Roles
              </button>
              <button
                onClick={() => {
                  document.getElementById('security')?.scrollIntoView({ behavior: 'smooth' });
                  setMobileMenuOpen(false);
                }}
                className="block w-full text-left text-gray-700 hover:text-primary-600 font-medium py-2"
              >
                Security
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary-500/20 to-transparent rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-primary-400/20 to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-28 sm:py-36">
          <div className="text-center">
            <div className="flex items-center justify-center mb-8 animate-fade-in-up">
              <div className="relative">
                <div className="absolute inset-0 bg-white/20 rounded-2xl blur-xl"></div>
                <GraduationCap className="relative w-20 h-20 mr-4 drop-shadow-2xl" />
              </div>
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight drop-shadow-lg">EduCore AI</h1>
            </div>
            <h2 className="text-2xl sm:text-3xl mt-6 mb-4 text-white max-w-3xl mx-auto font-bold animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              The Intelligent Core of Academic Management
            </h2>
            <p className="text-lg sm:text-xl text-primary-100 max-w-2xl mx-auto mb-12 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              Streamline your institution with AI-powered management, real-time insights, and seamless collaboration.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
              <button
                onClick={() => navigate('/login')}
                className="group relative btn bg-white text-primary-700 hover:bg-primary-50 px-10 py-4 text-lg font-semibold shadow-2xl hover:shadow-primary-500/50 hover:scale-105 transition-all duration-300"
              >
                <span className="relative z-10">Get Started</span>
                <ArrowRight className="inline-block ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => {
                  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="btn bg-transparent border-2 border-white text-white hover:bg-white/10 backdrop-blur-sm px-10 py-4 text-lg font-semibold hover:scale-105 transition-all duration-300"
              >
                Explore Features
              </button>
            </div>
            <p className="text-sm text-primary-200 italic flex items-center justify-center gap-2 animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
              <Lock className="w-4 h-4" />
              Secure access for authorized users only
            </p>
          </div>
        </div>
        {/* Wave divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg className="w-full h-16" viewBox="0 0 1200 120" preserveAspectRatio="none">
            <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z" fill="white"></path>
          </svg>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 bg-gradient-to-b from-white via-gray-50 to-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-block px-4 py-2 bg-red-50 text-red-600 rounded-full text-sm font-semibold mb-4">
              The Challenge
            </div>
            <h2 className="text-3xl sm:text-5xl font-bold text-gray-900 mb-6">Breaking Down Educational Barriers</h2>
            <p className="text-lg sm:text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
              Educational institutions face a <span className="text-gray-900 font-semibold">fragmented landscape</span> of disconnected tools, 
              scattered data, and inefficient workflows that slow down learning and administration.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white p-6 rounded-2xl border-2 border-red-100 hover:border-red-200 transition-all hover:shadow-lg group">
              <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <X className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Data Silos</h3>
              <p className="text-sm text-gray-600">Information trapped across spreadsheets and tools</p>
            </div>
            <div className="bg-white p-6 rounded-2xl border-2 border-red-100 hover:border-red-200 transition-all hover:shadow-lg group">
              <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <X className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Manual Overhead</h3>
              <p className="text-sm text-gray-600">Time-consuming administrative tasks</p>
            </div>
            <div className="bg-white p-6 rounded-2xl border-2 border-red-100 hover:border-red-200 transition-all hover:shadow-lg group">
              <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <X className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Poor Visibility</h3>
              <p className="text-sm text-gray-600">Lack of real-time insights and analytics</p>
            </div>
          </div>
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 p-8 sm:p-12 rounded-3xl border border-primary-200 shadow-xl">
            <div className="flex items-center justify-center mb-6">
              <div className="w-14 h-14 bg-primary-600 rounded-2xl flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
            </div>
            <h3 className="text-2xl sm:text-3xl font-bold text-center text-gray-900 mb-4">EduCore AI: The Unified Solution</h3>
            <p className="text-center text-gray-700 text-lg leading-relaxed max-w-2xl mx-auto">
              A <strong className="text-primary-700">single, intelligent platform</strong> that centralizes all academic management functions. 
              Experience seamless collaboration, real-time insights, and AI-powered assistance — all in one place.
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Key Features</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to manage your academic institution in one powerful platform
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={index} 
                  className="group relative card hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border-2 border-gray-100 hover:border-primary-200 overflow-hidden"
                >
                  {/* Gradient overlay on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary-50/0 to-primary-100/0 group-hover:from-primary-50/50 group-hover:to-primary-100/30 transition-all duration-300 -z-10"></div>
                  
                  <div className="relative">
                    <div className="flex-shrink-0 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                        <Icon className="w-7 h-7 text-primary-600" />
                      </div>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-primary-700 transition-colors">{feature.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                    <div className="mt-4 flex items-center text-primary-600 opacity-0 group-hover:opacity-100 transition-all duration-300 font-semibold text-sm">
                      Learn more <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Role-Based Access Section */}
      <section id="roles" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Role-Based Access</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Tailored experiences for different user roles with appropriate permissions and capabilities
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {roles.map((role, index) => {
              const Icon = role.icon;
              const colors = [
                { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'text-blue-600', gradient: 'from-blue-100 to-blue-200', hover: 'hover:border-blue-300' },
                { bg: 'bg-green-50', border: 'border-green-200', icon: 'text-green-600', gradient: 'from-green-100 to-green-200', hover: 'hover:border-green-300' },
                { bg: 'bg-purple-50', border: 'border-purple-200', icon: 'text-purple-600', gradient: 'from-purple-100 to-purple-200', hover: 'hover:border-purple-300' }
              ];
              const color = colors[index];
              return (
                <div key={index} className={`group card text-center border-2 ${color.border} ${color.hover} hover:shadow-2xl transition-all duration-300 hover:-translate-y-2`}>
                  <div className="flex justify-center mb-6">
                    <div className={`relative w-20 h-20 bg-gradient-to-br ${color.gradient} rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg`}>
                      <Icon className={`w-10 h-10 ${color.icon}`} />
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">{role.title}</h3>
                  <ul className="space-y-3">
                    {role.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center text-left text-gray-700 group/item hover:translate-x-2 transition-transform duration-200">
                        <div className={`w-6 h-6 ${color.bg} rounded-lg flex items-center justify-center mr-3 flex-shrink-0`}>
                          <CheckCircle className={`w-4 h-4 ${color.icon}`} />
                        </div>
                        <span className="font-medium">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section id="security" className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <Lock className="w-8 h-8 text-green-600" />
              </div>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Security & Trust</h2>
            <p className="text-lg text-gray-600">
              Built with security and privacy at its core
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="group flex items-start space-x-4 p-5 bg-white rounded-2xl border-2 border-green-100 hover:border-green-300 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-green-200 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-2 text-lg">JWT Authentication</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Secure token-based authentication ensures only authorized access to the platform.</p>
              </div>
            </div>
            <div className="group flex items-start space-x-4 p-5 bg-white rounded-2xl border-2 border-green-100 hover:border-green-300 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-green-200 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-2 text-lg">Role-Based Permissions</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Granular access control based on user roles and responsibilities.</p>
              </div>
            </div>
            <div className="group flex items-start space-x-4 p-5 bg-white rounded-2xl border-2 border-green-100 hover:border-green-300 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-green-200 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-2 text-lg">Data-Controlled Access</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Users can only access data appropriate to their role and permissions.</p>
              </div>
            </div>
            <div className="group flex items-start space-x-4 p-5 bg-white rounded-2xl border-2 border-green-100 hover:border-green-300 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-green-200 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-2 text-lg">Secure Academic Environment</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Enterprise-grade security measures protect sensitive academic data.</p>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* Footer */}
      <footer className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-300 py-12 overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYgMi42ODYgNiA2cy0yLjY4NiA2LTYgNi02LTIuNjg2LTYtNiAyLjY4Ni02IDYtNiIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utb3BhY2l0eT0iLjA1IiBzdHJva2Utd2lkdGg9IjEiLz48L2c+PC9zdmc+')] opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="font-bold text-white text-lg">EduCore AI</p>
                <p className="text-xs text-gray-400">Educational Excellence Platform</p>
              </div>
            </div>
            <div className="text-center md:text-right">
              <p className="text-sm text-gray-400">For institutional use only</p>
              <p className="text-xs text-gray-500 mt-1">© {currentYear} EduCore AI. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;

