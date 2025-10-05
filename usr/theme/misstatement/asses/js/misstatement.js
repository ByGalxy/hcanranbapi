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
const imagePlaceholder = document.querySelector('.image-placeholder');


// 加载图片类型
async function loadImageTypes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/img/types`);
        const data = await response.json();

        // 只在首页更新选择框（帮助页没有imageTypeSelect元素）
        if (imageTypeSelect) {
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
        }

    } catch (error) {
        console.error('加载图片类型失败:', error);
        showStatus('error', '加载图片类型失败，请检查后端是否运行');
    }
}


// 加载服务状态
async function loadServiceStatus() {
    // 只在首页加载服务状态（帮助页没有serviceStatusDiv元素）
    if (!serviceStatusDiv) return;
    
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
    // 只在首页加载图片类型统计（帮助页没有typeStatsDiv元素）
    if (!typeStatsDiv || !imageTypeSelect) return;
    
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
                        ${data.vertical_count ? `竖屏: ${data.vertical_count}` : ''}
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
    // 只在首页执行（帮助页没有相关元素）
    if (!imageTypeSelect || !apiTypeSelect || !previewImage || !resultDisplay || !imagePlaceholder) {
        console.log('不在首页，无法获取随机图片');
        return;
    }
    
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
    // 只在首页显示加载动画（帮助页没有loadingSpinner元素）
    if (!loadingSpinner) return;
    
    loadingSpinner.style.display = show ? 'block' : 'none';
}


// 显示状态消息
function showStatus(type, message) {
    // 检查statusDiv是否存在（只在首页存在）
    if (!statusDiv) {
        // 在控制台输出消息作为替代
        console.log(`[${type}] ${message}`);
        return;
    }
    
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


// 首页标签页切换处理函数
function handleHomePageTabSwitch(tabText) {
    // 隐藏所有首页内容卡片
    const cards = document.querySelectorAll('.main-content .card');
    cards.forEach(card => {
        card.style.display = 'none';
    });

    // 根据标签页显示对应内容
    switch (tabText) {
        case '控制':
            // 显示API控制台和文档卡片（第1个和第2个.card）
            if (cards[0]) cards[0].style.display = 'block';
            break;
        case '文档':
            // 只显示文档卡片（第2个.card）
            if (cards[1]) cards[1].style.display = 'block';
            break;
        case '统计':
            // 创建并显示统计内容
            // showStatisticsTab();
            if (cards[2]) cards[2].style.display = 'block';
            break;
    }
}


// 帮助页面标签页切换处理函数
function handleHelpPageTabSwitch(tabText) {
    // 隐藏所有帮助内容卡片
    const cards = document.querySelectorAll('.main-content .card');
    cards.forEach(card => {
        card.style.display = 'none';
    });

    // 根据标签页显示对应内容
    switch (tabText) {
        case '指南':
            if (cards[0]) cards[0].style.display = 'block';
            break;
        case '说明':
            if (cards[1]) cards[1].style.display = 'block';
            break;
        case '问题':
            if (cards[2]) cards[2].style.display = 'block';
            break;
    }
}


// 加载统计信息
async function loadStatisticsData() {
    const statsContent = document.getElementById('statistics-content');
    if (!statsContent) return;

    try {
        // 显示加载状态
        statsContent.innerHTML = '<p>正在加载统计信息...</p>';

        // 获取服务状态
        const statusResponse = await fetch(`${API_BASE_URL}/api`);
        const statusData = await statusResponse.json();

        // 获取图片类型统计
        const typesResponse = await fetch(`${API_BASE_URL}/api/img/types`);
        const typesData = await typesResponse.json();

        // 构建统计内容HTML
        let statsHTML = `
            <div class="service-stats">
                <div class="service-stat">
                    <div class="service-stat-value">${statusData.version || 'N/A'}</div>
                    <div class="service-stat-label">版本</div>
                </div>
                <div class="service-stat">
                    <div class="service-stat-value">${statusData.start_time || 'N/A'}</div>
                    <div class="service-stat-label">启动时间</div>
                </div>
                <div class="service-stat">
                    <div class="service-stat-value">${typesData.count || 0}</div>
                    <div class="service-stat-label">图片类型数</div>
                </div>
            </div>
        `;

        // 添加各类型统计详情
        statsHTML += '<h3 style="margin: 20px 0 10px; color: var(--twitter-blue);"><i class="fas fa-list"></i> 各类型图片统计</h3>';
        statsHTML += '<div class="type-stats-detail">';

        // 遍历types数组
        for (const type of typesData.types || []) {
            try {
                const countResponse = await fetch(`${API_BASE_URL}/api/img/${type}/count`);
                const countData = await countResponse.json();

                statsHTML += `
                    <div class="type-stat-item">
                        <div class="type-name">${type}</div>
                        <div class="type-count">总数: ${countData.total_count || 0}</div>
                        ${countData.horizontal_count ? `<div class="screen-count">横屏: ${countData.horizontal_count}</div>` : ''}
                        ${countData.vertical_count ? `<div class="screen-count">竖屏: ${countData.vertical_count}</div>` : ''}
                    </div>
                `;
            } catch (error) {
                console.error(`获取${type}统计失败:`, error);
                statsHTML += `
                    <div class="type-stat-item">
                        <div class="type-name">${type}</div>
                        <div class="type-count">统计获取失败</div>
                    </div>
                `;
            }
        }

        statsHTML += '</div>';

        statsContent.innerHTML = statsHTML;
    } catch (error) {
        console.error('加载统计信息失败:', error);
        statsContent.innerHTML = '<p class="error">无法加载统计信息: ' + error.message + '</p>';
    }
}


// 初始化事件监听器
function initEventListeners() {
    // 只在存在相应元素的页面添加事件监听器
    if (fetchButton) {
        fetchButton.addEventListener('click', fetchRandomImage);
    }

    // 添加导航项点击事件
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // 页面导航功能
            const navText = this.querySelector('span').textContent;
            if (navText === '图片') {
                window.location.href = '/';
            } else if (navText === '帮助') {
                window.location.href = '/help';
            }
        });
    });

    // 添加标签页点击事件
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function () {
            // 移除所有标签页的active类
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            // 为当前点击的标签页添加active类
            this.classList.add('active');

            // 获取标签页文本
            const tabText = this.textContent;

            // 根据不同页面实现不同的标签页切换逻辑
            if (window.location.pathname === '/') {
                // 首页标签页切换
                handleHomePageTabSwitch(tabText);
            } else if (window.location.pathname === '/help') {
                // 帮助页面标签页切换
                handleHelpPageTabSwitch(tabText);
            }
        });
    });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadImageTypes();
});