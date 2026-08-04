'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ProviderKey {
  id: number;
  provider: string;
  name: string;
  is_active: boolean;
  rate_limit_per_minute: number | null;
  requests_today: number;
  created_at: string;
}

interface UsageStats {
  total_requests: number;
  by_provider: Record<string, number>;
  today_requests: number;
}

const PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI', icon: '🟢' },
  { value: 'anthropic', label: 'Anthropic', icon: '🟠' },
  { value: 'google_ai', label: 'Google AI', icon: '🔵' },
  { value: 'groq', label: 'Groq', icon: '⚡' },
  { value: 'openrouter', label: 'OpenRouter', icon: '🌐' },
  { value: 'together_ai', label: 'Together AI', icon: '🤝' },
  { value: 'cerebras', label: 'Cerebras', icon: '🧠' },
  { value: 'mistral', label: 'Mistral', icon: '💨' },
  { value: 'deepseek', label: 'DeepSeek', icon: '🔍' },
];

export default function ProvidersPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<ProviderKey[]>([]);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newProvider, setNewProvider] = useState({
    provider: 'openai',
    name: '',
    api_key: '',
    rate_limit_per_minute: 60,
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    if (!storedToken) {
      router.push('/login');
      return;
    }
    setToken(storedToken);
    fetchProviders(storedToken);
    fetchUsage(storedToken);
  }, [router]);

  const fetchProviders = async (authToken: string) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/providers/list', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      if (res.ok) {
        const data = await res.json();
        setProviders(data);
      } else if (res.status === 401) {
        localStorage.removeItem('access_token');
        router.push('/login');
      }
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsage = async (authToken: string) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/providers/usage', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      if (res.ok) {
        const data = await res.json();
        setUsage(data);
      }
    } catch (error) {
      console.error('Failed to fetch usage:', error);
    }
  };

  const handleAddProvider = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    try {
      const res = await fetch('http://localhost:8000/api/v1/providers/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newProvider),
      });

      const data = await res.json();

      if (res.ok) {
        setMessage({ type: 'success', text: `✅ ${data.provider} key added successfully!` });
        setShowAddForm(false);
        setNewProvider({ provider: 'openai', name: '', api_key: '', rate_limit_per_minute: 60 });
        fetchProviders(token);
        fetchUsage(token);
      } else {
        setMessage({ type: 'error', text: `❌ ${data.detail}` });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '❌ Failed to add provider key' });
    }

    setTimeout(() => setMessage(null), 5000);
  };

  const handleToggleProvider = async (id: number) => {
    if (!token) return;

    try {
      const res = await fetch(`http://localhost:8000/api/v1/providers/${id}/toggle`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (res.ok) {
        fetchProviders(token);
        setMessage({ type: 'success', text: '✅ Provider status updated!' });
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (error) {
      console.error('Failed to toggle provider:', error);
    }
  };

  const handleDeleteProvider = async (id: number, providerName: string) => {
    if (!token) return;
    if (!confirm(`Are you sure you want to delete the ${providerName} API key?`)) return;

    try {
      const res = await fetch(`http://localhost:8000/api/v1/providers/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (res.ok) {
        fetchProviders(token);
        fetchUsage(token);
        setMessage({ type: 'success', text: '✅ Provider key deleted!' });
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (error) {
      console.error('Failed to delete provider:', error);
    }
  };

  const getProviderIcon = (provider: string) => {
    const found = PROVIDER_OPTIONS.find(p => p.value === provider);
    return found?.icon || '🔑';
  };

  const getProviderLabel = (provider: string) => {
    const found = PROVIDER_OPTIONS.find(p => p.value === provider);
    return found?.label || provider;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-xl">Loading providers...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← Back
            </button>
            <h1 className="text-2xl font-bold">🔑 API Keys Management</h1>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
          >
            {showAddForm ? 'Cancel' : '+ Add New Key'}
          </button>
        </div>
      </header>

      {/* Message */}
      {message && (
        <div className={`px-6 py-3 ${message.type === 'success' ? 'bg-green-900/50' : 'bg-red-900/50'}`}>
          {message.text}
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <div className="px-6 py-4">
          <form onSubmit={handleAddProvider} className="bg-gray-800 rounded-lg p-6 max-w-2xl">
            <h2 className="text-xl font-semibold mb-4">Add New API Key</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Provider</label>
                <select
                  value={newProvider.provider}
                  onChange={(e) => setNewProvider({ ...newProvider, provider: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {PROVIDER_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.icon} {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Key Name (optional)</label>
                <input
                  type="text"
                  value={newProvider.name}
                  onChange={(e) => setNewProvider({ ...newProvider, name: e.target.value })}
                  placeholder="e.g., My Production Key"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">API Key</label>
                <input
                  type="password"
                  value={newProvider.api_key}
                  onChange={(e) => setNewProvider({ ...newProvider, api_key: e.target.value })}
                  placeholder="sk-..."
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Rate Limit (requests/minute)</label>
                <input
                  type="number"
                  value={newProvider.rate_limit_per_minute}
                  onChange={(e) => setNewProvider({ ...newProvider, rate_limit_per_minute: parseInt(e.target.value) || 60 })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700 px-4 py-3 rounded-lg font-medium transition-colors"
              >
                Save API Key
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Usage Stats */}
      {usage && (
        <div className="px-6 py-4">
          <div className="grid grid-cols-3 gap-4 max-w-4xl">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-gray-400 text-sm">Total Requests</div>
              <div className="text-2xl font-bold">{usage.total_requests}</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-gray-400 text-sm">Today</div>
              <div className="text-2xl font-bold">{usage.today_requests}</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-gray-400 text-sm">Active Keys</div>
              <div className="text-2xl font-bold">{providers.filter(p => p.is_active).length} / {providers.length}</div>
            </div>
          </div>
        </div>
      )}

      {/* Providers List */}
      <div className="px-6 py-4">
        <h2 className="text-xl font-semibold mb-4">Your API Keys</h2>
        
        {providers.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-400">
            No API keys configured yet. Click &quot;+ Add New Key&quot; to get started.
          </div>
        ) : (
          <div className="grid gap-4 max-w-4xl">
            {providers.map((provider) => (
              <div
                key={provider.id}
                className={`bg-gray-800 rounded-lg p-4 border-l-4 ${
                  provider.is_active ? 'border-green-500' : 'border-gray-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getProviderIcon(provider.provider)}</span>
                    <div>
                      <div className="font-semibold">{getProviderLabel(provider.provider)}</div>
                      <div className="text-sm text-gray-400">{provider.name}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-400">Requests Today</div>
                      <div className="font-medium">{provider.requests_today}</div>
                    </div>
                    
                    <button
                      onClick={() => handleToggleProvider(provider.id)}
                      className={`px-3 py-1 rounded text-sm ${
                        provider.is_active
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-gray-600 hover:bg-gray-700'
                      }`}
                    >
                      {provider.is_active ? 'Active' : 'Inactive'}
                    </button>
                    
                    <button
                      onClick={() => handleDeleteProvider(provider.id, provider.provider)}
                      className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Guide */}
      <div className="px-6 py-4 mt-8">
        <div className="bg-gray-800 rounded-lg p-6 max-w-4xl">
          <h3 className="text-lg font-semibold mb-3">📖 How to Get API Keys</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-300">
            <div>
              <strong>🟢 OpenAI:</strong> Visit{' '}
              <a href="https://platform.openai.com/api-keys" target="_blank" className="text-blue-400 hover:underline">
                platform.openai.com
              </a>
            </div>
            <div>
              <strong>🟠 Anthropic:</strong> Visit{' '}
              <a href="https://console.anthropic.com" target="_blank" className="text-blue-400 hover:underline">
                console.anthropic.com
              </a>
            </div>
            <div>
              <strong>🔵 Google AI:</strong> Visit{' '}
              <a href="https://makersuite.google.com" target="_blank" className="text-blue-400 hover:underline">
                makersuite.google.com
              </a>
            </div>
            <div>
              <strong>⚡ Groq:</strong> Visit{' '}
              <a href="https://console.groq.com" target="_blank" className="text-blue-400 hover:underline">
                console.groq.com
              </a>
            </div>
            <div>
              <strong>🌐 OpenRouter:</strong> Visit{' '}
              <a href="https://openrouter.ai" target="_blank" className="text-blue-400 hover:underline">
                openrouter.ai
              </a>
            </div>
            <div>
              <strong>💨 Mistral:</strong> Visit{' '}
              <a href="https://console.mistral.ai" target="_blank" className="text-blue-400 hover:underline">
                console.mistral.ai
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
