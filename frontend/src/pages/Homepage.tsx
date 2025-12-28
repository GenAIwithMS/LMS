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
      <section className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            <div className="flex items-center justify-center mb-6">
              <GraduationCap className="w-16 h-16 mr-4" />
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold">EduCore AI</h1>
            </div>
            <h1 className="text-xl sm:text-2xl mt-6 mb-10 text-primary-100 max-w-3xl mx-auto font-bold">
              The Intelligent Core of Academic Management.
            </h1>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
              <button
                onClick={() => navigate('/login')}
                className="btn bg-white text-primary-700 hover:bg-primary-50 px-8 py-3 text-lg font-semibold shadow-lg"
              >
                Login
              </button>
              <button
                onClick={() => {
                  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="btn bg-transparent border-2 border-white text-white hover:bg-white hover:text-primary-700 px-8 py-3 text-lg font-semibold"
              >
                Learn More
              </button>
            </div>
            <p className="text-sm text-primary-200 italic">
              Access restricted — only authorized users can log in.
            </p>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">The Problem We Solve</h2>
            <p className="text-lg text-gray-700 leading-relaxed">
              Educational institutions often struggle with fragmented data across multiple tools and spreadsheets. 
              This leads to inefficiency, data silos, and administrative overhead. <strong>EduCore AI</strong> centralizes 
              all academic management functions into one secure, intelligent platform, eliminating the need for 
              disconnected systems and providing a unified experience for administrators, teachers, and students.
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
                <div key={index} className="card hover:shadow-xl transition-shadow">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                        <Icon className="w-6 h-6 text-primary-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-gray-600">{feature.description}</p>
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
              return (
                <div key={index} className="card text-center">
                  <div className="flex justify-center mb-4">
                    <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                      <Icon className="w-8 h-8 text-primary-600" />
                    </div>
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-4">{role.title}</h3>
                  <ul className="space-y-2">
                    {role.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center justify-center text-gray-600">
                        <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                        {feature}
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
            <div className="flex items-start space-x-3">
              <Shield className="w-6 h-6 text-primary-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">JWT Authentication</h3>
                <p className="text-gray-600">Secure token-based authentication ensures only authorized access.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Shield className="w-6 h-6 text-primary-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Role-Based Permissions</h3>
                <p className="text-gray-600">Granular access control based on user roles and responsibilities.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Shield className="w-6 h-6 text-primary-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Data-Controlled Access</h3>
                <p className="text-gray-600">Users can only access data appropriate to their role and permissions.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Shield className="w-6 h-6 text-primary-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Secure Academic Environment</h3>
                <p className="text-gray-600">Enterprise-grade security measures protect sensitive academic data.</p>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-4">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm">
            <p>For institutional use only • © {currentYear} EduCore AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;

