import React from 'react';
import { Shield, Server, Cpu, FileText, CheckCircle2, History, LogIn, LogOut, Terminal, Radio } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: User | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  pendingApprovalsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenLogin,
  onLogout,
  pendingApprovalsCount,
}) => {
  const navItems = [
    { id: 'overview', label: 'Cluster Overview', icon: Cpu },
    { id: 'nodes', label: 'Compute Nodes', icon: Server },
    { id: 'submit', label: 'Submit Workload', icon: Terminal },
    { id: 'jobs', label: 'Job Queue', icon: FileText },
    { id: 'approvals', label: 'Approvals', icon: CheckCircle2, badge: pendingApprovalsCount },
    { id: 'audit', label: 'Audit Trail', icon: History },
  ];

  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Cluster Pulse */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-sky-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-sky-400 bg-clip-text text-transparent">
                  LocalCompute Commons
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <Radio className="w-3 h-3 animate-pulse" />
                  Live Mesh
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Privacy-Preserving Distributed Local AI</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`relative flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-slate-800 text-sky-400 border border-slate-700 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.badge && item.badge > 0 ? (
                    <span className="ml-1 px-1.5 py-0.5 text-xs font-bold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                      {item.badge}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </nav>

          {/* User Auth Info */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-sm font-semibold text-slate-200">{user.username}</span>
                  <span className="text-xs uppercase tracking-wider font-mono text-sky-400">{user.role}</span>
                </div>
                <button
                  onClick={onLogout}
                  title="Logout"
                  className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-rose-400 hover:bg-slate-700 transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={onOpenLogin}
                className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium bg-brand-600 hover:bg-brand-500 text-white transition shadow-sm glow-brand"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
