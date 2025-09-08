// 管理后台护眼模式设置
document.addEventListener('DOMContentLoaded', function() {
    // 查找主题切换按钮
    const themeButton = document.querySelector('#user-tools > button');
    
    if (themeButton) {
        // 1. 禁用自动主题切换功能
        // 阻止主题按钮的默认点击行为
        themeButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, true);
        
        // 2. 添加护眼模式样式
        function addEyeCareStyles() {
            // 检查是否已存在护眼模式样式
            if (document.getElementById('eye-care-styles')) {
                return;
            }
            
            const style = document.createElement('style');
            style.id = 'eye-care-styles';
            style.textContent = `
                /* 护眼模式样式 */
                :root {
                    /* 护眼模式颜色变量 */
                    --eye-care-bg: #f0f4f2;
                    --eye-care-text: #2d3e40;
                    --eye-care-bg-secondary: #e8ece9;
                    --eye-care-header: #d9e2dd;
                    --eye-care-border: #c3cdc7;
                    --eye-care-hover: #d1dad5;
                    --eye-care-primary: #4a6cf7;
                }
                
                /* 应用护眼模式 */
                body {
                    background-color: var(--eye-care-bg) !important;
                    color: var(--eye-care-text) !important;
                }
                
                /* 容器背景 */
                #container {
                    background-color: var(--eye-care-bg) !important;
                }
                
                /* 内容区域 */
                #content-main,
                #content,
                .card,
                .module,
                .dashboard-container,
                .question-management-container {
                    background-color: var(--eye-care-bg-secondary) !important;
                    color: var(--eye-care-text) !important;
                }
                
                /* 导航栏 */
                #header {
                    background-color: var(--eye-care-header) !important;
                    border-color: var(--eye-care-border) !important;
                }
                
                /* 侧边栏 */
                #nav-sidebar {
                    background-color: var(--eye-care-bg-secondary) !important;
                    border-color: var(--eye-care-border) !important;
                }
                
                #nav-sidebar a {
                    color: var(--eye-care-text) !important;
                }
                
                #nav-sidebar a:hover,
                #nav-sidebar a.active {
                    background-color: var(--eye-care-primary) !important;
                    color: white !important;
                }
                
                /* 表格 */
                table {
                    background-color: var(--eye-care-bg-secondary) !important;
                }
                
                th {
                    background-color: var(--eye-care-header) !important;
                    color: var(--eye-care-text) !important;
                    border-color: var(--eye-care-border) !important;
                }
                
                td {
                    border-color: var(--eye-care-border) !important;
                }
                
                tr:hover {
                    background-color: var(--eye-care-hover) !important;
                }
                
                /* 输入框 */
                input[type="text"],
                input[type="password"],
                input[type="email"],
                input[type="url"],
                input[type="number"],
                input[type="tel"],
                textarea,
                select,
                .vTextField,
                .vURLField,
                .vIntegerField,
                .vPositiveIntegerField,
                .vFloatField,
                .vEmailField {
                    background-color: var(--eye-care-bg) !important;
                    border-color: var(--eye-care-border) !important;
                    color: var(--eye-care-text) !important;
                }
                
                /* 按钮 */
                button,
                input[type="submit"],
                input[type="button"],
                input[type="reset"],
                .btn {
                    background-color: var(--eye-care-bg) !important;
                    color: var(--eye-care-text) !important;
                    border-color: var(--eye-care-border) !important;
                }
                
                /* 链接 */
                a {
                    color: var(--eye-care-primary) !important;
                }
            `;
            
            document.head.appendChild(style);
        }
        
        // 3. 应用护眼模式
        addEyeCareStyles();
        
        // 4. 在localStorage中保存设置，确保页面刷新后仍保持护眼模式
        localStorage.setItem('django_admin_theme', 'eye_care');
        
        console.log('管理后台护眼模式已启用，自动主题切换已禁用。');
    }
});