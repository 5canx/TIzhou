function renderResult(data) {
    const container = document.getElementById('result');
    if (!data || (Array.isArray(data) && data.length === 0)) {
        container.innerHTML = '<p>未找到相关题目。</p>';
        return;
    }

    const results = Array.isArray(data) ? data : [data];

    container.innerHTML = results.map(q => {
        let parsedOptions = [];

        if (Array.isArray(q.options)) {
            parsedOptions = q.options;
        } else if (typeof q.options === 'string') {
            try {
                parsedOptions = JSON.parse(q.options);
            } catch (e) {
                parsedOptions = [];
            }
        } else if (typeof q.options === 'object' && q.options !== null) {
            parsedOptions = Object.values(q.options);
        }

        // 这里判断是否显示无选项上传
        let optionsHtml = '';
        if (parsedOptions.length > 0) {
            optionsHtml = parsedOptions.map(opt => `${opt.label}. ${opt.text}`).join('，');
        } else {
            // 有题目内容但无选项，显示“无选项上传”，否则显示'-'
            optionsHtml = (q.content && q.content.trim() !== '') ? '无选项上传' : '-';
        }

        let answers = [];
        if (Array.isArray(q.answer)) {
            answers = q.answer.map(String);
        } else if (q.answer !== undefined && q.answer !== null) {
            answers = [String(q.answer)];
        }
        const answerLabels = answers.map(ans => {
            const opt = parsedOptions.find(o => o.text === ans || o.label === ans);
            return opt ? opt.label : ans;
        });
        const answerStr = answerLabels.join('').toUpperCase();

        return `
            <div style="margin-bottom:10px; padding:6px 0; border-bottom:1px dashed #ccc; font-size:14px; line-height:1.4; text-align:left;">
                <p><strong>题目ID：</strong> ${q.question_id || '-'}</p>
                <p><strong>题目类型：</strong> ${q.question_type || '-'}</p>
                <p><strong>题目内容：</strong> ${q.content || '-'}</p>
                <p><strong>选项：</strong> ${optionsHtml}</p>
                <p><strong>答案：</strong> <span class="answer-bold">${answerStr || '-'}</span></p>
            </div>
        `;
    }).join('');
}



document.getElementById('search-id-btn').addEventListener('click', async () => {
    const id = document.getElementById('id-input').value.trim();
    if (!id) {
        alert('请输入题目ID');
        return;
    }
    try {
        const response = await fetch('/api/search/id/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });
        const data = await response.json();
        renderResult(data);
    } catch (err) {
        document.getElementById('result').textContent = '请求失败: ' + err.message;
    }
});

document.getElementById('search-content-btn').addEventListener('click', async () => {
    const content = document.getElementById('content-input').value.trim();
    if (!content) {
        alert('请输入查询内容');
        return;
    }
    try {
        const response = await fetch('/api/search/content/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        const data = await response.json();
        renderResult(data);
    } catch (err) {
        document.getElementById('result').textContent = '请求失败: ' + err.message;
    }
});
