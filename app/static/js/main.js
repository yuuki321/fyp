function switchMode(mode) {
    const simpleModeBtn = document.getElementById('simpleMode');
    const advancedModeBtn = document.getElementById('advancedMode');
    const simpleForm = document.getElementById('simpleForm');
    const advancedForm = document.getElementById('advancedForm');

    if (mode === 'simple') {
        simpleModeBtn.classList.add('active');
        advancedModeBtn.classList.remove('active');
        simpleForm.classList.remove('hidden');
        advancedForm.classList.add('hidden');
    } else {
        simpleModeBtn.classList.remove('active');
        advancedModeBtn.classList.add('active');
        simpleForm.classList.add('hidden');
        advancedForm.classList.remove('hidden');
    }
}

// 更新速度和持续时间显示
document.addEventListener('DOMContentLoaded', function() {
    const tempoInput = document.querySelector('input[name="tempo"]');
    const tempoValue = document.getElementById('tempoValue');
    const durationInput = document.querySelector('input[name="duration"]');
    const durationValue = document.getElementById('durationValue');
    
    if (tempoInput && tempoValue) {
        tempoInput.addEventListener('input', function() {
            tempoValue.textContent = this.value + ' BPM';
        });
    }
    
    if (durationInput && durationValue) {
        durationInput.addEventListener('input', function() {
            durationValue.textContent = this.value;
        });
    }
});

// 音乐创建函数
function createMusic(mode) {
    const form = document.getElementById('musicGenerationForm');
    if (!form) {
        console.error('Form not found');
        return;
    }

    const formData = new FormData(form);
    formData.append('mode', mode);

    // 显示加载动画
    const submitBtn = form.querySelector('button[onclick*="createMusic"]');
    if (!submitBtn) {
        console.error('Submit button not found');
        return;
    }
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    submitBtn.disabled = true;

    // 显示错误消息的函数
    function showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'alert');
        
        const messageDiv = document.createElement('span');
        messageDiv.textContent = message;
        
        alertDiv.appendChild(messageDiv);
        alertDiv.appendChild(closeButton);
        form.insertBefore(alertDiv, form.firstChild);
    }

    // 发送请求
    fetch('/create_music', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => {
        // 检查是否重定向到登录页面
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        // 检查响应类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }
        throw new Error('未登录或服务器返回了非 JSON 响应');
    })
    .then(data => {
        if (!data) return; // 如果是重定向，data 将是 undefined
        
        // 恢复按钮状态
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        if (data.status === 'success') {
            // 显示成功消息
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
            const closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.className = 'btn-close';
            closeButton.setAttribute('data-bs-dismiss', 'alert');
            
            const messageDiv = document.createElement('span');
            messageDiv.textContent = data.message;
            
            alertDiv.appendChild(messageDiv);
            alertDiv.appendChild(closeButton);
            form.insertBefore(alertDiv, form.firstChild);
            
            // 重定向到项目页面
            if (data.project_id) {
                window.location.href = `/project/${data.project_id}`;
            }
        } else {
            showError(data.message || '生成音乐时发生错误');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        showError(error.message || '生成音乐时发生错误');
    });
}

// 消息提示函数
function showSuccessMessage(message) {
    // 实现成功消息提示
    alert(message); // 可以替换为更好的提示UI
}

function showErrorMessage(message) {
    // 实现错误消息提示
    alert(message); // 可以替换为更好的提示UI
}

// 文件选择处理
function handleFileSelect(input) {
    const fileName = input.files[0]?.name;
    const fileNameDisplay = input.closest('.custom-file-upload').querySelector('.selected-file-name');
    const filePreview = document.getElementById('filePreview');
    
    if (fileName) {
        fileNameDisplay.textContent = fileName;
        filePreview.classList.remove('d-none');
        filePreview.querySelector('.file-name').textContent = fileName;
    } else {
        fileNameDisplay.textContent = _('No file chosen');
        filePreview.classList.add('d-none');
    }
}

function clearFileInput() {
    const input = document.getElementById('incomplete_track');
    const fileNameDisplay = input.closest('.custom-file-upload').querySelector('.selected-file-name');
    const filePreview = document.getElementById('filePreview');
    
    input.value = '';
    fileNameDisplay.textContent = _('No file chosen');
    filePreview.classList.add('d-none');
} 