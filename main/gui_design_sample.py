from flask import Flask, request, send_file, send_from_directory, render_template_string
import requests
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = PROJECT_ROOT / "img"

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Capstone Web Archiver</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --card-bg: rgba(255, 255, 255, 0.90);
            --text-main: #1f2a44;
            --text-muted: #5b6780;
            --brand-start: #4f46e5;
            --brand-end: #06b6d4;
            --success: #16a34a;
            --shadow: 0 20px 45px rgba(22, 34, 66, 0.20);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: "Inter", "Segoe UI", Roboto, Arial, sans-serif;
            color: var(--text-main);
            background-image:
                linear-gradient(120deg, rgba(245, 247, 255, 0.78), rgba(235, 255, 250, 0.82)),
                url("/img/backgrounds/home.png");
            background-size: cover;
            background-position: center;
            padding: 24px;
        }

        .page-shell {
            width: min(1400px, 100%);
            margin: 0 auto;
            display: grid;
            grid-template-columns: 220px minmax(0, 860px) 220px;
            gap: 24px;
            align-items: stretch;
        }

        .app-card {
            width: 100%;
            background: var(--card-bg);
            border-radius: 20px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.55);
            padding: 32px;
            backdrop-filter: blur(2px);
        }

        .side-panel {
            background: rgba(255, 255, 255, 0.88);
            border-radius: 20px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.6);
            padding: 24px 18px;
            backdrop-filter: blur(2px);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 100%;
        }

        .side-title {
            margin: 0 0 8px;
            font-size: 18px;
        }

        .side-copy {
            margin: 0 0 20px;
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
        }

        .vertical-progress {
            display: grid;
            grid-template-columns: 18px 1fr;
            gap: 14px;
            align-items: start;
            flex: 1;
        }

        .vertical-progress.right {
            grid-template-columns: 1fr 18px;
        }

        .vertical-track {
            position: relative;
            height: 320px;
            width: 12px;
            border-radius: 999px;
            background: #e6ebff;
            overflow: hidden;
            margin: 4px auto 0;
        }

        .vertical-fill {
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            height: 10%;
            border-radius: 999px;
            background: linear-gradient(180deg, var(--brand-start), var(--brand-end));
        }

        .vertical-progress.right .vertical-fill {
            background: linear-gradient(180deg, var(--brand-start), var(--brand-end));
        }

        .vertical-steps {
            display: flex;
            flex-direction: column;
            gap: 18px;
        }

        .vertical-step {
            padding: 12px 14px;
            border-radius: 16px;
            background: #f5f7ff;
            border: 1px solid #e4e9fb;
            color: var(--text-muted);
            font-size: 13px;
            line-height: 1.5;
        }

        .vertical-step b {
            display: block;
            margin-bottom: 4px;
            color: var(--text-main);
            font-size: 14px;
        }

        .vertical-step.current {
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.12), rgba(6, 182, 212, 0.12));
            border-color: rgba(79, 70, 229, 0.25);
            color: #2f3a56;
        }

        .badge {
            display: inline-block;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #0f766e;
            background: #ccfbf1;
            padding: 8px 12px;
            border-radius: 999px;
            margin-bottom: 14px;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 18px;
        }

        .topbar-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .nav-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(79, 70, 229, 0.08);
            color: #4338ca;
            font-size: 14px;
            font-weight: 700;
            text-decoration: none;
        }

        .progress-panel {
            margin: 10px 0 24px;
            padding: 18px;
            border-radius: 18px;
            background: rgba(248, 250, 255, 0.92);
            border: 1px solid #e4e9fb;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 14px;
            font-weight: 700;
        }

        .progress-left {
            color: var(--text-main);
        }

        .progress-right {
            color: #4338ca;
        }

        .progress-track {
            width: 100%;
            height: 12px;
            border-radius: 999px;
            background: #e6ebff;
            overflow: hidden;
            margin-bottom: 14px;
        }

        .progress-fill {
            width: 10%;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--brand-start), var(--brand-end));
        }

        .progress-milestones {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .progress-step {
            padding: 10px 14px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 700;
            color: #3730a3;
            background: #eef2ff;
        }

        .progress-step.current {
            color: #ffffff;
            background: linear-gradient(135deg, var(--brand-start), var(--brand-end));
            box-shadow: 0 10px 22px rgba(79, 70, 229, 0.22);
        }

        h1 {
            margin: 0;
            font-size: clamp(28px, 4vw, 42px);
            line-height: 1.15;
        }

        .subtitle {
            margin: 14px 0 26px;
            color: var(--text-muted);
            font-size: 16px;
            line-height: 1.6;
            max-width: 700px;
        }

        .input-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
        }

        input[type="url"] {
            width: 100%;
            border: 1px solid #d7def0;
            border-radius: 12px;
            padding: 14px 16px;
            font-size: 15px;
            color: var(--text-main);
            outline: none;
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }

        input[type="url"]:focus {
            border-color: #7c8cff;
            box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12);
        }

        button[type="submit"] {
            border: none;
            border-radius: 12px;
            padding: 0 22px;
            font-size: 15px;
            font-weight: 700;
            color: #fff;
            background: linear-gradient(135deg, var(--brand-start), var(--brand-end));
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        button[type="submit"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(79, 70, 229, 0.28);
        }

        .highlights {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-top: 24px;
        }

        .feature {
            background: #f8fafc;
            border: 1px solid #e8eefb;
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 14px;
            color: var(--text-muted);
        }

        .feature b {
            color: var(--text-main);
        }

        .notice {
            margin-top: 16px;
            color: var(--success);
            font-size: 13px;
            font-weight: 600;
        }

        .credits-card {
            margin-top: 24px;
            padding: 20px;
            border-radius: 16px;
            background: #f8fbff;
            border: 1px solid #e4e9fb;
        }

        .credits-card h2 {
            margin: 0 0 10px;
            font-size: 22px;
        }

        .credits-card p {
            margin: 0 0 14px;
            color: var(--text-muted);
            line-height: 1.6;
        }

        .member-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
        }

        .member-chip {
            padding: 14px;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid #e7ecfb;
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.5;
        }

        .member-chip b {
            display: block;
            color: var(--text-main);
            margin-bottom: 4px;
        }

        @media (max-width: 1100px) {
            .page-shell {
                grid-template-columns: 1fr;
            }

            .side-panel {
                order: 2;
            }
        }

        @media (max-width: 720px) {
            .app-card {
                padding: 24px;
            }

            .input-row {
                grid-template-columns: 1fr;
            }

            button[type="submit"] {
                height: 46px;
            }

            .highlights {
                grid-template-columns: 1fr;
            }

            .member-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="page-shell">
        <aside class="side-panel">
            <div>
                <h2 class="side-title">Left progress bar</h2>
                <p class="side-copy">The capstone is currently in the proposal stage, so the vertical bar highlights the first milestone.</p>
            </div>
            <div class="vertical-progress">
                <div class="vertical-track">
                    <div class="vertical-fill"></div>
                </div>
                <div class="vertical-steps">
                    <div class="vertical-step current"><b>Proposal</b>Problem framing, scope, and initial planning.</div>
                    <div class="vertical-step"><b>Progress Report</b>Implementation evidence and mid-project findings.</div>
                    <div class="vertical-step"><b>Presentation</b>Demonstration, communication, and defense.</div>
                    <div class="vertical-step"><b>Final Delivery</b>Report, evaluation, and complete deliverables.</div>
                </div>
            </div>
        </aside>

        <main class="app-card">
            <div class="topbar">
                <span class="badge">CS15-2 Capstone Service</span>
                <div class="topbar-links">
                    <a class="nav-link" href="/about">About Project</a>
                    <a class="nav-link" href="/references">References</a>
                </div>
            </div>
            <section class="progress-panel">
                <div class="progress-header">
                    <span class="progress-left">Current phase: Proposal</span>
                    <span class="progress-right">10% complete</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-milestones">
                    <span class="progress-step current">Proposal 10%</span>
                    <span class="progress-step">Progress Report 10%</span>
                    <span class="progress-step">Presentation 15%</span>
                    <span class="progress-step">Final Report / Deliverables 65%</span>
                </div>
            </section>
            <h1>Multimodal Fake News Analysis Web Archiver</h1>
            <p class="subtitle">
                Save a target page as an MHTML archive to support reproducible collection and analysis workflows
                for text-and-visual misinformation research.
            </p>

            <form method="post" action="/save">
                <div class="input-row">
                    <input type="url" name="url" placeholder="https://example.com/article" required>
                    <button type="submit">Save as MHTML</button>
                </div>
            </form>

            <section class="highlights">
                <div class="feature"><b>Fast capture</b><br>One-click archiving from URL input.</div>
                <div class="feature"><b>Research-ready</b><br>Preserves page structure for later analysis.</div>
                <div class="feature"><b>Simple workflow</b><br>Download output immediately after fetch.</div>
            </section>
            <p class="notice">Tip: Include the full URL with http:// or https://</p>
            <section class="credits-card">
                <h2>Project credits</h2>
                <p>Team members extracted from the proposal document, including student IDs and proposal-stage responsibilities.</p>
                <div class="member-grid">
                    <div class="member-chip"><b>Frank Shi</b>540435478<br>Crawler developer and data support.</div>
                    <div class="member-chip"><b>Han Li</b>500047446<br>Technical implementation, crawling, and dataset storage.</div>
                    <div class="member-chip"><b>Yaning Chen</b>540482069<br>Literature review lead, research analysis, and data support.</div>
                    <div class="member-chip"><b>Tianze Xu</b>490040016<br>Librarian and meeting-record maintainer.</div>
                    <div class="member-chip"><b>Yuqing Yang</b>530194981<br>Altmetric retrieval, cleaning, and structured output delivery.</div>
                    <div class="member-chip"><b>Haobo Zhao</b>540654057<br>Pipeline integration and system execution.</div>
                    <div class="member-chip"><b>Ruicheng Zhang</b>490030501<br>Team leader, coordinator, and client communicator.</div>
                    <div class="member-chip"><b>Nho Thanh Le</b>530832278<br>Document review, web UI, backend, and pipeline support.</div>
                </div>
            </section>
        </main>

        <aside class="side-panel">
            <div>
                <h2 class="side-title">Right progress bar</h2>
                <p class="side-copy">This side bar mirrors the capstone path and keeps the current milestone visible beside the main content.</p>
            </div>
            <div class="vertical-progress right">
                <div class="vertical-steps">
                    <div class="vertical-step current"><b>10%</b>Proposal is active right now.</div>
                    <div class="vertical-step"><b>20%</b>Progress report checkpoint after early build work.</div>
                    <div class="vertical-step"><b>35%</b>Presentation milestone for communicating results.</div>
                    <div class="vertical-step"><b>100%</b>Final report and deliverables complete the project.</div>
                </div>
                <div class="vertical-track">
                    <div class="vertical-fill"></div>
                </div>
            </div>
        </aside>
    </div>
</body>
</html>
"""


About_page = """    
<!doctype html>
<html>
<head>
    <title>About the Capstone Project</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --page-bg: #f4f7ff;
            --text-main: #1f2a44;
            --text-muted: #58657d;
            --panel: rgba(255, 255, 255, 0.92);
            --line: #dfe7fb;
            --brand: #4338ca;
            --accent: #0891b2;
            --shadow: 0 20px 45px rgba(22, 34, 66, 0.12);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Inter", "Segoe UI", Roboto, Arial, sans-serif;
            color: var(--text-main);
            background:
                linear-gradient(180deg, rgba(248, 250, 255, 0.92), rgba(235, 250, 248, 0.94)),
                url("/img/backgrounds/home.png") center/cover fixed;
        }

        .page-shell {
            width: min(1540px, 100%);
            margin: 0 auto;
            padding: 28px 20px 48px;
            display: grid;
            grid-template-columns: 220px minmax(0, 1080px) 220px;
            gap: 20px;
            align-items: start;
        }

        .page {
            width: 100%;
        }

        .hero,
        .section {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 22px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(3px);
        }

        .hero {
            padding: 28px;
            margin-bottom: 18px;
        }

        .side-panel {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.75);
            border-radius: 22px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(3px);
            padding: 22px 18px;
            position: sticky;
            top: 28px;
        }

        .side-title {
            margin: 0 0 8px;
            font-size: 18px;
        }

        .side-copy {
            margin: 0 0 18px;
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
        }

        .vertical-progress {
            display: grid;
            grid-template-columns: 18px 1fr;
            gap: 14px;
            align-items: start;
        }

        .vertical-progress.right {
            grid-template-columns: 1fr 18px;
        }

        .vertical-track {
            position: relative;
            height: 320px;
            width: 12px;
            border-radius: 999px;
            background: #e6ebff;
            overflow: hidden;
            margin: 4px auto 0;
        }

        .vertical-fill {
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            height: 10%;
            border-radius: 999px;
            background: linear-gradient(180deg, var(--brand), var(--accent));
        }

        .vertical-progress.right .vertical-fill {
            background: linear-gradient(180deg, var(--brand), var(--accent));
        }

        .vertical-steps {
            display: flex;
            flex-direction: column;
            gap: 18px;
        }

        .vertical-step {
            padding: 12px 14px;
            border-radius: 16px;
            background: #f5f7ff;
            border: 1px solid var(--line);
            color: var(--text-muted);
            font-size: 13px;
            line-height: 1.5;
        }

        .vertical-step b {
            display: block;
            margin-bottom: 4px;
            color: var(--text-main);
            font-size: 14px;
        }

        .vertical-step.current {
            background: linear-gradient(135deg, rgba(67, 56, 202, 0.12), rgba(8, 145, 178, 0.12));
            border-color: rgba(67, 56, 202, 0.22);
            color: #2f3a56;
        }

        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
        }

        .eyebrow {
            display: inline-block;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #155e75;
            background: #cffafe;
        }

        .nav a {
            text-decoration: none;
            color: var(--brand);
            font-weight: 700;
        }

        .progress-panel {
            margin: 8px 0 24px;
            padding: 18px;
            border-radius: 18px;
            background: #f8fbff;
            border: 1px solid var(--line);
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 14px;
            font-weight: 700;
        }

        .progress-left {
            color: var(--text-main);
        }

        .progress-right {
            color: var(--brand);
        }

        .progress-track {
            width: 100%;
            height: 12px;
            border-radius: 999px;
            background: #e6ebff;
            overflow: hidden;
            margin-bottom: 14px;
        }

        .progress-fill {
            width: 10%;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--brand), var(--accent));
        }

        .progress-milestones {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .progress-step {
            padding: 10px 14px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 700;
            color: #3730a3;
            background: #eef2ff;
        }

        .progress-step.current {
            color: #fff;
            background: linear-gradient(135deg, var(--brand), var(--accent));
            box-shadow: 0 10px 22px rgba(67, 56, 202, 0.18);
        }

        h1 {
            margin: 0 0 12px;
            font-size: clamp(30px, 4.6vw, 46px);
            line-height: 1.1;
        }

        .lead {
            margin: 0;
            color: var(--text-muted);
            font-size: 17px;
            line-height: 1.7;
            max-width: 820px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
            margin-bottom: 18px;
        }

        .section {
            padding: 24px;
        }

        h2 {
            margin: 0 0 12px;
            font-size: 22px;
        }

        p {
            margin: 0 0 12px;
            color: var(--text-muted);
            line-height: 1.7;
        }

        ul {
            margin: 0;
            padding-left: 20px;
            color: var(--text-muted);
        }

        li {
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .full-width {
            margin-bottom: 18px;
        }

        .three-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin-bottom: 18px;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 16px;
        }

        .pill {
            padding: 10px 14px;
            border-radius: 999px;
            background: #eef2ff;
            color: #3730a3;
            font-size: 14px;
            font-weight: 700;
        }

        .timeline {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-top: 16px;
        }

        .step {
            padding: 16px;
            border-radius: 16px;
            border: 1px solid var(--line);
            background: #f8fbff;
        }

        .step b {
            display: block;
            margin-bottom: 6px;
            color: var(--text-main);
        }

        .muted {
            color: var(--text-muted);
        }

        .two-column-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
        }

        .scope-box {
            padding: 18px;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: #f8fbff;
        }

        .scope-box h3 {
            margin: 0 0 12px;
            font-size: 18px;
        }

        .artifact-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 16px;
        }

        .artifact {
            padding: 16px;
            border-radius: 16px;
            border: 1px solid var(--line);
            background: #f9fbff;
        }

        .artifact b {
            display: block;
            margin-bottom: 6px;
        }

        .tag {
            display: inline-block;
            margin-top: 8px;
            padding: 6px 10px;
            border-radius: 999px;
            background: #ecfeff;
            color: var(--accent);
            font-size: 12px;
            font-weight: 700;
        }

        .credits-board {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 16px;
        }

        .credit-item {
            padding: 16px;
            border-radius: 16px;
            border: 1px solid var(--line);
            background: #f9fbff;
            color: var(--text-muted);
            line-height: 1.6;
        }

        .credit-item b {
            display: block;
            margin-bottom: 4px;
            color: var(--text-main);
        }

        @media (max-width: 860px) {
            .page-shell,
            .grid,
            .timeline,
            .three-grid,
            .two-column-list,
            .artifact-list,
            .credits-board {
                grid-template-columns: 1fr;
            }

            .side-panel {
                position: static;
            }
        }
    </style>
