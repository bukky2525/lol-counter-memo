/**
 * アイテムページのロジック
 */

let itemsData = {};
let currentCategory = 'all';
let searchTerm = '';

const searchBox = document.getElementById('searchBox');
const categoryFilters = document.getElementById('categoryFilters');
const itemsContainer = document.getElementById('itemsContainer');
const DDragonVersion = '14.24.1';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    setupEventListeners();
});

// データ読み込み
function loadData() {
    fetch('items_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`items_data.json: HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('アイテムデータ読み込み成功');
            itemsData = data.categories;
            initializeCategoryButtons();
            renderItems();
        })
        .catch(error => {
            console.error('データの読み込みに失敗しました:', error);
            itemsContainer.innerHTML = `
                <div class="no-results">
                    <h3>データの読み込みに失敗しました</h3>
                    <p>エラー: ${error.message}</p>
                </div>
            `;
        });
}

// カテゴリボタンを初期化
function initializeCategoryButtons() {
    const categories = [
        { id: 'all', name: '全アイテム' },
        { id: 'starter', name: 'スタート' },
        { id: 'boots', name: 'ブーツ' },
        { id: 'legendary', name: 'レジェンダリー' },
        { id: 'mythic', name: 'ミシック' },
        { id: 'support', name: 'サポート' },
        { id: 'consumable', name: '消耗品' }
    ];

    categoryFilters.innerHTML = categories.map(cat => 
        `<button class="category-btn ${cat.id === 'all' ? 'active' : ''}" data-category="${cat.id}">${cat.name}</button>`
    ).join('');
}

// イベントリスナー設定
function setupEventListeners() {
    // カテゴリフィルター
    categoryFilters.addEventListener('click', (e) => {
        if (e.target.classList.contains('category-btn')) {
            document.querySelectorAll('.category-btn').forEach(btn => 
                btn.classList.remove('active')
            );
            e.target.classList.add('active');
            currentCategory = e.target.getAttribute('data-category');
            renderItems();
        }
    });

    // 検索ボックス
    searchBox.addEventListener('input', (e) => {
        searchTerm = e.target.value.toLowerCase();
        renderItems();
    });
}

// アイテムアイコンURLを取得
function getItemIconUrl(itemId) {
    return `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/${itemId}.png`;
}

// 検索マッチング
function matchesSearch(item) {
    if (!searchTerm) return true;
    
    const nameJpMatch = item.nameJp.toLowerCase().includes(searchTerm);
    const nameEnMatch = item.nameEn.toLowerCase().includes(searchTerm);
    const statsMatch = item.stats.toLowerCase().includes(searchTerm);
    
    return nameJpMatch || nameEnMatch || statsMatch;
}

// アイテムを描画
function renderItems() {
    itemsContainer.innerHTML = '';
    let totalVisible = 0;

    Object.keys(itemsData).forEach(categoryId => {
        // カテゴリフィルタリング
        if (currentCategory !== 'all' && currentCategory !== categoryId) {
            return;
        }

        const category = itemsData[categoryId];
        
        // 検索フィルタリング
        const filteredItems = category.items.filter(item => matchesSearch(item));
        
        if (filteredItems.length === 0) {
            return;
        }

        const categorySection = document.createElement('div');
        categorySection.className = 'items-category';
        
        const itemsHtml = filteredItems.map(item => `
            <div class="item-card">
                <img src="${getItemIconUrl(item.id)}" 
                     alt="${item.nameJp}" 
                     class="item-icon"
                     onerror="this.src='https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/1001.png'">
                <div class="item-name">${item.nameJp}</div>
                <div class="item-name-en">${item.nameEn}</div>
                <div class="item-cost">🪙 ${item.cost}G</div>
                <div class="item-stats">${item.stats}</div>
            </div>
        `).join('');

        categorySection.innerHTML = `
            <h2>${category.name}</h2>
            <div class="items-grid">
                ${itemsHtml}
            </div>
        `;

        itemsContainer.appendChild(categorySection);
        totalVisible += filteredItems.length;
    });

    // 検索結果なし
    if (totalVisible === 0) {
        itemsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>"${searchTerm}" に一致するアイテムが見つかりませんでした。</p>
            </div>
        `;
    }
}

