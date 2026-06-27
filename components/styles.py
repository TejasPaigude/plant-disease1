"""Centralized CSS for the premium Streamlit interface."""

import streamlit as st


def apply_global_styles():
    """Apply the project theme and component classes."""
    st.markdown(
        """
        <style>
        :root {
            --bg: #0d1117;
            --surface: #111827;
            --surface-2: #162033;
            --surface-3: #0f172a;
            --text: #f9fafb;
            --muted: #94a3b8;
            --muted-2: #64748b;
            --border: rgba(148, 163, 184, 0.22);
            --accent: #22c55e;
            --accent-2: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --cyan: #06b6d4;
            --shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
            --radius: 22px;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(34, 197, 94, 0.15), transparent 32rem),
                radial-gradient(circle at top right, rgba(59, 130, 246, 0.14), transparent 34rem),
                linear-gradient(135deg, #0d1117 0%, #101827 48%, #111827 100%);
            color: var(--text);
        }

        #MainMenu, header, footer {
            visibility: hidden;
        }

        .stApp {
            background: transparent;
        }

        [data-testid="stHeader"] {
            background: rgba(11, 18, 32, 0.72);
            backdrop-filter: blur(18px);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(17, 24, 39, 0.95));
            border-right: 1px solid rgba(148, 163, 184, 0.14);
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: var(--muted);
        }

        .block-container {
            max-width: 1240px;
            padding: 2.8rem 2.2rem 4rem;
        }

        h1, h2, h3, h4, h5, h6, p {
            letter-spacing: 0;
        }

        .top-title {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin: 8px 0 26px;
        }

        .top-title-icon {
            font-size: 2rem;
            line-height: 1;
            margin-bottom: 8px;
        }

        .top-title h1 {
            margin: 0;
            color: #16a34a;
            font-size: clamp(2.1rem, 4vw, 3rem);
            font-weight: 900;
            letter-spacing: 0.02em;
            text-shadow: 0 0 22px rgba(34, 197, 94, 0.18);
        }

        .top-title p {
            margin: 8px 0 0;
            color: rgba(203, 213, 225, 0.72);
            font-size: 0.95rem;
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 32px;
            padding: clamp(28px, 5vw, 56px);
            margin-bottom: 26px;
            background:
                linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(59, 130, 246, 0.13)),
                rgba(17, 24, 39, 0.78);
            box-shadow: var(--shadow);
        }

        .hero-shell:before {
            content: "";
            position: absolute;
            inset: -45%;
            background: conic-gradient(from 180deg, rgba(34,197,94,.28), rgba(59,130,246,.20), rgba(16,185,129,.22), rgba(34,197,94,.28));
            animation: soft-spin 16s linear infinite;
            opacity: 0.42;
            pointer-events: none;
        }

        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 850px;
        }

        .hero-centered {
            text-align: center;
        }

        .hero-centered .hero-content {
            margin: 0 auto;
        }

        .hero-centered .badge-row,
        .hero-centered .cta-row {
            justify-content: center;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 18px;
        }

        .soft-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 999px;
            padding: 7px 12px;
            color: #dbeafe;
            background: rgba(15, 23, 42, 0.68);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .hero-title {
            margin: 0;
            max-width: 980px;
            color: var(--text);
            font-size: clamp(2.35rem, 6vw, 4.7rem);
            line-height: 1.02;
            font-weight: 860;
        }

        .hero-gradient-text {
            background: linear-gradient(90deg, #86efac, #93c5fd 46%, #5eead4);
            -webkit-background-clip: text;
            color: transparent;
        }

        .hero-subtitle {
            max-width: 780px;
            margin: 18px 0 24px;
            color: #cbd5e1;
            font-size: clamp(1rem, 2vw, 1.2rem);
            line-height: 1.7;
        }

        .cta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }

        .primary-cta, .secondary-cta {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 42px;
            border-radius: 999px;
            padding: 0 18px;
            text-decoration: none !important;
            font-weight: 800;
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }

        .primary-cta {
            color: #04130a !important;
            background: linear-gradient(90deg, #22c55e, #86efac);
            box-shadow: 0 16px 40px rgba(34, 197, 94, 0.28);
        }

        .secondary-cta {
            color: #dbeafe !important;
            border: 1px solid rgba(147, 197, 253, 0.26);
            background: rgba(15, 23, 42, 0.68);
        }

        .primary-cta:hover, .secondary-cta:hover {
            transform: translateY(-2px);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin: 22px 0 16px;
        }

        .stat-card, .premium-card, .prediction-card, .upload-card, .info-card {
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.94), rgba(15, 23, 42, 0.88));
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.22);
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }

        .stat-card:hover, .premium-card:hover, .prediction-card:hover, .upload-card:hover, .info-card:hover {
            transform: translateY(-3px);
            border-color: rgba(34, 197, 94, 0.42);
            box-shadow: 0 22px 56px rgba(0, 0, 0, 0.28);
        }

        .stat-card {
            padding: 28px 22px;
            min-height: 150px;
            text-align: center;
            border-radius: 18px;
        }

        .stat-cyan {
            background: linear-gradient(135deg, #05c7d6, #0cb7bc);
            box-shadow: 0 18px 48px rgba(6, 182, 212, 0.22);
        }

        .stat-green {
            background: linear-gradient(135deg, #02b72d, #00991f);
            box-shadow: 0 18px 48px rgba(34, 197, 94, 0.22);
        }

        .stat-purple {
            background: linear-gradient(135deg, #a855f7, #7e22ce);
            box-shadow: 0 18px 48px rgba(168, 85, 247, 0.22);
        }

        .stat-orange {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.24), rgba(17, 24, 39, 0.92));
            box-shadow: 0 18px 48px rgba(245, 158, 11, 0.14);
        }

        .benefits-banner {
            margin: 0 0 38px;
            padding: 24px;
            border-radius: 18px;
            text-align: center;
            border: 1px solid rgba(245, 158, 11, 0.32);
            background: linear-gradient(90deg, rgba(245, 158, 11, 0.88), rgba(249, 115, 22, 0.82));
            box-shadow: 0 18px 50px rgba(245, 158, 11, 0.18);
        }

        .benefits-banner h3 {
            margin: 0 0 10px;
            color: #fff7ed;
            font-weight: 860;
        }

        .benefits-banner p {
            margin: 0;
            color: #fff7ed;
            font-weight: 750;
        }

        .stat-label {
            margin: 0 0 14px;
            color: rgba(255, 255, 255, 0.92);
            font-size: 0.95rem;
            font-weight: 800;
        }

        .stat-value {
            margin: 0;
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 860;
            line-height: 1.05;
        }

        .stat-note {
            margin: 18px 0 0;
            color: rgba(255, 255, 255, 0.82);
            font-size: 0.84rem;
            line-height: 1.45;
        }

        .section-kicker {
            color: #86efac;
            font-size: 0.78rem;
            font-weight: 850;
            text-transform: uppercase;
            margin: 12px 0 4px;
        }

        .section-divider {
            height: 1px;
            margin: 34px 0 38px;
            background: rgba(148, 163, 184, 0.18);
        }

        .section-heading {
            color: #16a34a;
            font-size: clamp(1.45rem, 3vw, 2.05rem);
            line-height: 1.16;
            margin: 0 0 18px;
            font-weight: 840;
        }

        .upload-card {
            padding: 0;
            min-height: auto;
            border: 0;
            background: transparent;
            box-shadow: none;
        }

        .compact-upload {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .upload-title, .card-title {
            color: var(--text);
            font-size: 1.12rem;
            font-weight: 840;
            margin: 0 0 8px;
        }

        .muted-copy {
            color: var(--muted);
            line-height: 1.55;
            font-size: 0.93rem;
        }

        .preview-frame {
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 20px;
            padding: 10px;
            background: rgba(2, 6, 23, 0.42);
            margin-top: 16px;
        }

        .prediction-card {
            padding: 22px;
            min-height: 128px;
        }

        .empty-result {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 82px;
            border: 1px solid rgba(6, 182, 212, 0.86);
            background: rgba(8, 36, 43, 0.38);
        }

        .empty-result p {
            margin: 0;
            color: #67e8f9;
            font-weight: 750;
        }

        .prediction-name {
            color: var(--text);
            font-size: clamp(1.4rem, 4vw, 2rem);
            line-height: 1.16;
            margin: 4px 0 10px;
            font-weight: 860;
        }

        .status-pill {
            display: inline-flex;
            border-radius: 999px;
            padding: 7px 11px;
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
        }

        .status-ok {
            color: #bbf7d0;
            background: rgba(34, 197, 94, 0.13);
            border: 1px solid rgba(34, 197, 94, 0.38);
        }

        .status-warning {
            color: #fde68a;
            background: rgba(245, 158, 11, 0.13);
            border: 1px solid rgba(245, 158, 11, 0.42);
        }

        .status-info {
            color: #bfdbfe;
            background: rgba(59, 130, 246, 0.13);
            border: 1px solid rgba(59, 130, 246, 0.38);
        }

        .rank-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-top: 14px;
        }

        .rank-card {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 15px;
            background: rgba(15, 23, 42, 0.74);
            min-height: 142px;
        }

        .rank-title {
            color: var(--text);
            font-weight: 800;
            font-size: 0.94rem;
            line-height: 1.35;
            margin: 8px 0 4px;
        }

        .confidence-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin: 18px 0 6px;
        }

        .confidence-number {
            color: var(--accent);
            font-size: 1.4rem;
            font-weight: 860;
        }

        .advisory-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin-top: 16px;
        }

        .info-card {
            padding: 18px;
            min-height: 180px;
        }

        .info-card ul {
            margin: 10px 0 0;
            padding-left: 1.1rem;
            color: #cbd5e1;
            line-height: 1.55;
        }

        .gradcam-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
        }

        .footer {
            margin-top: 42px;
            padding: 22px;
            border-top: 1px solid rgba(148, 163, 184, 0.15);
            color: var(--muted);
            text-align: center;
            font-size: 0.88rem;
        }

        .tech-row {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 9px;
            margin-top: 14px;
        }

        .tech-chip {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 999px;
            padding: 8px 11px;
            color: #dbeafe;
            background: rgba(15, 23, 42, 0.72);
            font-weight: 750;
        }

        .about-card {
            margin-top: 44px;
            padding: clamp(24px, 4vw, 38px);
            text-align: center;
            border: 2px solid rgba(6, 182, 212, 0.72);
            border-radius: 24px;
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.92), rgba(13, 17, 23, 0.90));
            box-shadow: 0 20px 58px rgba(6, 182, 212, 0.12);
        }

        .about-card h2 {
            margin: 0 0 12px;
            color: var(--text);
            font-weight: 860;
        }

        .about-card > p {
            max-width: 780px;
            margin: 0 auto 20px;
            color: var(--muted);
            line-height: 1.65;
        }

        .about-stats {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-top: 18px;
            text-align: left;
        }

        .sidebar-brand {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            padding: 18px;
            margin-bottom: 16px;
            background: rgba(2, 6, 23, 0.26);
        }

        .sidebar-logo {
            width: 42px;
            height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            color: #052e16;
            background: linear-gradient(135deg, #22c55e, #93c5fd);
            font-weight: 900;
            margin-bottom: 12px;
        }

        .sidebar-title {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 850;
            margin: 0;
        }

        .sidebar-subtitle {
            color: var(--muted);
            font-size: 0.84rem;
            margin: 5px 0 0;
            line-height: 1.45;
        }

        .side-nav {
            display: grid;
            gap: 8px;
            margin: 12px 0 20px;
        }

        .side-nav span {
            display: block;
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.13);
            color: #cbd5e1 !important;
            font-weight: 700;
        }

        div[data-testid="stFileUploader"] {
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 8px;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.06);
            transition: border-color .18s ease, background .18s ease;
        }

        div[data-testid="stFileUploader"]:hover {
            border-color: rgba(34, 197, 94, 0.85);
            background: rgba(34, 197, 94, 0.07);
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #22c55e, #3b82f6);
        }

        @keyframes soft-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        @media (max-width: 980px) {
            .stats-grid,
            .about-stats,
            .rank-grid,
            .advisory-grid,
            .gradcam-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 720px) {
            .block-container {
                padding: 2rem 1rem 3rem;
            }

            .hero-shell {
                padding: 28px 22px;
                border-radius: 24px;
            }

            .stats-grid,
            .about-stats,
            .rank-grid,
            .advisory-grid,
            .gradcam-grid {
                grid-template-columns: 1fr;
            }

            .upload-card,
            .prediction-card {
                min-height: auto;
                padding: 20px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