</head>
<body>
    <div class="page-shell">
        <aside class="side-panel">
            <h2 class="side-title">Left progress bar</h2>
            <p class="side-copy">The project is still at the proposal milestone, so the first stage is highlighted and the remaining stages stay pending.</p>
            <div class="vertical-progress">
                <div class="vertical-track">
                    <div class="vertical-fill"></div>
                </div>
                <div class="vertical-steps">
                    <div class="vertical-step current"><b>Proposal</b>Research framing, scope, and feasibility definition.</div>
                    <div class="vertical-step"><b>Progress Report</b>Pipeline implementation and interim findings.</div>
                    <div class="vertical-step"><b>Presentation</b>Storytelling, prototype demo, and technical defense.</div>
                    <div class="vertical-step"><b>Final Delivery</b>Evaluation, report writing, and deliverables.</div>
                </div>
            </div>
        </aside>

        <div class="page">
        <section class="hero">
            <div class="nav">
                <span class="eyebrow">About the Capstone</span>
                <a href="/">Back to Home</a>
            </div>
            <section class="progress-panel">
                <div class="progress-header">
                    <span class="progress-left">Current phase: Proposal</span>
                    <span class="progress-right">10% complete</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-milestones">
                    <span class="progress-step current">Proposal 10%</span>
                    <span class="progress-step">Progress Report 10%</span>
                    <span class="progress-step">Presentation 15%</span>
                    <span class="progress-step">Final Report / Deliverables 65%</span>
                </div>
            </section>
            <h1>Multimodal Fake News Analysis: project direction, requirements, and next-step ideas</h1>
            <p class="lead">
                Based on the capstone briefing, this project should demonstrate independent technical competence,
                produce a substantial final deliverable, and clearly communicate methodology, findings, and progress.
                For this topic, the strongest direction is a research-driven platform that analyzes both textual and visual
                signals in online news content while preserving evidence through reproducible archiving.
            </p>
            <div class="pill-row">
                <span class="pill">Proposal 10%</span>
                <span class="pill">Progress Report 10%</span>
                <span class="pill">Presentation 15%</span>
                <span class="pill">Final Report / Deliverables 65%</span>
            </div>
        </section>

        <section class="section full-width">
            <h2>What this project is</h2>
            <p>
                A multimodal analysis system that compares real and fake news using both article text and visual evidence.
                The platform archives webpages, extracts textual and image-based signals, and presents interpretable
                credibility insights rather than a black-box score.
            </p>
        </section>

        <div class="grid">
            <section class="section">
                <h2>Problem statement</h2>
                <ul>
                    <li>Fake news is not only expressed through wording, but also through screenshots, reused images, memes, and misleading visual framing.</li>
                    <li>Many basic approaches focus only on text, which can miss important evidence contained in attached visuals and page structure.</li>
                    <li>This project explores whether combining text and image signals leads to stronger, more interpretable fake-news analysis.</li>
                    <li>The system is designed to support evidence-assisted assessment, not to make absolute truth claims.</li>
                </ul>
            </section>

            <section class="section">
                <h2>What the capstone brief implies</h2>
                <ul>
                    <li>The project needs to apply knowledge from earlier study units and show clear technical ownership.</li>
                    <li>Assessment emphasises a proposal, progress evidence, presentation quality, and a substantial final report.</li>
                    <li>Documentation matters as much as implementation: the capstone expects methodology, findings, communication, and reflection to be well recorded.</li>
                    <li>Version control, privacy, progress tracking, and professional communication are part of good capstone practice.</li>
                </ul>
            </section>
        </div>

        <section class="section full-width">
            <h2>Research questions</h2>
            <ul>
                <li>How do fake and real news articles differ in tone, structure, sentiment, and presentation style?</li>
                <li>What visual signals commonly appear in misleading or manipulated news content?</li>
                <li>Does combining text and image features perform better than text-only analysis?</li>
                <li>Which signals are most interpretable when explaining why a page appears suspicious?</li>
            </ul>
        </section>

        <section class="section full-width">
            <h2>Proposed system idea</h2>
            <p>
                A practical capstone scope is to build a pipeline that captures webpages, extracts article text and images,
                computes multimodal features, and produces an interpretable prediction or credibility analysis. The system
                can compare signals such as headline style, sentiment, named entities, source metadata, image reuse, OCR
                text from images, and mismatch between visual content and article claims.
            </p>
            <div class="timeline">
                <div class="step">
                    <b>1. Collect</b>
                    Archive webpages as MHTML and preserve source URLs, timestamps, and metadata.
                </div>
                <div class="step">
                    <b>2. Process</b>
                    Extract article text, page structure, screenshots, images, and OCR-ready visual assets.
                </div>
                <div class="step">
                    <b>3. Analyze</b>
                    Combine NLP features with image-based or vision-language features for classification.
                </div>
                <div class="step">
                    <b>4. Explain</b>
                    Show why an article is suspicious using evidence-backed feature summaries.
                </div>
            </div>
        </section>

        <div class="grid">
            <section class="section">
                <h2>Scope</h2>
                <div class="two-column-list">
                    <div class="scope-box">
                        <h3>In scope</h3>
                        <ul>
                            <li>Archived article pages and webpage snapshots.</li>
                            <li>Headline and body-text extraction.</li>
                            <li>Attached article images, screenshots, and OCR text.</li>
                            <li>Multimodal feature comparison and explainable output summaries.</li>
                            <li>Prototype web interface for capture and analysis demonstration.</li>
                        </ul>
                    </div>
                    <div class="scope-box">
                        <h3>Out of scope</h3>
                        <ul>
                            <li>Real-time social media moderation at production scale.</li>
                            <li>Fully automated truth verification across the whole web.</li>
                            <li>Large-scale claim fact-checking with human editorial workflows.</li>
                            <li>Deepfake video detection and audiovisual forensics.</li>
                            <li>Use as a final authority on whether content is true or false.</li>
                        </ul>
                    </div>
                </div>
            </section>

            <section class="section">
                <h2>Target users</h2>
                <ul>
                    <li>Researchers studying misinformation and multimodal communication.</li>
                    <li>Journalism and media students exploring credibility signals.</li>
                    <li>Fact-checking or media-literacy educators who need teaching examples.</li>
                    <li>Assessors interested in how interpretable misinformation tools can be built and evaluated.</li>
                </ul>
            </section>
        </div>

        <div class="grid">
            <section class="section">
                <h2>Data sources</h2>
                <ul>
                    <li>Fact-checking archives and misinformation case examples.</li>
                    <li>Verified real-news sources used as comparison references.</li>
                    <li>Fake-news examples that include associated visuals, screenshots, or reused imagery.</li>
                    <li>Archived HTML or MHTML, timestamps, metadata, extracted images, and OCR text.</li>
                    <li>Potential topic categories such as politics, health, and entertainment.</li>
                </ul>
            </section>

            <section class="section">
                <h2>Methodology snapshot</h2>
                <ul>
                    <li>Web archiving and scraping to preserve source evidence.</li>
                    <li>NLP feature extraction from titles, article bodies, and metadata.</li>
                    <li>OCR for embedded screenshots, memes, or image text.</li>
                    <li>Image or vision-language features for visual mismatch analysis.</li>
                    <li>Model comparison, error analysis, and explainability-oriented reporting.</li>
                </ul>
            </section>
        </div>

        <div class="three-grid">
            <section class="section">
                <h2>Evaluation plan</h2>
                <ul>
                    <li>Benchmark text-only, image-only, and multimodal models.</li>
                    <li>Use accuracy, precision, recall, and F1 to compare approaches.</li>
                    <li>Perform qualitative error analysis on ambiguous or misleading cases.</li>
                    <li>Review whether highlighted suspicious features are understandable to users.</li>
                </ul>
            </section>

            <section class="section">
                <h2>Ethics and limitations</h2>
                <ul>
                    <li>The system supports analysis, not absolute truth judgment.</li>
                    <li>Datasets may contain political, cultural, or source-selection bias.</li>
                    <li>Images can appear misleading even without direct manipulation.</li>
                    <li>Outputs should be treated as evidence-assisted assessments with uncertainty.</li>
                </ul>
            </section>

            <section class="section">
                <h2>Brainstorming directions</h2>
                <ul>
                    <li>Build a benchmark comparing text-only, image-only, and multimodal fake-news models.</li>
                    <li>Detect inconsistency between headline claims and the attached hero image.</li>
                    <li>Use OCR on embedded screenshots or memes to capture hidden textual misinformation.</li>
                    <li>Create a source credibility layer using domain reputation, publication patterns, or metadata completeness.</li>
                    <li>Provide an explainability dashboard that highlights suspicious phrases, emotional wording, and mismatched visuals.</li>
                </ul>
            </section>
        </div>

        <div class="grid">
            <section class="section">
                <h2>Suggested deliverables</h2>
                <ul>
                    <li>A data collection pipeline for archived webpages and extracted multimodal assets.</li>
                    <li>A modeling pipeline with at least one baseline and one stronger multimodal approach.</li>
                    <li>An evaluation report with metrics, dataset limitations, and error analysis.</li>
                    <li>A small web interface that demonstrates capture, analysis, and result presentation.</li>
                    <li>Clear documentation showing methodology, assumptions, ethical limits, and future work.</li>
                </ul>
            </section>

            <section class="section">
                <h2>Capstone timeline</h2>
                <div class="timeline">
                    <div class="step">
                        <b>Proposal</b>
                        Define the problem, scope, literature context, and initial dataset plan.
                    </div>
                    <div class="step">
                        <b>Data pipeline</b>
                        Build archiving, extraction, and preprocessing for text and visuals.
                    </div>
                    <div class="step">
                        <b>Modeling</b>
                        Compare baseline models against a multimodal approach.
                    </div>
                    <div class="step">
                        <b>Final delivery</b>
                        Complete the demo, evaluation, report, and presentation materials.
                    </div>
                </div>
            </section>
        </div>

        <section class="section full-width">
            <h2>Recommended capstone framing</h2>
            <p>
                A strong project statement would be: <span class="muted">"Design and evaluate a multimodal system for fake news analysis
                that integrates webpage archiving, textual feature extraction, and visual evidence processing to improve
                credibility assessment and reproducibility of analysis."</span>
            </p>
            <p>
                This framing aligns well with the capstone expectations in the PDF: it is technically substantial,
                research-oriented, measurable, and suitable for proposal, progress, presentation, and final report milestones.
            </p>
        </section>

        <section class="section full-width">
            <h2>Project artifacts and evidence</h2>
            <p>
                This prototype should eventually connect the public-facing app to project evidence such as methodology notes,
                proposal documents, progress reports, evaluation summaries, and repository history.
            </p>
            <div class="artifact-list">
                <div class="artifact">
                    <b>Live demo</b>
                    Current web archiver interface for collecting reproducible webpage evidence.
                    <span class="tag">Available now via Home</span>
                </div>
                <div class="artifact">
                    <b>Project proposal</b>
                    Problem framing, scope, related work, and planned methodology.
                    <span class="tag">To be linked when ready</span>
                </div>
                <div class="artifact">
                    <b>Progress report</b>
                    Mid-project findings, risks, and implementation progress.
                    <span class="tag">To be linked when ready</span>
                </div>
                <div class="artifact">
                    <b>Final report and deliverables</b>
                    Final evaluation, discussion, limitations, and conclusions.
                    <span class="tag">To be linked when ready</span>
                </div>
            </div>
        </section>

        <section class="section full-width">
            <h2>Credits</h2>
            <p>
                The following member information was extracted from the proposal document and reflects the team list and
                proposal-stage responsibilities.
            </p>
            <div class="credits-board">
                <div class="credit-item"><b>Frank Shi (540435478)</b>Crawler developer and data support for identifier handling, URL generation, and collection stability.</div>
                <div class="credit-item"><b>Han Li (500047446)</b>Technical implementation, web crawling, Altmetric integration, and dataset storage management.</div>
                <div class="credit-item"><b>Yaning Chen (540482069)</b>Literature review lead, research analyst, and support for data verification and interpretation.</div>
                <div class="credit-item"><b>Tianze Xu (490040016)</b>Librarian responsible for meeting minutes and report documentation.</div>
                <div class="credit-item"><b>Yuqing Yang (530194981)</b>Altmetric data retrieval, cleaning, and CSV preparation for downstream analysis.</div>
                <div class="credit-item"><b>Haobo Zhao (540654057)</b>Pipeline integration and system execution across MHTML crawling and Altmetric retrieval.</div>
                <div class="credit-item"><b>Ruicheng Zhang (490030501)</b>Team leader, coordinator, and primary communicator with the client.</div>
                <div class="credit-item"><b>Nho Thanh Le (530832278)</b>Document review, web-based UI, backend work, and data pipeline support.</div>
            </div>
        </section>

        </div>

        <aside class="side-panel">
            <h2 class="side-title">Right progress bar</h2>
            <p class="side-copy">This sidebar gives a quick milestone summary and keeps the capstone journey visible while scrolling the About page.</p>
            <div class="vertical-progress right">
                <div class="vertical-steps">
                    <div class="vertical-step current"><b>10%</b>Proposal active now.</div>
                    <div class="vertical-step"><b>20%</b>Progress checkpoint after early implementation.</div>
                    <div class="vertical-step"><b>35%</b>Presentation milestone with demo and explanation.</div>
                    <div class="vertical-step"><b>100%</b>Final report and complete deliverables.</div>
                </div>
                <div class="vertical-track">
                    <div class="vertical-fill"></div>
                </div>
            </div>
        </aside>
    </div>
