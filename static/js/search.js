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

        let optionsHtml = '';
        if (parsedOptions.length > 0) {
            optionsHtml = parsedOptions.map(opt => {
                if (opt.is_image && opt.image) {
                    const imgSrc = opt.image.startsWith('http') ? opt.image : STATIC_PREFIX + opt.image;
                    return `
                        <div style="margin: 20px 0; padding: 12px; background-color: #f8f8f8; border-radius: 10px;">
                            <div style="font-weight: bold; margin-bottom: 10px;">${opt.label || '-'}</div>
                            <img class="option-image" src="${imgSrc}" alt="${opt.label || '选项'}"
                                 style="width: 192px; height: 132px; object-fit: cover; display: block; margin: 0 auto; border: 1px solid #ccc; border-radius: 4px;">
                        </div>
                    `;
                } else if (opt.text) {
                    return `
                        <div style="margin: 20px 0; padding: 12px; background-color: #f8f8f8; border-radius: 10px;">
                            <strong>${opt.label || '-'}</strong> ${opt.text}
                        </div>
                    `;
                } else {
                    return `
                        <div style="margin: 20px 0; padding: 12px; background-color: #f8f8f8; border-radius: 10px;">
                            <strong>${opt.label || '-'}</strong> -
                        </div>
                    `;
                }
            }).join('');
        } else {
            optionsHtml = (q.content && q.content.trim() !== '') ? '<div>无选项上传</div>' : '<div>-</div>';
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
            <div style="margin-bottom:20px; padding:12px 0; border-bottom:1px dashed #ccc; font-size:14px; line-height:1.6; text-align:left;">
                <p><strong>题目ID：</strong> ${q.question_id || q.id || '-'}</p>
                <p><strong>题目类型：</strong> ${q.question_type || '-'}</p>
                <p><strong>题目内容：</strong> ${q.content || '-'}</p>
                <p><strong>选项：</strong></p>
                ${optionsHtml}
                <p><strong>答案：</strong> <span class="answer-bold">${answerStr || '-'}</span></p>
            </div>
        `;
    }).join('');
}

// ID 查询
document.getElementById('search-id-btn')?.addEventListener('click', () => {
    const id = document.getElementById('id-input')?.value.trim();
    if (!id) {
        alert('请输入题目ID');
        return;
    }

    fetch('/api/search/id/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        },
        body: JSON.stringify({ id: id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP 错误: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerHTML = `<p>${data.error}</p>`;
        } else {
            renderResult(data);
        }
    })
    .catch(error => {
        document.getElementById('result').innerHTML = `<p>查询失败: ${error.message}</p>`;
    });
});

// 内容查询
document.getElementById('search-content-btn')?.addEventListener('click', () => {
    const content = document.getElementById('content-input')?.value.trim();
    if (!content) {
        alert('请输入查询内容');
        return;
    }

    fetch('/api/search/content/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        },
        body: JSON.stringify({ content: content, size: 10, from: 0 })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP 错误: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerHTML = `<p>${data.error}</p>`;
        } else {
            renderResult(data.results);
        }
    })
    .catch(error => {
        document.getElementById('result').innerHTML = `<p>查询失败: ${error.message}</p>`;
    });
});