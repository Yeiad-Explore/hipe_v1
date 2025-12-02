import React from 'react'
import { Zap, Brain, Database } from 'lucide-react'

export default function AboutPage() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Synthesis',
      description: 'Intelligent multi-agent system that analyzes and synthesizes information from multiple sources'
    },
    {
      icon: Zap,
      title: 'Real-time Search',
      description: 'Search X (Twitter) and Reddit simultaneously to get the latest insights and discussions'
    },
    {
      icon: Database,
      title: 'Confidence Scoring',
      description: 'Get transparency metrics showing how confident the AI is in each answer'
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">About Hipe</h1>
          <p className="text-xl text-slate-400">
            AI-Powered Q&A Search Engine for Modern Information Discovery
          </p>
        </div>

        {/* Mission */}
        <section className="bg-slate-800 border border-slate-700 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-4">Our Mission</h2>
          <p className="text-slate-300 leading-relaxed mb-4">
            Hipe makes information discovery smarter by combining the power of artificial intelligence with real-time data from X (Twitter) and Reddit. We synthesize diverse perspectives and provide you with comprehensive, confidence-scored answers backed by multiple sources.
          </p>
          <p className="text-slate-300 leading-relaxed">
            In a world of information overload, Hipe cuts through the noise to bring you what matters most—multi-perspective insights with transparent confidence metrics.
          </p>
        </section>

        {/* Features */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-8">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon
              return (
                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                  <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4">
                    <Icon size={24} className="text-blue-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-slate-400 text-sm">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </section>

        {/* Technology */}
        <section className="bg-slate-800 border border-slate-700 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Technology Stack</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-white mb-3">Frontend</h3>
              <ul className="space-y-2 text-slate-300 text-sm">
                <li>• React 18 with TypeScript</li>
                <li>• Tailwind CSS for styling</li>
                <li>• Zustand for state management</li>
                <li>• Lucide React for icons</li>
                <li>• Vite for build tooling</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-3">Backend & AI</h3>
              <ul className="space-y-2 text-slate-300 text-sm">
                <li>• LangGraph for multi-agent orchestration</li>
                <li>• Azure OpenAI for LLM & embeddings</li>
                <li>• X API v2 via Tweepy</li>
                <li>• Reddit API via PRAW</li>
                <li>• ChromaDB for vector caching</li>
              </ul>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-8">How It Works</h2>
          <div className="space-y-4">
            {[
              { num: '1', title: 'Query Analysis', desc: 'AI analyzes your question to understand intent and extract key entities' },
              { num: '2', title: 'Intelligent Search', desc: 'Parallel searches across X and Reddit with smart platform selection' },
              { num: '3', title: 'Content Processing', desc: 'Results are ranked by semantic relevance and credibility' },
              { num: '4', title: 'Synthesis', desc: 'Multiple sources are synthesized into a coherent answer with confidence scoring' },
            ].map((step, idx) => (
              <div key={idx} className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                    {step.num}
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-white mb-1">{step.title}</h4>
                  <p className="text-slate-400 text-sm">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="bg-slate-800 border border-slate-700 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">FAQ</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-white mb-2">Is Hipe free to use?</h3>
              <p className="text-slate-400 text-sm">
                Yes! Hipe is designed to be accessible to everyone. We're continuously improving the service.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">How accurate are the answers?</h3>
              <p className="text-slate-400 text-sm">
                Hipe provides confidence scores for each answer based on source quality, information consistency, and recency. We recommend checking source links for critical information.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">Can I use Hipe offline?</h3>
              <p className="text-slate-400 text-sm">
                No, Hipe requires internet connectivity to search X and Reddit APIs. However, your search history is cached locally.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">What data does Hipe collect?</h3>
              <p className="text-slate-400 text-sm">
                We collect minimal data. Your search history is stored locally in your browser by default. You can disable this in settings.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