</body>
</html>
"""


References_page = """
<!doctype html>
<html>
<head>
    <title>References</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --page-bg: #f4f7ff;
            --text-main: #1f2a44;
            --text-muted: #58657d;
            --panel: rgba(255, 255, 255, 0.92);
            --line: #dfe7fb;
            --brand: #4338ca;
            --accent: #0891b2;
            --shadow: 0 20px 45px rgba(22, 34, 66, 0.12);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Inter", "Segoe UI", Roboto, Arial, sans-serif;
            color: var(--text-main);
            background:
                linear-gradient(180deg, rgba(248, 250, 255, 0.92), rgba(235, 250, 248, 0.94)),
                url("/img/backgrounds/home.png") center/cover fixed;
            min-height: 100vh;
            padding: 28px 20px 48px;
        }

        .page {
            width: min(980px, 100%);
            margin: 0 auto;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 22px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(3px);
            padding: 28px;
        }

        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        .nav a {
            text-decoration: none;
            color: var(--brand);
            font-weight: 700;
        }

        h1 {
            margin: 0 0 10px;
            font-size: clamp(28px, 4vw, 40px);
        }

        .subtitle {
            margin: 0 0 18px;
            color: var(--text-muted);
            line-height: 1.7;
        }

        .reference-item {
            display: block;
            margin: 0;
            padding: 18px;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: #f8fbff;
            color: var(--text-main);
            line-height: 1.8;
            word-break: break-word;
            text-decoration: none;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .reference-item:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(67, 56, 202, 0.12);
        }

        .reference-item .doi {
            color: var(--brand);
            text-decoration: underline;
        }

        .reference-item .hint {
            display: block;
            margin-top: 6px;
            color: var(--text-muted);
            font-size: 13px;
        }

        .reference-list {
            margin-top: 14px;
            display: grid;
            gap: 10px;
        }

        .reference-list-item {
            margin: 0;
            padding: 14px 16px;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: #f8fbff;
            line-height: 1.7;
            color: var(--text-main);
        }

        .reference-list-item a {
            color: var(--brand);
        }
    </style>
