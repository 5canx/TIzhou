const STATIC_PREFIX = '/staticfiles/';

function renderResult(data) {
    const container = document.getElementById('result');
    if (!data || (Array.isArray(data) && data.length === 0)) {
        container.innerHTML = '<p>未找到相关题目。</p>';
        return;
    }

    const results = Array.isArray(data) ? data : [data];

    container.innerHTML = results.map(q => {
        let parsedOptions = [];

        // 解析选项
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

        // 渲染选项 HTML（每个选项一行）
        let optionsHtml = '';
        if (parsedOptions.length > 0) {
            optionsHtml = parsedOptions.map(opt => {
                if (opt.is_image && opt.image) {
                    const imgSrc = opt.image.startsWith('http') ? opt.image : STATIC_PREFIX + opt.image;
                    return `<div style="margin-bottom:0; padding:0; line-height:1.2;">${opt.label}. <img class="option-image" src="${imgSrc}" alt="${opt.label}"></div>`;
                } else if (opt.text) {
                    return `<div style="margin-bottom:0; padding:0; line-height:1.2;">${opt.label}. ${opt.text}</div>`;
                } else {
                    return `<div style="margin-bottom:0; padding:0; line-height:1.2;">${opt.label}. -</div>`;
                }
            }).join('');
        } else {
            optionsHtml = (q.content && q.content.trim() !== '') ? '<div>无选项上传</div>' : '<div>-</div>';
        }

        // 渲染答案
        let answers = [];
        if (Array.isArray(q.answer)) {
            answers = q.answer.map(a => String(a).toUpperCase());
        } else if (typeof q.answer === 'string') {
            if (q.answer.length > 1) {
                // 可能是多选题，如 "ACD"，拆分每个字符
                answers = q.answer.toUpperCase().split('');
            } else {
                answers = [q.answer.toUpperCase()];
            }
        } else if (q.answer !== undefined && q.answer !== null) {
            answers = [String(q.answer).toUpperCase()];
        }
        const answerStr = answers.join('');  //答案以“、”分隔


        return `
            <div style="margin-bottom:10px; padding:6px 0; border-bottom:1px dashed #ccc; font-size:14px; line-height:1.6; text-align:left;">
                <p><strong>题目ID：</strong> ${q.question_id || '-'}</p>
                <p><strong>题目类型：</strong> ${q.question_type || '-'}</p>
                <p><strong>题目内容：</strong> ${q.content || '-'}</p>
                <p><strong>选项：</strong></p>
                ${optionsHtml}
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
