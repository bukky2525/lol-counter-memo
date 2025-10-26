/**
 * アイテムページのロジック
 */

let itemsData = {};
let currentCategory = 'all';
let searchTerm = '';

const searchBox = document.getElementById('searchBox');
const categoryFilters = document.getElementById('categoryFilters');
const itemsContainer = document.getElementById('itemsContainer');
const DDragonVersion = '15.17.1';

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
            console.log('アイテムデータ読み込み成功:', data);
            itemsData = data;
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
        ...Object.keys(itemsData.categories).map(categoryId => ({
            id: categoryId,
            name: itemsData.categories[categoryId].name
        }))
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
    
    const nameMatch = item.name.toLowerCase().includes(searchTerm);
    const englishNameMatch = item.englishName.toLowerCase().includes(searchTerm);
    const descriptionMatch = item.description.toLowerCase().includes(searchTerm);
    const plaintextMatch = item.plaintext.toLowerCase().includes(searchTerm);
    
    return nameMatch || englishNameMatch || descriptionMatch || plaintextMatch;
}

// アイテムを描画
function renderItems() {
    itemsContainer.innerHTML = '';
    let totalVisible = 0;

    // 全アイテムを取得
    let allItems = itemsData.items || [];
    
    // カテゴリフィルタリング
    if (currentCategory !== 'all') {
        allItems = allItems.filter(item => item.category === currentCategory);
    }
    
    // 検索フィルタリング
    const filteredItems = allItems.filter(item => matchesSearch(item));
    
    if (filteredItems.length === 0) {
        itemsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>"${searchTerm}" に一致するアイテムが見つかりませんでした。</p>
            </div>
        `;
        return;
    }

    // カテゴリごとにグループ化
    const itemsByCategory = {};
    filteredItems.forEach(item => {
        const categoryKey = item.category;
        if (!itemsByCategory[categoryKey]) {
            itemsByCategory[categoryKey] = [];
        }
        itemsByCategory[categoryKey].push(item);
    });

    // カテゴリごとに表示
    Object.keys(itemsByCategory).forEach(categoryId => {
        const categoryItems = itemsByCategory[categoryId];
        const category = itemsData.categories[categoryId];
        
        const categorySection = document.createElement('div');
        categorySection.className = 'items-category';
        
        const itemsHtml = categoryItems.map(item => {
            const statsHtml = Object.keys(item.stats).map(stat => {
                const value = item.stats[stat];
                return `<span class="stat">${stat}: ${value}</span>`;
            }).join(' ');
            
            return `
                <div class="item-card">
                    <img src="${getItemIconUrl(item.id)}" 
                         alt="${item.name}" 
                         class="item-icon"
                         onerror="this.src='https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/1001.png'">
                    <div class="item-name">${item.name}</div>
                    <div class="item-category">${category.name} - ${category.subcategories[item.subcategory]}</div>
                    <div class="item-cost">🪙 ${item.price}G (売却: ${item.sellPrice}G)</div>
                    <div class="item-stats">${statsHtml}</div>
                    ${item.description ? `<div class="item-description">${item.description}</div>` : ''}
                </div>
            `;
        }).join('');

        categorySection.innerHTML = `
            <h2>${category.name} (${categoryItems.length}個)</h2>
            <div class="items-grid">
                ${itemsHtml}
            </div>
        `;

        itemsContainer.appendChild(categorySection);
        totalVisible += categoryItems.length;
    });

    console.log(`表示されたアイテム数: ${totalVisible}`);
}