</head>
<body>
    <div class="page">
        <section class="card">
            <div class="nav">
                <a href="/">Back to Home</a>
                <a href="/about">About Project</a>
            </div>
            <h1>References</h1>
            <p class="subtitle">Source list in APA 7 format. The first paper is the main inspiration and is pinned at the top.</p>
            <a class="reference-item" href="/references/leap-2018-analysis">
                Thelwall, M., Lehtisaari, M., Katsirea, I., Holmberg, K., &amp; Zheng, E.-T. (2025).
                Does ChatGPT ignore article retractions and other reliability concerns?
                <em>Learned Publishing, 38</em>(4), e2018.
                <span class="doi">https://doi.org/10.1002/leap.2018</span>
                <span class="hint">Click to view detailed analysis page (placeholder).</span>
            </a>
            <div class="reference-list">
                <p class="reference-list-item">
                    Abdali, S., Shaham, S., &amp; Krishnamachari, B. (2024). Multi-modal misinformation detection:
                    Approaches, challenges and opportunities. <em>ACM Computing Surveys, 57</em>(3), 1-29.
                    <a href="https://doi.org/10.1145/3697349" target="_blank" rel="noopener noreferrer">https://doi.org/10.1145/3697349</a>
                </p>
                <p class="reference-list-item">
                    Abdelnabi, S., Hasan, R., &amp; Fritz, M. (2022). Open-domain, content-based, multi-modal
                    fact-checking of out-of-context images via online resources. In <em>Proceedings of the IEEE/CVF Conference on
                    Computer Vision and Pattern Recognition</em> (pp. 14940-14949).
                    <a href="https://doi.org/10.1109/CVPR52688.2022.01452" target="_blank" rel="noopener noreferrer">https://doi.org/10.1109/CVPR52688.2022.01452</a>
                </p>
                <p class="reference-list-item">
                    D'Ulizia, A., Caschera, M. C., Ferri, F., &amp; Grifoni, P. (2021). Fake news detection: A survey of
                    evaluation datasets. <em>PeerJ Computer Science, 7</em>, e518.
                    <a href="https://doi.org/10.7717/peerj-cs.518" target="_blank" rel="noopener noreferrer">https://doi.org/10.7717/peerj-cs.518</a>
                </p>
                <p class="reference-list-item">
                    Papadopoulos, S.-I., Koutlis, C., Papadopoulos, S., &amp; Petrantonakis, P. C. (2024). VERITE: A robust
                    benchmark for multimodal misinformation detection accounting for unimodal bias.
                    <em>International Journal of Multimedia Information Retrieval, 13</em>, Article 4.
                    <a href="https://doi.org/10.1007/s13735-023-00312-6" target="_blank" rel="noopener noreferrer">https://doi.org/10.1007/s13735-023-00312-6</a>
                </p>
                <p class="reference-list-item">
                    Przybyla, P. (2020). Capturing the style of fake news. <em>Proceedings of the AAAI Conference on Artificial Intelligence, 34</em>(1), 490-497.
                    <a href="https://doi.org/10.1609/aaai.v34i01.5386" target="_blank" rel="noopener noreferrer">https://doi.org/10.1609/aaai.v34i01.5386</a>
                </p>
                <p class="reference-list-item">
                    Rashkin, H., Choi, E., Jang, J. Y., Volkova, S., &amp; Choi, Y. (2017). Truth of varying shades:
                    Analyzing language in fake news and political fact-checking. In <em>Proceedings of the 2017 Conference on Empirical
                    Methods in Natural Language Processing</em> (pp. 2931-2937). Association for Computational Linguistics.
                    <a href="https://doi.org/10.18653/v1/D17-1317" target="_blank" rel="noopener noreferrer">https://doi.org/10.18653/v1/D17-1317</a>
                </p>
                <p class="reference-list-item">
                    Sabir, E., AbdAlmageed, W., Wu, Y., &amp; Natarajan, P. (2018). Deep multimodal image-repurposing detection.
                    In <em>Proceedings of the 26th ACM International Conference on Multimedia</em> (pp. 1337-1345).
                </p>
                <p class="reference-list-item">
                    Serghiou, S., Marton, R. M., &amp; Ioannidis, J. P. A. (2021). Media and social media attention to
                    retracted articles according to Altmetric. <em>PLOS ONE, 16</em>(5), e0248625.
                    <a href="https://doi.org/10.1371/journal.pone.0248625" target="_blank" rel="noopener noreferrer">https://doi.org/10.1371/journal.pone.0248625</a>
                </p>
                <p class="reference-list-item">
                    Shu, K., Mahudeswaran, D., Wang, S., Lee, D., &amp; Liu, H. (2020). FakeNewsNet: A data repository
                    with news content, social context, and spatiotemporal information for studying fake news on social media.
                    <em>Big Data, 8</em>(3), 171-188.
                    <a href="https://doi.org/10.1089/big.2020.0062" target="_blank" rel="noopener noreferrer">https://doi.org/10.1089/big.2020.0062</a>
                </p>
                <p class="reference-list-item">
                    Valinciute, A., &amp; Halffman, W. (2025). Do journalists update retracted science news?
                    <em>Journalism Practice</em>, 1-23.
                    <a href="https://doi.org/10.1080/17512786.2025.2540460" target="_blank" rel="noopener noreferrer">https://doi.org/10.1080/17512786.2025.2540460</a>
                </p>
                <p class="reference-list-item">
                    Wang, Y., Ma, F., Jin, Z., Yuan, Y., Xun, G., Jha, K., Su, L., &amp; Gao, J. (2018). EANN: Event
                    adversarial neural networks for multi-modal fake news detection. In <em>Proceedings of the 24th ACM SIGKDD International
                    Conference on Knowledge Discovery &amp; Data Mining</em> (pp. 849-857).
                    <a href="https://doi.org/10.1145/3219819.3219903" target="_blank" rel="noopener noreferrer">https://doi.org/10.1145/3219819.3219903</a>
                </p>
                <p class="reference-list-item">
                    Zhou, X., &amp; Zafarani, R. (2020). A survey of fake news. <em>ACM Computing Surveys, 53</em>(5), 1-40.
                    <a href="https://doi.org/10.1145/3395046" target="_blank" rel="noopener noreferrer">https://doi.org/10.1145/3395046</a>
                </p>
            </div>
        </section>
    </div>
