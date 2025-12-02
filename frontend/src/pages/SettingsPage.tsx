import React from 'react'
import { Moon, Sun, AlertCircle } from 'lucide-react'
import { useStore } from '../store'

export default function SettingsPage() {
  const { darkMode, toggleDarkMode, selectedPlatform, setSelectedPlatform } = useStore()

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Settings</h1>
          <p className="text-slate-400">Customize your Hipe experience</p>
        </div>

        <div className="space-y-6">
          {/* Appearance Section */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Appearance</h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-white font-medium mb-1">Dark Mode</label>
                  <p className="text-slate-400 text-sm">
                    {darkMode ? 'Dark mode is enabled' : 'Dark mode is disabled'}
                  </p>
                </div>
                <button
                  onClick={toggleDarkMode}
                  className={`p-3 rounded-lg transition-colors ${
                    darkMode
                      ? 'bg-slate-700 text-yellow-400'
                      : 'bg-slate-700 text-blue-400'
                  }`}
                >
                  {darkMode ? <Moon size={20} /> : <Sun size={20} />}
                </button>
              </div>
            </div>
          </section>

          {/* Search Preferences */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Search Preferences</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-white font-medium mb-3">Default Platform</label>
                <div className="space-y-2">
                  {['All', 'X (Twitter)', 'Reddit'].map(platform => (
                    <label key={platform} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="radio"
                        name="defaultPlatform"
                        value={platform}
                        checked={selectedPlatform === platform}
                        onChange={(e) => setSelectedPlatform(e.target.value)}
                        className="w-4 h-4 rounded border-slate-600 text-blue-600 cursor-pointer"
                      />
                      <span className="text-slate-300">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Privacy Section */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Privacy</h2>

            <div className="space-y-4">
              <div className="flex items-start gap-3 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
                <AlertCircle size={20} className="text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-blue-300 text-sm">
                    Your search history is stored locally in your browser. No data is sent to external servers unless necessary for search functionality.
                  </p>
                </div>
              </div>

              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked={true}
                    className="w-4 h-4 rounded border-slate-600 text-blue-600 cursor-pointer"
                  />
                  <span className="text-slate-300">Save search history locally</span>
                </label>
              </div>

              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked={false}
                    className="w-4 h-4 rounded border-slate-600 text-blue-600 cursor-pointer"
                  />
                  <span className="text-slate-300">Allow analytics</span>
                </label>
              </div>
            </div>
          </section>

          {/* About Section */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">About</h2>

            <div className="space-y-3 text-slate-300 text-sm">
              <div>
                <span className="font-medium text-slate-200">Version</span>
                <p className="text-slate-400">1.0.0</p>
              </div>
              <div>
                <span className="font-medium text-slate-200">Built with</span>
                <p className="text-slate-400">React, TypeScript, Tailwind CSS</p>
              </div>
              <div className="pt-4 border-t border-slate-700">
                <p className="text-slate-400 text-xs">
                  © 2024 Hipe. All rights reserved.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
