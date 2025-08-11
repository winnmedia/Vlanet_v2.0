'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/Spinner';

interface UserSettings {
  profile: {
    name: string;
    email: string;
    avatar?: string;
    bio?: string;
  };
  notifications: {
    email: boolean;
    push: boolean;
    feedback: boolean;
    mentions: boolean;
  };
  privacy: {
    profilePublic: boolean;
    allowSearching: boolean;
    showActivity: boolean;
  };
  preferences: {
    language: string;
    theme: 'light' | 'dark' | 'auto';
    timezone: string;
  };
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await fetch('/api/users/me/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(localStorage.getItem('token') && {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            })
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const userData = await response.json();
        
        //     
        setSettings({
          profile: {
            name: userData.first_name || '',
            email: userData.email || '',
            bio: userData.bio || ''
          },
          notifications: {
            email: true,
            push: true,
            feedback: true,
            mentions: true
          },
          privacy: {
            profilePublic: false,
            allowSearching: true,
            showActivity: true
          },
          preferences: {
            language: 'ko',
            theme: 'light',
            timezone: 'Asia/Seoul'
          }
        });
      } catch (err) {
        console.error('Settings fetch error:', err);
        setError(err instanceof Error ? err.message : '   .');
        
        // Fallback 
        setSettings({
          profile: {
            name: '',
            email: 'user@example.com',
            bio: ''
          },
          notifications: {
            email: true,
            push: true,
            feedback: true,
            mentions: true
          },
          privacy: {
            profilePublic: false,
            allowSearching: true,
            showActivity: true
          },
          preferences: {
            language: 'ko',
            theme: 'light',
            timezone: 'Asia/Seoul'
          }
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSaveSettings = async () => {
    if (!settings) return;
    
    setSaving(true);
    try {
      const response = await fetch('/api/users/settings/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('token') && {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          })
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        alert(' .');
      } else {
        throw new Error('  .');
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : '    .');
    } finally {
      setSaving(false);
    }
  };

  const updateSettings = (section: keyof UserSettings, key: string, value: any) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [key]: value
      }
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
        <span className="ml-3 text-lg">  ...</span>
      </div>
    );
  }

  if (!settings) return null;

  const tabs = [
    { id: 'profile', name: '', icon: '' },
    { id: 'notifications', name: '', icon: '' },
    { id: 'privacy', name: '', icon: '' },
    { id: 'preferences', name: '', icon: '' }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">   .</p>
        
        {error && (
          <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700">
            <p className="font-medium"></p>
            <p>{error}</p>
            <p className="text-sm mt-1">  .</p>
          </div>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/*   */}
        <div className="lg:w-1/4">
          <Card className="p-4 bg-white shadow-sm">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </Card>
        </div>

        {/*   */}
        <div className="lg:w-3/4">
          <Card className="p-6 bg-white shadow-sm">
            {activeTab === 'profile' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4"> </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                    <input
                      type="text"
                      value={settings.profile.name}
                      onChange={(e) => updateSettings('profile', 'name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                    <input
                      type="email"
                      value={settings.profile.email}
                      onChange={(e) => updateSettings('profile', 'email', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                    <textarea
                      value={settings.profile.bio || ''}
                      onChange={(e) => updateSettings('profile', 'bio', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="  "
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4"> </h2>
                <div className="space-y-4">
                  {Object.entries(settings.notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        {key === 'email' ? ' ' :
                         key === 'push' ? ' ' :
                         key === 'feedback' ? ' ' : ' '}
                      </span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={(e) => updateSettings('notifications', key, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4"> </h2>
                <div className="space-y-4">
                  {Object.entries(settings.privacy).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        {key === 'profilePublic' ? ' ' :
                         key === 'allowSearching' ? ' ' : ' '}
                      </span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={(e) => updateSettings('privacy', key, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'preferences' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4"></h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                    <select
                      value={settings.preferences.language}
                      onChange={(e) => updateSettings('preferences', 'language', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="ko"></option>
                      <option value="en">English</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                    <select
                      value={settings.preferences.theme}
                      onChange={(e) => updateSettings('preferences', 'theme', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="light"></option>
                      <option value="dark"></option>
                      <option value="auto"></option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                    <select
                      value={settings.preferences.timezone}
                      onChange={(e) => updateSettings('preferences', 'timezone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Asia/Seoul">Asia/Seoul (KST)</option>
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">America/New_York (EST)</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={handleSaveSettings}
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {saving ? ' ...' : ' '}
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}