</body>
</html>
"""

Reference_detail_page = """
<!doctype html>
<html>
<head>
    <title>Reference Analysis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --text-main: #1f2a44;
            --text-muted: #58657d;
            --panel: rgba(255, 255, 255, 0.92);
            --line: #dfe7fb;
            --brand: #4338ca;
            --shadow: 0 20px 45px rgba(22, 34, 66, 0.12);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Inter", "Segoe UI", Roboto, Arial, sans-serif;
            color: var(--text-main);
            background:
                linear-gradient(180deg, rgba(248, 250, 255, 0.92), rgba(235, 250, 248, 0.94)),
                url("/img/backgrounds/home.png") center/cover fixed;
            min-height: 100vh;
            padding: 28px 20px 48px;
        }

        .page {
            width: min(980px, 100%);
            margin: 0 auto;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 22px;
            box-shadow: var(--shadow);
            padding: 28px;
        }

        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        .nav a {
            text-decoration: none;
            color: var(--brand);
            font-weight: 700;
        }

        h1 {
            margin: 0 0 10px;
            font-size: clamp(26px, 4vw, 38px);
        }

        .citation {
            margin: 0 0 14px;
            padding: 16px;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: #f8fbff;
            line-height: 1.7;
        }

        .placeholder {
            margin: 0;
            color: var(--text-muted);
            line-height: 1.7;
        }
    </style>
