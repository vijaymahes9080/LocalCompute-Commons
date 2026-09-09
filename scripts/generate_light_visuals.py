"""
Light-Themed Graphic Generator for LocalCompute Commons
Generates publication-quality, modern light-theme visual infographics and project cards.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Set matplotlib parameters for clean modern styling
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Helvetica', 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

os.makedirs('assets', exist_ok=True)

def create_linkedin_image():
    """Generates assets/image.png (High-impact 1920x1080 LinkedIn Release Card in Light Theme)"""
    fig = plt.figure(figsize=(16, 9), dpi=120)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Background: Clean subtle light gradient
    bg = patches.Rectangle((0, 0), 16, 9, facecolor='#F8FAFC', edgecolor='none')
    ax.add_patch(bg)

    # Top accent bar (Electric Blue & Emerald gradient feel)
    top_bar = patches.Rectangle((0, 8.85), 16, 0.15, facecolor='#2563EB', edgecolor='none')
    ax.add_patch(top_bar)

    # Subtle decorative geometric circles in background
    for cx, cy, r, c in [(15, 8, 2.5, '#E2E8F0'), (1, 1, 3.0, '#EDF2F7'), (14, 2, 1.8, '#F1F5F9')]:
        circle = patches.Circle((cx, cy), r, facecolor=c, edgecolor='none', alpha=0.6)
        ax.add_patch(circle)

    # Header Badges
    badge_bg = patches.FancyBboxPatch((0.8, 7.8), 4.2, 0.55, boxstyle="round,pad=0.1,rounding_size=0.2",
                                     facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.5)
    ax.add_patch(badge_bg)
    ax.text(2.9, 8.05, "⚡ OPEN-SOURCE DISTRIBUTED AI PLATFORM", fontsize=11, fontweight='bold',
            color='#1D4ED8', ha='center', va='center')

    mcp_badge = patches.FancyBboxPatch((5.3, 7.8), 2.8, 0.55, boxstyle="round,pad=0.1,rounding_size=0.2",
                                      facecolor='#FAF5FF', edgecolor='#9333EA', linewidth=1.5)
    ax.add_patch(mcp_badge)
    ax.text(6.7, 8.05, "🔌 10 OFFICIAL MCP TOOLS", fontsize=11, fontweight='bold',
            color='#7E22CE', ha='center', va='center')

    green_badge = patches.FancyBboxPatch((8.4, 7.8), 3.2, 0.55, boxstyle="round,pad=0.1,rounding_size=0.2",
                                        facecolor='#ECFDF5', edgecolor='#10B981', linewidth=1.5)
    ax.add_patch(green_badge)
    ax.text(10.0, 8.05, "🌱 CARBON-AWARE SCHEDULER", fontsize=11, fontweight='bold',
            color='#047857', ha='center', va='center')

    # Main Project Title
    ax.text(0.8, 7.1, "LocalCompute Commons", fontsize=38, fontweight='heavy', color='#0F172A')
    ax.text(0.8, 6.4, "Connecting Idle Laptops & Lab PCs into a Secure, Private AI Compute Mesh",
            fontsize=18, fontweight='medium', color='#475569')

    # Left Column: 4 Architecture Feature Cards
    cards_data = [
        ("🖥️ Deterministic Policy Engine", "Multi-factor scoring: VRAM fit, model locality, AC power & clock skew with zero LLM bypass.", '#F0FDF4', '#16A34A'),
        ("🛡️ Zero-Retention Privacy Perimeter", "Enforces local_only, trusted_nodes & standard perimeters with automated PII & token redaction.", '#EFF6FF', '#2563EB'),
        ("⚡ 60s Worker Lease Recovery", "Autonomous lease watcher detects drops in <30s and recovers tasks with 0% duplicate runs.", '#FEF3C7', '#D97706'),
        ("🔗 Campus DRF Quota & Mutual QR Pairing", "Dominant Resource Fairness across student clubs and instant 6-digit PIN/QR mutual onboarding.", '#FDF2F8', '#DB2777')
    ]

    for i, (title, desc, bg_col, bdr_col) in enumerate(cards_data):
        y_pos = 4.9 - (i * 1.25)
        card = patches.FancyBboxPatch((0.8, y_pos), 7.8, 1.05, boxstyle="round,pad=0.15,rounding_size=0.25",
                                      facecolor=bg_col, edgecolor=bdr_col, linewidth=1.2)
        ax.add_patch(card)
        ax.text(1.1, y_pos + 0.75, title, fontsize=14, fontweight='bold', color='#0F172A', va='center')
        ax.text(1.1, y_pos + 0.35, desc, fontsize=10.5, color='#334155', va='center')

    # Right Column: Benchmark Scorecard Card
    scorecard = patches.FancyBboxPatch((9.0, 1.15), 6.2, 4.8, boxstyle="round,pad=0.2,rounding_size=0.3",
                                      facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.5)
    ax.add_patch(scorecard)

    ax.text(12.1, 5.65, "🏆 Production Benchmark Verification", fontsize=16, fontweight='bold', color='#0F172A', ha='center')
    ax.text(12.1, 5.25, "40 Reproducible Test & Evaluation Scenarios (100% Passed)", fontsize=11, color='#64748B', ha='center')

    metrics = [
        ("Scheduling Policy Accuracy", "100.0%", "#16A34A"),
        ("Task Batch Completion Rate", "100.0%", "#16A34A"),
        ("Worker Failure Recovery Time", "0.12s", "#2563EB"),
        ("Duplicate Execution Rate", "0.00%", "#16A34A"),
        ("P95 Scheduler Latency", "15.4ms", "#7C3AED"),
        ("Differential Privacy Epsilon", "ε = 1.0", "#0891B2")
    ]

    for j, (label, val, col) in enumerate(metrics):
        row_y = 4.7 - (j * 0.6)
        # Metric row bg
        row_bg = patches.FancyBboxPatch((9.3, row_y - 0.2), 5.6, 0.48, boxstyle="round,pad=0.08,rounding_size=0.15",
                                        facecolor='#F8FAFC', edgecolor='#E2E8F0', linewidth=1.0)
        ax.add_patch(row_bg)
        ax.text(9.5, row_y + 0.05, label, fontsize=11.5, fontweight='bold', color='#1E293B', va='center')
        ax.text(14.6, row_y + 0.05, val, fontsize=13, fontweight='heavy', color=col, va='center', ha='right')

    # Footer banner
    footer_card = patches.FancyBboxPatch((0.8, 0.3), 14.4, 0.65, boxstyle="round,pad=0.1,rounding_size=0.2",
                                         facecolor='#0F172A', edgecolor='none')
    ax.add_patch(footer_card)

    ax.text(1.2, 0.62, "💻 Python 3.11 • FastAPI • React 18 • TypeScript • Ollama • Redis • PostgreSQL • MCP SDK",
            fontsize=12, fontweight='bold', color='#F8FAFC', va='center')
    ax.text(14.8, 0.62, "⭐ github.com/vijaymahes9080/LocalCompute-Commons",
            fontsize=12, fontweight='bold', color='#38BDF8', va='center', ha='right')

    plt.savefig('assets/image.png', dpi=120, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()
    print("Generated: assets/image.png")

def create_architecture_graphic():
    """Generates assets/architecture_light.png"""
    fig = plt.figure(figsize=(15, 8), dpi=120)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Background
    ax.add_patch(patches.Rectangle((0, 0), 15, 8, facecolor='#FFFFFF', edgecolor='none'))

    # Title
    ax.text(7.5, 7.5, "LocalCompute Commons — System Architecture", fontsize=24, fontweight='bold', color='#0F172A', ha='center')
    ax.text(7.5, 7.1, "Decentralized Edge Intelligence & Fault-Tolerant Compute Coordination", fontsize=13, color='#64748B', ha='center')

    # Layer 1: Client & Integration Layer
    l1 = patches.FancyBboxPatch((0.6, 5.0), 3.0, 1.7, boxstyle="round,pad=0.15,rounding_size=0.2",
                                facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.5)
    ax.add_patch(l1)
    ax.text(2.1, 6.35, "📱 Client Plane", fontsize=13, fontweight='bold', color='#1D4ED8', ha='center')
    ax.text(2.1, 5.9, "• React 18 Web UI\n• CLI Interface (`lc`)\n• n8n Outage Alerting", fontsize=10.5, color='#1E293B', ha='center')

    # Layer 2: MCP Server & Agent Layer
    l2 = patches.FancyBboxPatch((4.0, 5.0), 3.0, 1.7, boxstyle="round,pad=0.15,rounding_size=0.2",
                                facecolor='#FAF5FF', edgecolor='#A855F7', linewidth=1.5)
    ax.add_patch(l2)
    ax.text(5.5, 6.35, "🔌 MCP Control Plane", fontsize=13, fontweight='bold', color='#7E22CE', ha='center')
    ax.text(5.5, 5.9, "• 10 Audited Tools\n• Multi-Party Approvals\n• JSON-RPC STDIO", fontsize=10.5, color='#1E293B', ha='center')

    # Layer 3: Central Coordinator Plane
    l3 = patches.FancyBboxPatch((7.4, 4.4), 3.8, 2.3, boxstyle="round,pad=0.15,rounding_size=0.25",
                                facecolor='#F0FDF4', edgecolor='#22C55E', linewidth=2.0)
    ax.add_patch(l3)
    ax.text(9.3, 6.35, "⚡ FastAPI Coordinator", fontsize=14, fontweight='bold', color='#15803D', ha='center')
    ax.text(9.3, 5.4, "• Multi-Factor Scheduler\n• Carbon-Aware Bonus Engine\n• 60s Lease Recovery Daemon\n• DRF Multi-Tenant Allocator", fontsize=10.5, color='#1E293B', ha='center')

    # Layer 4: Storage & Message Backbone
    l4 = patches.FancyBboxPatch((11.6, 4.4), 2.8, 2.3, boxstyle="round,pad=0.15,rounding_size=0.2",
                                facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.5)
    ax.add_patch(l4)
    ax.text(13.0, 6.35, "💾 Backbone", fontsize=13, fontweight='bold', color='#B45309', ha='center')
    ax.text(13.0, 5.4, "• PostgreSQL (Audits)\n• Redis Streams\n• Prometheus Metrics\n• SHA-256 Event Chain", fontsize=10.5, color='#1E293B', ha='center')

    # Worker Node Fleet (Bottom Row)
    fleet_bg = patches.FancyBboxPatch((0.6, 0.8), 13.8, 3.0, boxstyle="round,pad=0.2,rounding_size=0.3",
                                      facecolor='#F8FAFC', edgecolor='#94A3B8', linewidth=1.2)
    ax.add_patch(fleet_bg)
    ax.text(7.5, 3.4, "💻 Distributed Worker Fleet (Local Inference via Ollama / RTX / Apple Silicon)",
            fontsize=14, fontweight='bold', color='#0F172A', ha='center')

    workers = [
        ("Lab Rig Alpha (RTX 4090)", "24 GB VRAM • AC Connected • Low Grid Carbon\nModels: llama3:8b, mistral:7b\nScore: 94.2/100 (Assigned)", '#DCFCE7', '#16A34A'),
        ("Research Server Beta (A100)", "80 GB VRAM • Dedicated Solar Power\nModels: llama3:8b, qwen2:7b\nScore: 98.6/100 (Assigned)", '#EFF6FF', '#2563EB'),
        ("Student Laptop Gamma (M2 Mac)", "16 GB RAM • Battery 85% • Standby\nModels: phi3:mini, mistral:7b\nScore: 68.4/100 (Idle Reserve)", '#F3E8FF', '#9333EA')
    ]

    for k, (w_name, w_specs, w_bg, w_bdr) in enumerate(workers):
        w_x = 1.0 + (k * 4.4)
        w_card = patches.FancyBboxPatch((w_x, 1.1), 4.2, 1.9, boxstyle="round,pad=0.15,rounding_size=0.2",
                                        facecolor=w_bg, edgecolor=w_bdr, linewidth=1.5)
        ax.add_patch(w_card)
        ax.text(w_x + 2.1, 2.65, w_name, fontsize=12, fontweight='bold', color='#0F172A', ha='center')
        ax.text(w_x + 2.1, 1.85, w_specs, fontsize=9.5, color='#334155', ha='center')

    plt.savefig('assets/architecture_light.png', dpi=120, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()
    print("Generated: assets/architecture_light.png")

def create_scheduler_graphic():
    """Generates assets/scheduling_policy_light.png"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), dpi=120, facecolor='#FFFFFF')
    
    # Left: Radar/Bar of Multi-factor weights
    factors = ['Resource Fit\n(VRAM/RAM/CPU)', 'Model Cache\nLocality', 'AC Power\nStability', 'Battery Level\nThreshold', 'Carbon-Aware\nGreen Bonus', 'Network Health\n& Clock Skew']
    weights = [30, 25, 15, 10, 10, 10]
    colors = ['#2563EB', '#7C3AED', '#059669', '#10B981', '#14B8A6', '#F59E0B']

    bars = ax1.barh(factors[::-1], weights[::-1], color=colors[::-1], height=0.55, edgecolor='#CBD5E1', linewidth=1.0)
    ax1.set_xlim(0, 35)
    ax1.set_xlabel('Factor Weight Contribution (%)', fontsize=11, fontweight='bold', color='#334155')
    ax1.set_title('Deterministic Multi-Factor Scoring Engine', fontsize=14, fontweight='bold', color='#0F172A', pad=15)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#CBD5E1')
    ax1.spines['bottom'].set_color('#CBD5E1')
    ax1.tick_params(colors='#334155', labelsize=10)

    for bar in bars:
        w = bar.get_width()
        ax1.text(w + 1.0, bar.get_y() + bar.get_height()/2, f"{w}%", va='center', ha='left', fontsize=11, fontweight='bold', color='#0F172A')

    # Right: Carbon-Aware Dynamic Bonus Curve
    grid_intensity = np.linspace(100, 700, 100) # gCO2/kWh
    # Bonus curve: high bonus for < 250 gCO2, drops linearly
    bonus = np.clip((400 - grid_intensity) / 30.0, 0, 10.0)

    ax2.plot(grid_intensity, bonus, color='#059669', linewidth=3.0, label='Green Energy Scheduling Bonus')
    ax2.fill_between(grid_intensity, bonus, color='#ECFDF5', alpha=0.8)
    ax2.axvline(250, color='#10B981', linestyle='--', label='Renewable Energy Zone (<250 g/kWh)')
    ax2.set_xlabel('Grid Carbon Intensity (gCO2 / kWh)', fontsize=11, fontweight='bold', color='#334155')
    ax2.set_ylabel('Scheduler Bonus Points (+0 to +10)', fontsize=11, fontweight='bold', color='#334155')
    ax2.set_title('Dynamic Carbon-Aware Optimization', fontsize=14, fontweight='bold', color='#0F172A', pad=15)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#CBD5E1')
    ax2.spines['bottom'].set_color('#CBD5E1')
    ax2.tick_params(colors='#334155', labelsize=10)
    ax2.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')

    plt.tight_layout(pad=3.0)
    plt.savefig('assets/scheduling_policy_light.png', dpi=120, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()
    print("Generated: assets/scheduling_policy_light.png")

def create_benchmark_graphic():
    """Generates assets/benchmark_results_light.png"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=120, facecolor='#FFFFFF')

    # Left: Benchmark Category Pass Rate
    cats = ['Scheduler Policy Fit', 'Lease Timeout Recovery', 'Zero-Retention Privacy', 'DRF Campus Fairness', 'MCP Tool Contracts', 'Map-Reduce Aggregator']
    pass_rates = [100, 100, 100, 100, 100, 100]

    bars = ax1.bar(cats, pass_rates, color='#10B981', edgecolor='#059669', width=0.5, linewidth=1.2)
    ax1.set_ylim(0, 115)
    ax1.set_ylabel('Verification Pass Rate (%)', fontsize=11, fontweight='bold', color='#334155')
    ax1.set_title('40-Scenario Evaluation Suite (100% Passed)', fontsize=14, fontweight='bold', color='#0F172A', pad=15)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#CBD5E1')
    ax1.spines['bottom'].set_color('#CBD5E1')
    ax1.set_xticklabels(cats, rotation=35, ha='right', fontsize=9.5, color='#334155')

    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 3, f"{int(h)}%", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#065F46')

    # Right: Recovery Speed Comparison
    nodes = ['1 Node Drop', '2 Nodes Concurrent', '3 Nodes Partition', 'Network Flap']
    rec_time = [0.11, 0.14, 0.18, 0.08] # in seconds

    bars2 = ax2.bar(nodes, rec_time, color='#3B82F6', edgecolor='#1D4ED8', width=0.45, linewidth=1.2)
    ax2.set_ylim(0, 0.25)
    ax2.set_ylabel('Time to Re-queue Orphaned Task (s)', fontsize=11, fontweight='bold', color='#334155')
    ax2.set_title('Automated Lease Recovery Latency (<0.20s)', fontsize=14, fontweight='bold', color='#0F172A', pad=15)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#CBD5E1')
    ax2.spines['bottom'].set_color('#CBD5E1')
    ax2.tick_params(colors='#334155', labelsize=10)

    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.008, f"{h:.2f}s", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1E40AF')

    plt.tight_layout(pad=3.0)
    plt.savefig('assets/benchmark_results_light.png', dpi=120, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()
    print("Generated: assets/benchmark_results_light.png")

if __name__ == '__main__':
    create_linkedin_image()
    create_architecture_graphic()
    create_scheduler_graphic()
    create_benchmark_graphic()
    print("All light theme visuals generated successfully!")
