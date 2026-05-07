// Cloudflare Worker - 飞书报告实时生成触发器
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 处理 CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }

    // 从 URL 参数获取记录ID（飞书按钮点击时传入）
    const recordId = url.searchParams.get('record');

    if (!recordId) {
      return new Response('Missing record parameter', {
        status: 400,
        headers: { 'Access-Control-Allow-Origin': '*' }
      });
    }

    const GITHUB_TOKEN = env.GITHUB_TOKEN;
    const GITHUB_REPO = env.GITHUB_REPO || 'wwzz168/kechengbaogao';

    if (!GITHUB_TOKEN) {
      return new Response('Missing GITHUB_TOKEN', {
        status: 500,
        headers: { 'Access-Control-Allow-Origin': '*' }
      });
    }

    try {
      // 触发 GitHub Actions
      const response = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/actions/workflows/generate.yml/dispatches`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ref: 'main'
        })
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`GitHub API error: ${response.status} ${error}`);
      }

      // 重定向到生成的报告页面（带等待提示）
      const reportUrl = `https://wwzz168.github.io/kechengbaogao/${recordId}.html`;

      return new Response(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>生成报告中...</title>
          <style>
            body { font-family: -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f5f5f5; }
            .box { background: white; padding: 40px; border-radius: 12px; text-align: center; }
            .spinner { width: 40px; height: 40px; border: 3px solid #e0e0e0; border-top-color: #1976d2; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
            @keyframes spin { to { transform: rotate(360deg); } }
            h2 { margin: 0 0 10px; color: #333; }
            p { color: #666; margin: 0; }
          </style>
        </head>
        <body>
          <div class="box">
            <div class="spinner"></div>
            <h2>正在生成报告...</h2>
            <p>请稍候，约需 10-20 秒</p>
          </div>
          <script>
            let attempts = 0;
            const maxAttempts = 30;
            const check = () => {
              fetch('${reportUrl}', { method: 'HEAD' })
                .then(r => {
                  if (r.ok) {
                    window.location.href = '${reportUrl}';
                  } else if (++attempts < maxAttempts) {
                    setTimeout(check, 2000);
                  } else {
                    document.querySelector('h2').textContent = '生成可能需要更长时间';
                    document.querySelector('p').innerHTML = '<a href="${reportUrl}">点击刷新查看</a>';
                  }
                })
                .catch(() => {
                  if (++attempts < maxAttempts) {
                    setTimeout(check, 2000);
                  }
                });
            };
            setTimeout(check, 3000);
          </script>
        </body>
        </html>
      `, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Access-Control-Allow-Origin': '*'
        }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }
};
