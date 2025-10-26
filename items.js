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
    console.log('データ読み込み開始...');
    
    fetch('items_data.json')
        .then(response => {
            console.log('レスポンス受信:', response.status);
            if (!response.ok) {
                throw new Error(`items_data.json: HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('JSON解析成功:', data);
            console.log('アイテム数:', data.items ? data.items.length : 'undefined');
            console.log('カテゴリ数:', data.categories ? Object.keys(data.categories).length : 'undefined');
            console.log('最初の5個のアイテム:', data.items ? data.items.slice(0, 5).map(item => item.name) : 'undefined');
            
            // データの存在確認
            if (!data.items || !Array.isArray(data.items)) {
                throw new Error('items配列が見つかりません');
            }
            if (!data.categories || typeof data.categories !== 'object') {
                throw new Error('categoriesオブジェクトが見つかりません');
            }
            
            itemsData = data;
            console.log('itemsData設定完了:', itemsData);
            
            try {
                initializeCategoryButtons();
                console.log('カテゴリボタン初期化完了');
            } catch (error) {
                console.error('カテゴリボタン初期化エラー:', error);
                throw error;
            }
            
            try {
                renderItems();
                console.log('アイテム描画完了');
            } catch (error) {
                console.error('アイテム描画エラー:', error);
                throw error;
            }
        })
        .catch(error => {
            console.error('データの読み込みに失敗しました:', error);
            itemsContainer.innerHTML = `
                <div class="no-results">
                    <h3>データの読み込みに失敗しました</h3>
                    <p>エラー: ${error.message}</p>
                    <p>ページを再読み込みしてください。</p>
                </div>
            `;
        });
}

// カテゴリボタンを初期化
function initializeCategoryButtons() {
    // データの存在確認
    if (!itemsData || !itemsData.categories) {
        console.error('カテゴリデータが見つかりません');
        return;
    }
    
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
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            searchTerm = e.target.value.toLowerCase();
            renderItems();
        });
    }
}

// アイテムアイコンURLを取得
function getItemIconUrl(itemId) {
    return `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/${itemId}.png`;
}

// 検索マッチング
function matchesSearch(item) {
    console.log('matchesSearch呼び出し:', item);
    if (!searchTerm) return true;
    
    const nameMatch = (item.name || '').toLowerCase().includes(searchTerm);
    const englishNameMatch = (item.englishName || '').toLowerCase().includes(searchTerm);
    const descriptionMatch = (item.description || '').toLowerCase().includes(searchTerm);
    const plaintextMatch = (item.plaintext || '').toLowerCase().includes(searchTerm);
    
    console.log('検索結果:', { nameMatch, englishNameMatch, descriptionMatch, plaintextMatch });
    return nameMatch || englishNameMatch || descriptionMatch || plaintextMatch;
}

// アイテムを描画
function renderItems() {
    console.log('renderItems開始');
    console.log('itemsData:', itemsData);
    
    itemsContainer.innerHTML = '';
    let totalVisible = 0;

    // データの存在確認
    if (!itemsData || !itemsData.items || !Array.isArray(itemsData.items)) {
        console.error('itemsDataが正しく読み込まれていません');
        console.error('itemsData:', itemsData);
        itemsContainer.innerHTML = `
            <div class="no-results">
                <h3>データの読み込みエラー</h3>
                <p>アイテムデータが正しく読み込まれていません。</p>
            </div>
        `;
        return;
    }

    // 全アイテムを取得
    let allItems = itemsData.items;
    console.log(`全アイテム数: ${allItems.length}`);
    console.log('allItems:', allItems);
    console.log('最初の10個のアイテム名:', allItems.slice(0, 10).map(item => item.name));
    
    // カテゴリフィルタリング
    if (currentCategory !== 'all') {
        console.log(`カテゴリフィルタリング開始: ${currentCategory}`);
        console.log('allItems before filter:', allItems);
        allItems = allItems.filter(item => {
            console.log('フィルタリング中のアイテム:', item);
            return item.category === currentCategory;
        });
        console.log(`カテゴリ "${currentCategory}" のアイテム数: ${allItems.length}`);
    }
    
    // 検索フィルタリング
    console.log('検索フィルタリング開始');
    console.log('allItems before search filter:', allItems);
    const filteredItems = allItems.filter(item => {
        console.log('検索フィルタリング中のアイテム:', item);
        return matchesSearch(item);
    });
    console.log(`検索フィルター後のアイテム数: ${filteredItems.length}`);
    
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
    console.log('グループ化開始, filteredItems:', filteredItems);
    
    if (!Array.isArray(filteredItems)) {
        console.error('filteredItems is not an array:', filteredItems);
        return;
    }
    
    filteredItems.forEach(item => {
        console.log('グループ化中のアイテム:', item);
        const categoryKey = item.category;
        if (!itemsByCategory[categoryKey]) {
            itemsByCategory[categoryKey] = [];
        }
        itemsByCategory[categoryKey].push(item);
    });

    console.log('カテゴリ別グループ化完了:', Object.keys(itemsByCategory));

    // カテゴリごとに表示
    Object.keys(itemsByCategory).forEach(categoryId => {
        console.log(`カテゴリ "${categoryId}" を処理中...`);
        const categoryItems = itemsByCategory[categoryId];
        const category = itemsData.categories[categoryId];
        
        if (!category) {
            console.warn(`カテゴリ "${categoryId}" が見つかりません`);
            return;
        }
        
        const categorySection = document.createElement('div');
        categorySection.className = 'items-category';
        
        const itemsHtml = categoryItems.map(item => {
            const statsHtml = Object.keys(item.stats || {}).map(stat => {
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
                    <div class="item-category">${category.name} - ${category.subcategories[item.subcategory] || item.subcategory}</div>
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

