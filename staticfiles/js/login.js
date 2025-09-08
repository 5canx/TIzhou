// 登录页面交互逻辑
(function() {
    'use strict';

    // 登录方式切换
    const passwordTab = document.getElementById('password-tab');
    const codeTab = document.getElementById('code-tab');
    const passwordForm = document.getElementById('password-form');
    const codeForm = document.getElementById('code-form');

    if (passwordTab && codeTab && passwordForm && codeForm) {
        passwordTab.addEventListener('click', function() {
            passwordForm.style.display = 'flex';
            codeForm.style.display = 'none';
            passwordTab.classList.add('active');
            codeTab.classList.remove('active');
        });

        codeTab.addEventListener('click', function() {
            passwordForm.style.display = 'none';
            codeForm.style.display = 'flex';
            codeTab.classList.add('active');
            passwordTab.classList.remove('active');
        });
    }

    // 获取验证码功能
    const getCodeButton = document.querySelector('.get-code-btn');
    if (getCodeButton) {
        getCodeButton.addEventListener('click', function() {
            const emailInput = codeForm.querySelector('input[name="email"]');
            if (!emailInput || !emailInput.value) {
                showNotification('请先输入邮箱地址');
                return;
            }

            // 验证邮箱格式
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(emailInput.value)) {
                showNotification('请输入有效的邮箱地址');
                return;
            }

            // 发送请求获取验证码
            let countdown = 60;
            getCodeButton.disabled = true;
            getCodeButton.textContent = `${countdown}秒后重发`;

            const timer = setInterval(() => {
                countdown--;
                getCodeButton.textContent = `${countdown}秒后重发`;
                if (countdown <= 0) {
                    clearInterval(timer);
                    getCodeButton.disabled = false;
                    getCodeButton.textContent = '获取验证码';
                }
            }, 1000);

            // 这里应该有实际的后端请求逻辑
            console.log('发送验证码到邮箱:', emailInput.value);
            showNotification('验证码已发送，请查收');
        });
    }

    // 表单提交处理
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            // 可以在这里添加额外的表单验证逻辑
        });
    }

    if (codeForm) {
        codeForm.addEventListener('submit', function(e) {
            // 可以在这里添加额外的表单验证逻辑
        });
    }

    // 验证码图片点击刷新
    const captchaImg = document.querySelector('.captcha-img');
    if (captchaImg) {
        captchaImg.addEventListener('click', function() {
            // 添加时间戳防止缓存
            this.src = this.src.split('?')[0] + '?t=' + new Date().getTime();
        });
    }

    // 第三方登录处理
    const oauthButtons = document.querySelectorAll('.oauth-btn');
    oauthButtons.forEach(button => {
        button.addEventListener('click', function() {
            let provider = '';
            if (this.classList.contains('qq-login')) {
                provider = 'QQ授权登录';
            } else if (this.classList.contains('afdian-login')) {
                provider = '爱发电授权登录';
            }
            console.log(`使用${provider}登录`);
            // 这里应该有实际的第三方登录请求逻辑
            showNotification(`正在跳转到${provider}授权页面...`);
        });
    });

    // 通知提示功能
    function showNotification(message) {
        // 检查是否已存在通知元素
        let notification = document.getElementById('login-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'login-notification';
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.left = '50%';
            notification.style.transform = 'translateX(-50%)';
            notification.style.padding = '12px 20px';
            notification.style.backgroundColor = 'rgba(22, 93, 255, 0.9)';
            notification.style.color = 'white';
            notification.style.borderRadius = '4px';
            notification.style.zIndex = '1000';
            notification.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.05)';
            notification.style.fontFamily = 'Microsoft YaHei, SimHei, sans-serif';
            document.body.appendChild(notification);
        }

        notification.textContent = message;
        notification.style.opacity = '1';

        // 3秒后自动消失
        setTimeout(() => {
            notification.style.transition = 'opacity 0.5s ease';
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }, 3000);
    }

    // 添加页面加载动画
    document.addEventListener('DOMContentLoaded', function() {
        const loginCard = document.querySelector('.login-card');
        if (loginCard) {
            loginCard.style.opacity = '0';
            loginCard.style.transform = 'translateY(20px)';
            loginCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

            setTimeout(() => {
                loginCard.style.opacity = '1';
                loginCard.style.transform = 'translateY(0)';
            }, 100);
        }
    });
})();