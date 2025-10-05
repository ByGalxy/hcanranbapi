// 当前页面所在域
const API_BASE_URL = window.location.origin;

const imageTypeSelect = document.getElementById('image-type');
const apiTypeSelect = document.getElementById('api-type');
const fetchButton = document.getElementById('fetch-btn');
const previewImage = document.getElementById('preview-image');
const resultDisplay = document.getElementById('result-display');
const statusDiv = document.getElementById('status');
const serviceStatusDiv = document.getElementById('service-status');
const typeStatsDiv = document.getElementById('type-stats');
const loadingSpinner = document.getElementById('loading-spinner');
const refreshButton = document.getElementById('refresh-btn');
const imagePlaceholder = document.querySelector('.image-placeholder');


// 加载图片类型
async function loadImageTypes() {
    try {
        showStatus('info', '正在加载图片类型...');
        const response = await fetch(`${API_BASE_URL}/api/img/types`);
        const data = await response.json();

        // 更新选择框
        imageTypeSelect.innerHTML = '';
        data.types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            imageTypeSelect.appendChild(option);
        });

        // 加载服务状态
        loadServiceStatus();

        // 加载图片类型统计
        loadTypeStats();

        showStatus('success', '图片类型加载完成');

    } catch (error) {
        console.error('加载图片类型失败:', error);
        showStatus('error', '加载图片类型失败，请检查后端是否运行');
    }
}


// 加载服务状态
async function loadServiceStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api`);
        const data = await response.json();

        // 创建状态卡片 - 根据实际API响应调整
        let statsHTML = `
            <div class="service-stats">
                <div class="service-stat">
                    <div class="service-stat-value">${data.status || 'N/A'}</div>
                    <div class="service-stat-label">服务状态</div>
                </div>
                <div class="service-stat">
                    <div class="service-stat-value">${data.version || 'N/A'}</div>
                    <div class="service-stat-label">API版本</div>
                </div>
                <div class="service-stat">
                    <div class="service-stat-value">服务运行中</div>
                    <div class="service-stat-label">状态</div>
                </div>
            </div>
            <pre style="margin-top: 15px; color: var(--twitter-gray);">${JSON.stringify(data, null, 2)}</pre>
        `;

        serviceStatusDiv.innerHTML = statsHTML;

    } catch (error) {
        console.error('加载服务状态失败:', error);
        serviceStatusDiv.innerHTML = '<p class="error">无法获取服务状态</p>';
    }
}


// 加载图片类型统计
async function loadTypeStats() {
    try {
        const types = Array.from(imageTypeSelect.options).map(opt => opt.value);
        let statsHTML = '';

        for (const type of types) {
            const response = await fetch(`${API_BASE_URL}/api/img/${type}/count`);
            const data = await response.json();

            statsHTML += `
                <div class="service-stat">
                    <div class="service-stat-value">${data.total_count || 0}</div>
                    <div class="service-stat-label">${type}</div>
                    <div style="font-size: 11px; margin-top: 5px; color: var(--twitter-gray);">
                        ${data.horizontal_count ? `横屏: ${data.horizontal_count}` : ''} 
                        ${data.vertical_count ? `| 竖屏: ${data.vertical_count}` : ''}
                    </div>
                </div>
            `;
        }

        typeStatsDiv.innerHTML = statsHTML;
    } catch (error) {
        console.error('加载类型统计失败:', error);
        typeStatsDiv.innerHTML = '<p class="error">无法获取类型统计</p>';
    }
}


// 获取随机图片
async function fetchRandomImage() {
    const imageType = imageTypeSelect.value;
    const apiType = apiTypeSelect.value;

    if (!imageType) {
        showStatus('error', '请选择图片类型');
        return;
    }

    try {
        showSpinner(true);
        let url, isImage;

        switch (apiType) {
            case 'direct':
                url = `${API_BASE_URL}/random_image/${imageType}`;
                isImage = true;
                break;
            case 'json':
                url = `${API_BASE_URL}/random_image/j/${imageType}`;
                isImage = false;
                break;
            case 'redirect':
                url = `${API_BASE_URL}/random_image/g/${imageType}`;
                isImage = true;
                break;
            default:
                showStatus('error', '无效的API类型');
                return;
        }

        showStatus('info', '请求中...');

        if (isImage) {
            // 处理图片响应
            if (apiType === 'redirect') {
                // 对于重定向，直接设置图片URL
                previewImage.src = url;
                resultDisplay.innerHTML = `<p>重定向到: <a href="${url}" target="_blank" style="color: var(--twitter-blue);">${url}</a></p>`;
            } else {
                // 对于直接图片，添加时间戳避免缓存
                const timestamp = new Date().getTime();
                previewImage.src = `${url}?t=${timestamp}`;
                resultDisplay.innerHTML = `<p>直接返回图片: <a href="${url}" target="_blank" style="color: var(--twitter-blue);">${url}</a></p>`;
            }

            // 图片加载完成后隐藏placeholder，显示图片
            previewImage.onload = function () {
                imagePlaceholder.style.display = 'none';
                previewImage.style.display = 'block';
                showStatus('success', '图片加载成功');
                showSpinner(false);
            };

            previewImage.onerror = function () {
                showSpinner(false);
                showStatus('error', '图片加载失败');
            };
        } else {
            // 处理JSON响应
            const response = await fetch(url);
            const data = await response.json();

            // 显示图片
            previewImage.src = data.path;
            previewImage.onload = function () {
                imagePlaceholder.style.display = 'none';
                previewImage.style.display = 'block';
            };

            // 显示JSON结果
            resultDisplay.innerHTML = `
                <pre>${JSON.stringify(data, null, 2)}</pre>
                <p>直接访问: <a href="${API_BASE_URL}${data.direct_url}" target="_blank" style="color: var(--twitter-blue);">${data.direct_url}</a></p>
                <p>重定向URL: <a href="${API_BASE_URL}${data.redirect_url}" target="_blank" style="color: var(--twitter-blue);">${data.redirect_url}</a></p>
            `;

            showStatus('success', 'JSON数据加载成功');
            showSpinner(false);
        }

    } catch (error) {
        console.error('获取随机图片失败:', error);
        showStatus('error', '获取随机图片失败');
        resultDisplay.innerHTML = `<p class="error">错误: ${error.message}</p>`;
        showSpinner(false);
    }
}


// 显示/隐藏加载动画
function showSpinner(show) {
    loadingSpinner.style.display = show ? 'block' : 'none';
}


// 显示状态消息
function showStatus(type, message) {
    statusDiv.textContent = message;
    statusDiv.className = 'status';

    switch (type) {
        case 'success':
            statusDiv.classList.add('success');
            break;
        case 'error':
            statusDiv.classList.add('error');
            break;
        case 'info':
            statusDiv.classList.add('info');
            break;
    }

    statusDiv.style.display = 'block';

    // 3秒后隐藏消息（如果是info）
    if (type === 'info') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
}


// 初始化事件监听器
function initEventListeners() {
    fetchButton.addEventListener('click', fetchRandomImage);
    refreshButton.addEventListener('click', loadImageTypes);

    // 添加导航项点击事件
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // 添加标签页点击事件
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function () {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadImageTypes();
});