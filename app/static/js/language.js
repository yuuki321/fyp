// 语言切换功能

// 当前语言，默认为简体中文
let currentLanguage = localStorage.getItem('language') || 'zh_CN';

// 初始化函数 - 在页面加载时调用
function initLanguage() {
    // 设置当前语言
    setLanguage(currentLanguage);
    // 高亮显示当前语言的选择项
    highlightCurrentLanguage();
}

// 设置语言
function setLanguage(lang) {
    if (!translations[lang]) {
        console.error(`不支持的语言: ${lang}`);
        return;
    }
    
    // 保存语言选择到本地存储
    localStorage.setItem('language', lang);
    currentLanguage = lang;
    
    // 翻译所有带有 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // 翻译所有带有 data-i18n-placeholder 属性的输入元素
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            element.placeholder = translations[lang][key];
        }
    });
    
    // 翻译所有带有 data-i18n-title 属性的元素
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        if (translations[lang][key]) {
            element.title = translations[lang][key];
        }
    });
    
    // 更新导航栏中当前语言的显示
    updateLanguageDisplay(lang);
}

// 高亮显示当前语言的选项
function highlightCurrentLanguage() {
    document.querySelectorAll('.language-item').forEach(item => {
        const itemLang = item.getAttribute('data-lang');
        if (itemLang === currentLanguage) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// 更新导航栏中当前语言的显示
function updateLanguageDisplay(lang) {
    const languageText = document.getElementById('current-language-text');
    if (languageText) {
        switch (lang) {
            case 'en':
                languageText.textContent = 'English';
                break;
            case 'zh_CN':
                languageText.textContent = '简体中文';
                break;
            case 'zh_TW':
                languageText.textContent = '繁體中文';
                break;
            default:
                languageText.textContent = lang;
        }
    }
}

// 切换语言
function switchLanguage(lang) {
    // 先在前端设置语言
    setLanguage(lang);
    highlightCurrentLanguage();
    
    // 调用API保存语言设置到后端
    fetch('/auth/change_language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            language: lang
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 重新加载页面以完全应用新语言
            window.location.reload();
        } else {
            console.error('更改语言失败:', data.message);
        }
    })
    .catch(error => {
        console.error('API调用出错:', error);
    });
    
    return false; // 阻止链接的默认行为
}

// 在页面加载完成后初始化语言
document.addEventListener('DOMContentLoaded', initLanguage); 