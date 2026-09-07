import React, { useState } from 'react';
import { X, Lock, Shield, User as UserIcon, Check } from 'lucide-react';

interface LoginModalProps {
  onClose: () => void;
  onLogin: (username: string, password: string) => Promise<void>;
}

export const LoginModal: React.FC<LoginModalProps> = ({ onClose, onLogin }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('AdminLocalCompute2026!');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await onLogin(username, password);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePreset = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="glass-panel p-6 sm:p-8 rounded-2xl max-w-md w-full border border-sky-500/30">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-sky-400" />
            <h3 className="text-lg font-bold text-white">Sign In to LocalCompute</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="p-3 mb-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
            {error}
          </div>
        )}

        {/* Quick Role Demo Presets */}
        <div className="mb-5">
          <span className="text-xs text-slate-400 font-semibold block mb-2">
            Quick Select Demo Credentials:
          </span>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handlePreset('admin', 'AdminLocalCompute2026!')}
              className={`p-2 rounded-xl text-xs font-semibold border text-center transition ${
                username === 'admin'
                  ? 'bg-sky-500/20 border-sky-500 text-sky-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => handlePreset('operator1', 'OperatorPassword2026!')}
              className={`p-2 rounded-xl text-xs font-semibold border text-center transition ${
                username === 'operator1'
                  ? 'bg-sky-500/20 border-sky-500 text-sky-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              Operator
            </button>
            <button
              type="button"
              onClick={() => handlePreset('researcher1', 'ResearcherPassword2026!')}
              className={`p-2 rounded-xl text-xs font-semibold border text-center transition ${
                username === 'researcher1'
                  ? 'bg-sky-500/20 border-sky-500 text-sky-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              Researcher
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Username:
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Password:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500 font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl font-semibold text-sm bg-brand-600 hover:bg-brand-500 text-white transition shadow-md glow-brand disabled:opacity-50 mt-2"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};
