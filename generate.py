#!/usr/bin/env python3
import requests
import json
import os
import re

FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', 'cli_a971a71ab0395cce')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', 'T94yU3Og4QHiWxqmw4DNreSCipBmlJf7')
BITABLE_APP_TOKEN = 'DOK5bKaDtaJAnpsp3UZcuibRnFf'
TABLE_ID = 'tblfigiNW09OkXU9'

def get_token():
    resp = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET}
    )
    return resp.json()['tenant_access_token']

def get_all_records(token):
    all_records = []
    page_token = None
    while True:
        params = {'page_size': 500}
        if page_token:
            params['page_token'] = page_token
        resp = requests.get(
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records',
            headers={'Authorization': f'Bearer {token}'},
            params=params
        )
        data = resp.json()['data']
        all_records.extend(data.get('items', []))
        page_token = data.get('page_token')
        if not page_token:
            break
    return all_records

def is_complete(fields):
    """检查记录是否有核心数据（高光视频和分析非必填）"""
    required_fields = ['學生姓名', '課程名稱', '上課時間', '本节课核心', '答題正確率']
    for field in required_fields:
        if not fields.get(field):
            return False
    return True

def make_html(record):
    fields = record['fields']
    data_json = json.dumps(fields, ensure_ascii=False)
    name = fields.get('學生姓名', '学生')

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>课程报告 - {name}</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script id="tailwind-config">
tailwind.config = {{
    darkMode: "class",
    theme: {{
        extend: {{
            colors: {{
                "background": "#fbf9f7","surface": "#fbf9f7","surface-container-lowest": "#ffffff",
                "surface-container-low": "#f5f3f1","surface-container": "#efedeb",
                "surface-container-high": "#eae8e6","surface-container-highest": "#e4e2e0",
                "surface-bright": "#fbf9f7","outline-variant": "#d6c3b8","outline": "#84746a",
                "on-surface": "#1b1c1b","on-surface-variant": "#51443c","on-background": "#1b1c1b",
                "primary": "#85532e","primary-container": "#e8a87c","on-primary": "#ffffff",
                "on-primary-container": "#693c19","on-primary-fixed-variant": "#693c19",
                "primary-fixed": "#ffdcc6","primary-fixed-dim": "#fbb88b",
                "secondary": "#256583","secondary-container": "#a2dcff","on-secondary": "#ffffff",
                "on-secondary-container": "#216280","tertiary": "#286b33",
                "tertiary-container": "#80c683","on-tertiary": "#ffffff",
                "on-tertiary-container": "#08531e","inverse-surface": "#30302f",
                "inverse-on-surface": "#f2f0ee","inverse-primary": "#fbb88b",
                "error": "#ba1a1a","on-error": "#ffffff","error-container": "#ffdad6",
                "on-error-container": "#93000a"
            }},
            borderRadius: {{ DEFAULT: "0.5rem", lg: "0.5rem", xl: "0.75rem", full: "9999px" }},
            fontFamily: {{ sans: ["Plus Jakarta Sans", "sans-serif"] }},
            fontSize: {{
                "body-md": ["14px", {{ lineHeight: "20px", fontWeight: "400" }}],
                "label-md": ["13px", {{ lineHeight: "18px", letterSpacing: "0.01em", fontWeight: "600" }}],
                "label-sm": ["11px", {{ lineHeight: "14px", letterSpacing: "0.02em", fontWeight: "600" }}],
                "headline-lg": ["18px", {{ lineHeight: "24px", letterSpacing: "-0.01em", fontWeight: "700" }}],
                "body-lg": ["16px", {{ lineHeight: "22px", fontWeight: "500" }}],
                "headline-xl": ["24px", {{ lineHeight: "32px", letterSpacing: "-0.02em", fontWeight: "700" }}]
            }}
        }}
    }}
}}
</script>
<style>
body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #F7F5F3; }}
.report-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0px 2px 12px rgba(0,0,0,0.03); margin-bottom: 12px; }}
.material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }}
.video-wrapper {{ position: relative; width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #1b2e3c 0%, #2d4a5e 100%); border-radius: 12px; overflow: hidden; cursor: pointer; }}
.video-wrapper video {{ width: 100%; height: 100%; object-fit: cover; display: none; }}
.video-cover {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }}
.video-cover-icon {{ width: 56px; height: 56px; border-radius: 50%; background: rgba(255,255,255,0.18); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; transition: transform 0.2s, background 0.2s; }}
.video-wrapper:hover .video-cover-icon {{ background: rgba(255,255,255,0.28); transform: scale(1.06); }}
.video-cover-label {{ color: rgba(255,255,255,0.85); font-size: 13px; font-weight: 600; letter-spacing: 0.02em; }}
.progress-circle {{ transition: stroke-dashoffset 1s ease; }}
</style>
</head>
<body class="antialiased text-on-surface">
<main class="pt-8 px-4 max-w-lg mx-auto pb-24">
    <header class="mb-6 text-center">
        <h1 class="text-headline-xl font-bold text-on-surface" id="pageTitle">课后学习报告</h1>
    </header>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-3">
            <div class="p-1.5 bg-secondary-container/40 rounded-lg"><span class="material-symbols-outlined text-secondary text-xl">menu_book</span></div>
            <h3 class="text-headline-lg">课程信息</h3>
        </div>
        <div class="space-y-2.5">
            <div class="flex items-center justify-between">
                <span class="text-label-md text-on-surface-variant">课程名称</span>
                <span class="text-body-md font-bold" id="courseName">—</span>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-label-md text-on-surface-variant">上课时间</span>
                <span class="text-body-md" id="courseTime">—</span>
            </div>
            <div class="mt-3 p-3 bg-surface-container rounded-xl border border-dashed border-outline-variant">
                <p class="text-body-md text-on-surface-variant leading-relaxed" id="courseKey">—</p>
            </div>
        </div>
    </div>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-3">
            <div class="p-1.5 bg-tertiary-container/40 rounded-lg"><span class="material-symbols-outlined text-tertiary text-xl">auto_awesome</span></div>
            <h3 class="text-headline-lg">核心知识点</h3>
        </div>
        <ul class="space-y-2 mb-4" id="coreList"></ul>
        <div class="p-3 bg-surface-container rounded-xl border border-dashed border-outline-variant">
            <p class="text-body-md text-on-surface-variant leading-relaxed" id="coreSummary">—</p>
        </div>
    </div>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-4">
            <div class="p-1.5 bg-primary-container/40 rounded-lg"><span class="material-symbols-outlined text-primary text-xl">analytics</span></div>
            <h3 class="text-headline-lg">学习成果</h3>
        </div>
        <div class="flex flex-col items-center mb-5">
            <div class="relative w-24 h-24">
                <svg class="w-full h-full -rotate-90" viewBox="0 0 96 96">
                    <circle cx="48" cy="48" r="40" fill="transparent" stroke="#eae8e6" stroke-width="7"/>
                    <circle id="progressArc" cx="48" cy="48" r="40" fill="transparent" stroke="#286b33" stroke-width="8" stroke-linecap="round" stroke-dasharray="251.2" stroke-dashoffset="251.2" class="progress-circle"/>
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                    <span class="text-lg font-bold" id="rateText">—</span>
                    <span class="text-[10px] text-on-surface-variant">掌握率</span>
                </div>
            </div>
        </div>
        <div class="grid grid-cols-3 gap-2.5 mb-4">
            <div class="bg-surface-container p-3 rounded-xl text-center">
                <div class="text-lg font-bold text-on-surface" id="totalCount">—</div>
                <div class="text-label-sm text-on-surface-variant">答题数</div>
            </div>
            <div class="bg-surface-container p-3 rounded-xl text-center">
                <div class="text-lg font-bold text-tertiary" id="correctCount">—</div>
                <div class="text-label-sm text-on-surface-variant">已掌握</div>
            </div>
            <div class="bg-surface-container p-3 rounded-xl text-center">
                <div class="text-lg font-bold text-on-primary-fixed-variant" id="wrongCount">—</div>
                <div class="text-label-sm text-on-surface-variant">待巩固</div>
            </div>
        </div>
        <div class="mb-4">
            <div class="text-label-sm text-on-surface-variant mb-1.5">知识点详情</div>
            <div class="flex flex-wrap gap-1.5" id="knowledgeTags"></div>
        </div>
        <div class="p-3 bg-tertiary/10 rounded-xl">
            <div class="flex items-center gap-1.5 mb-1.5">
                <span class="material-symbols-outlined text-tertiary text-sm" style="font-variation-settings:'FILL' 1;">stars</span>
                <span class="text-label-md text-tertiary">答题情况评价</span>
            </div>
            <p class="text-body-md text-on-surface-variant" id="quizComment">—</p>
        </div>
    </div>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-3">
            <div class="p-1.5 bg-secondary-container/40 rounded-lg"><span class="material-symbols-outlined text-secondary text-xl">videocam</span></div>
            <h3 class="text-headline-lg">课堂精彩瞬间</h3>
        </div>
        <div class="video-wrapper mb-3" id="videoWrapper" onclick="toggleVideo()">
            <video id="highlightVideo" preload="none" playsinline></video>
            <div class="video-cover" id="videoCover">
                <div class="video-cover-icon">
                    <span class="material-symbols-outlined text-white text-4xl" style="font-variation-settings:'FILL' 1;">play_arrow</span>
                </div>
                <span class="video-cover-label">点击播放精彩瞬间</span>
            </div>
        </div>
        <p class="text-body-md text-on-surface-variant" id="videoComment">—</p>
    </div>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-4">
            <div class="p-1.5 bg-primary-container/40 rounded-lg"><span class="material-symbols-outlined text-primary text-xl">forum</span></div>
            <h3 class="text-headline-lg">老师点评</h3>
        </div>
        <div class="mb-3"><div class="text-label-md font-bold text-on-surface" id="teacherName">—</div></div>
        <div class="p-4 bg-surface-container-low rounded-xl">
            <p class="text-body-md text-on-surface italic leading-relaxed" id="teacherComment">—</p>
        </div>
    </div>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-3">
            <div class="p-1.5 bg-secondary-container/40 rounded-lg"><span class="material-symbols-outlined text-secondary text-xl">forward</span></div>
            <h3 class="text-headline-lg">下节预告</h3>
        </div>
        <p class="text-body-md text-on-surface-variant leading-relaxed" id="nextLesson">—</p>
    </div>
    <div class="report-card">
        <div class="flex items-center gap-2.5 mb-3">
            <div class="p-1.5 bg-tertiary-container/40 rounded-lg"><span class="material-symbols-outlined text-tertiary text-xl">lightbulb</span></div>
            <h3 class="text-headline-lg">预习建议</h3>
        </div>
        <ul class="space-y-2" id="suggestionList"></ul>
    </div>
    <div class="flex justify-center mt-6 mb-4">
        <button class="bg-[#81C784] text-white font-bold py-3 px-12 rounded-full shadow-lg active:scale-95 transition-transform flex items-center gap-2 text-sm">
            <span class="material-symbols-outlined text-lg">share</span>分享报告
        </button>
    </div>
</main>
<script type="application/json" id="report-data">{data_json}</script>
<script>
const DATA = JSON.parse(document.getElementById('report-data').textContent);

function parseCoreKnowledge(text) {{
    if (!text) return {{ items: [], summary: '' }};
    const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
    const items = [], summaryLines = [];
    let reachedSummary = false;
    for (const line of lines) {{
        if (!reachedSummary && /^核心\\d+[：:]/.test(line)) {{
            items.push(line.replace(/^核心\\d+[：:]\\s*/, ''));
        }} else {{ reachedSummary = true; summaryLines.push(line); }}
    }}
    return {{ items, summary: summaryLines.join('\\n') }};
}}

function parseSuggestions(text) {{
    if (!text) return [];
    return text.split('\\n').map(l => l.trim().replace(/^\\d+[\\.、]\\s*/, '')).filter(Boolean);
}}

function parseKnowledgeTags(val) {{
    if (!val) return [];
    if (Array.isArray(val)) return val.map(t => String(t).trim()).filter(Boolean);
    return String(val).split(/[\\s\\n]+/).map(t => t.trim()).filter(Boolean);
}}

function parseRate(val) {{
    if (!val) return 0;
    if (Array.isArray(val)) val = val[0];
    if (typeof val === 'object' && val.text) val = val.text;
    return parseFloat(String(val).replace('%', '')) || 0;
}}

function parseVideoUrl(val) {{
    if (!val) return '';
    if (Array.isArray(val)) val = val[0];
    if (typeof val === 'object' && val.link) return val.link;
    if (typeof val === 'string') return val;
    return '';
}}

function render(f) {{
    const name = f['學生姓名'] || '';
    document.getElementById('pageTitle').textContent = name ? name + '的课后学习报告' : '课后学习报告';
    document.title = name ? '课程报告 - ' + name : '课程报告';
    document.getElementById('courseName').textContent = f['課程名稱'] || '—';
    const courseTime = Array.isArray(f['上課時間']) ? f['上課時間'].join(', ') : (f['上課時間'] || '—');
    document.getElementById('courseTime').textContent = courseTime;
    document.getElementById('courseKey').textContent = f['课程重点'] || '—';

    const core = parseCoreKnowledge(f['本节课核心'] || '');
    const coreList = document.getElementById('coreList');
    coreList.innerHTML = core.items.map(item =>
        "<li class=\\"flex items-center gap-2.5\\"><span class=\\"material-symbols-outlined text-tertiary text-lg\\" style=\\"font-variation-settings:'FILL' 1;\\">check_circle</span><span class=\\"text-body-md\\">" + item + "</span></li>"
    ).join('');
    document.getElementById('coreSummary').textContent = core.summary || '—';

    const rate = parseRate(f['答題正確率']);
    document.getElementById('rateText').textContent = rate ? Math.round(rate) + '%' : '—';
    document.getElementById('totalCount').textContent = f['答題總數'] != null ? f['答題總數'] : '—';
    document.getElementById('correctCount').textContent = f['答題正確數'] != null ? f['答題正確數'] : '—';
    document.getElementById('wrongCount').textContent = f['答错数'] != null ? f['答错数'] : '—';

    const circumference = 251.2;
    setTimeout(() => {{
        document.getElementById('progressArc').style.strokeDashoffset = circumference * (1 - rate / 100);
    }}, 300);

    const tags = parseKnowledgeTags(f['課程知識點'] || '');
    document.getElementById('knowledgeTags').innerHTML = tags.map(tag =>
        '<span class="px-2 py-0.5 bg-secondary-container/20 text-secondary border border-secondary-container rounded-full text-[11px] font-semibold">' + tag + '</span>'
    ).join('') || '<span class="text-label-sm text-on-surface-variant">暂无数据</span>';

    document.getElementById('quizComment').textContent = f['答题情况评价'] || f['成长寄语'] || '—';

    const videoUrl = parseVideoUrl(f['高光视频']);
    if (videoUrl) document.getElementById('highlightVideo').src = videoUrl;
    document.getElementById('videoComment').textContent = f['高光视频分析'] || '—';

    document.getElementById('teacherName').textContent = f['主講老師'] || '—';
    document.getElementById('teacherComment').textContent = f['老师点评'] || '—';
    document.getElementById('nextLesson').textContent = f['下节课预告'] || '—';

    const suggestions = parseSuggestions(f['下节课预习建议'] || '');
    document.getElementById('suggestionList').innerHTML = suggestions.map(s =>
        '<li class="flex items-start gap-2"><span class="text-tertiary mt-1 text-[10px]">●</span><span class="text-body-md text-on-surface-variant">' + s + '</span></li>'
    ).join('') || '<li class="text-body-md text-on-surface-variant">暂无建议</li>';
}}

function toggleVideo() {{
    const video = document.getElementById('highlightVideo');
    const cover = document.getElementById('videoCover');
    if (!video.src) return;
    video.style.display = 'block';
    cover.style.display = 'none';
    video.play();
}}

render(DATA);
</script>
</body>
</html>'''

def main():
    os.makedirs('reports', exist_ok=True)

    print("获取飞书 token...")
    token = get_token()

    print("读取记录...")
    records = get_all_records(token)
    print(f"共 {len(records)} 条记录")

    generated = 0
    for record in records:
        fields = record.get('fields', {})
        if not is_complete(fields):
            continue
        record_id = record['record_id']
        name = fields.get('學生姓名', record_id)
        html = make_html(record)
        filename = f"reports/{record_id}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  生成: {filename} ({name})")
        generated += 1

    print(f"\n完成，共生成 {generated} 个报告")

if __name__ == '__main__':
    main()