</head>
<body>
    <div class="page">
        <section class="card">
            <div class="nav">
                <a href="/references">Back to References</a>
                <a href="/">Back to Home</a>
            </div>
            <h1>Detailed Analysis (Temporary Blank)</h1>
            <p class="citation">
                Thelwall, M., Lehtisaari, M., Katsirea, I., Holmberg, K., &amp; Zheng, E.-T. (2025).
                Does ChatGPT ignore article retractions and other reliability concerns?
                <em>Learned Publishing, 38</em>(4), e2018.
            </p>
            <p class="placeholder">
                This section is intentionally blank for now. Detailed analysis content will be added in a later update.
            </p>
        </section>
    </div>
</body>
</html>
"""

@app.route("/img/<path:filename>")
def image_assets(filename):
    return send_from_directory(IMG_DIR, filename)

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)


@app.route("/about", methods=["GET"])
def about():
    return render_template_string(About_page)

@app.route("/references", methods=["GET"])
def references():
    return render_template_string(References_page)

@app.route("/references/leap-2018-analysis", methods=["GET"])
def reference_leap_2018_analysis():
    return render_template_string(Reference_detail_page)

@app.route("/save", methods=["POST"])
def save_page():
    url = request.form.get("url", "").strip()

    if not url.startswith(("http://", "https://")):
        return "Invalid URL. Please include http:// or https://", 400

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        # simple MHTML-like file content
        now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        mhtml_content = f"""From: <Saved by Flask>
Subject: {url}
Date: {now}
MIME-Version: 1.0
Content-Type: multipart/related; boundary="BOUNDARY"

--BOUNDARY
Content-Type: text/html; charset="utf-8"
Content-Location: {url}

{resp.text}

--BOUNDARY--
"""

        output_path = Path("saved_page.mhtml")
        output_path.write_text(mhtml_content, encoding="utf-8")

        return send_file(
            output_path,
            as_attachment=True,
            download_name="saved_page.mhtml"
        )

    except requests.RequestException as e:
        return f"Failed to fetch page: {e}", 500
