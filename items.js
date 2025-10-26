/**
 * アイテムページのロジック
 */

let itemsData = {};
let currentCategory = 'all';
let currentPrice = 'all';
let currentStatus = 'all';
let searchTerm = '';

const searchBox = document.getElementById('searchBox');
const categorySelect = document.getElementById('categorySelect');
const priceSelect = document.getElementById('priceSelect');
const statusSelect = document.getElementById('statusSelect');
const clearFiltersBtn = document.getElementById('clearFiltersBtn');
const resultsCount = document.getElementById('resultsCount');
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
    
    // キャッシュを無効化するためにタイムスタンプを追加
    const timestamp = new Date().getTime();
    fetch(`items_data_final.json?t=${timestamp}`)
        .then(response => {
            console.log('レスポンス受信:', response.status);
            if (!response.ok) {
                throw new Error(`items_data_final.json: HTTP ${response.status}`);
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
                initializeCategorySelect();
                console.log('カテゴリセレクト初期化完了');
            } catch (error) {
                console.error('カテゴリセレクト初期化エラー:', error);
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

// カテゴリセレクトを初期化
function initializeCategorySelect() {
    // データの存在確認
    if (!itemsData || !itemsData.categories) {
        console.error('カテゴリデータが見つかりません');
        return;
    }
    
    const categories = [
        { value: 'all', text: 'すべてのカテゴリ' },
        ...Object.keys(itemsData.categories).map(categoryId => ({
            value: categoryId,
            text: itemsData.categories[categoryId].name
        }))
    ];

    if (categorySelect) {
        categorySelect.innerHTML = categories.map(cat => 
            `<option value="${cat.value}">${cat.text}</option>`
        ).join('');
    }
}

// イベントリスナー設定
function setupEventListeners() {
    // 検索ボックス
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            searchTerm = e.target.value.toLowerCase();
            renderItems();
        });
    }

    // カテゴリセレクト
    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            currentCategory = e.target.value;
            renderItems();
        });
    }

    // 価格セレクト
    if (priceSelect) {
        priceSelect.addEventListener('change', (e) => {
            currentPrice = e.target.value;
            renderItems();
        });
    }

    // ステータスセレクト
    if (statusSelect) {
        statusSelect.addEventListener('change', (e) => {
            currentStatus = e.target.value;
            renderItems();
        });
    }

    // フィルタークリアボタン
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            searchTerm = '';
            currentCategory = 'all';
            currentPrice = 'all';
            currentStatus = 'all';
            
            if (searchBox) searchBox.value = '';
            if (categorySelect) categorySelect.value = 'all';
            if (priceSelect) priceSelect.value = 'all';
            if (statusSelect) statusSelect.value = 'all';
            
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
    
    // ステータスフィルタリング
    if (currentStatus !== 'all') {
        console.log(`ステータスフィルタリング開始: ${currentStatus}`);
        allItems = allItems.filter(item => {
            const stats = item.stats || {};
            const statusMapping = {
                'physical-defense': '物理防御',
                'critical-rate': 'クリティカル率',
                'health': '体力',
                'health-regen': '体力回復',
                'mana': 'マナ',
                'magic-power': '魔法攻撃力',
                'movement-speed': '移動速度',
                'attack-damage': '攻撃力',
                'magic-defense': '魔法防御',
                'attack-speed': '攻撃速度',
                'lifesteal': 'ライフステール',
                'movement-speed-percent': '移動速度%'
            };
            
            const targetStat = statusMapping[currentStatus];
            return targetStat && stats[targetStat] !== undefined;
        });
        console.log(`ステータス "${currentStatus}" のアイテム数: ${allItems.length}`);
    }
    
    // 価格フィルタリング
    if (currentPrice !== 'all') {
        console.log(`価格フィルタリング開始: ${currentPrice}`);
        allItems = allItems.filter(item => {
            const price = item.price || 0;
            switch (currentPrice) {
                case '0-500':
                    return price >= 0 && price <= 500;
                case '500-1000':
                    return price > 500 && price <= 1000;
                case '1000-2000':
                    return price > 1000 && price <= 2000;
                case '2000+':
                    return price > 2000;
                default:
                    return true;
            }
        });
        console.log(`価格 "${currentPrice}" のアイテム数: ${allItems.length}`);
    }
    
    // 検索フィルタリング
    console.log('検索フィルタリング開始');
    console.log('allItems before search filter:', allItems);
    const filteredItems = allItems.filter(item => {
        console.log('検索フィルタリング中のアイテム:', item);
        return matchesSearch(item);
    });
    console.log(`検索フィルター後のアイテム数: ${filteredItems.length}`);
    
    // あいうえお順でソート
    filteredItems.sort((a, b) => {
        const nameA = a.name || '';
        const nameB = b.name || '';
        return nameA.localeCompare(nameB, 'ja');
    });
    
    if (filteredItems.length === 0) {
        itemsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>"${searchTerm}" に一致するアイテムが見つかりませんでした。</p>
            </div>
        `;
        return;
    }

    // あいうえお順で直接表示（カテゴリグループ化なし）
    console.log('あいうえお順で表示開始');
    
    if (!Array.isArray(filteredItems)) {
        console.error('filteredItems is not an array:', filteredItems);
        return;
    }
    
    const itemsHtml = filteredItems.map(item => {
        return `
            <div class="item-card" onclick="showItemDetail('${item.id}')">
                <div class="item-header">
                    <div class="item-price">${item.price}G</div>
                </div>
                <div class="item-content">
                    <img src="${getItemIconUrl(item.id)}" 
                         alt="${item.name}" 
                         class="item-icon"
                         onerror="this.src='https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/1001.png'">
                    <div class="item-details">
                        <div class="item-name">${item.name}</div>
                        <div class="item-effect">${item.plaintext || item.description || '基本アイテム'}</div>
                        <div class="item-stats-section">
                            <div class="stats-label">主要ステータス</div>
                            ${Object.keys(item.stats || {}).map(stat => `
                                <div class="stat-row">
                                    <span class="stat-name">${stat}</span>
                                    <span class="stat-value">+${item.stats[stat]}</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="item-tags">
                            ${item.tags.map(tag => `<span class="item-tag">${tag}</span>`).join('')}
                        </div>
                        ${item.buildsInto && item.buildsInto.length > 0 ? `
                            <div class="item-evolutions">
                                <div class="evolutions-label">進化先</div>
                                <div class="evolutions-list">
                                    ${item.buildsInto.slice(0, 2).map(buildId => `
                                        <div class="evolution-item">
                                            <img src="${getItemIconUrl(buildId)}" class="evolution-icon" alt="進化先">
                                            <div class="evolution-name">進化先</div>
                                        </div>
                                    `).join('')}
                                </div>
                                ${item.buildsInto.length > 2 ? `<div class="other-evolutions">他${item.buildsInto.length - 2}件</div>` : ''}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    itemsContainer.innerHTML = `
        <div class="items-grid">
            ${itemsHtml}
        </div>
    `;
    
    totalVisible = filteredItems.length;

    console.log(`表示されたアイテム数: ${totalVisible}`);
}

// アイテム詳細表示関数
function showItemDetail(itemId) {
    const item = itemsData.items.find(i => i.id === itemId);
    if (!item) return;
    
    const category = itemsData.categories[item.category];
    
    // モーダルを作成
    const modal = document.createElement('div');
    modal.className = 'item-detail-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeItemDetail()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h2>${item.name}</h2>
                <button class="close-modal-btn" onclick="closeItemDetail()">×</button>
            </div>
            <div class="modal-body">
                <div class="item-detail-header">
                    <img src="${getItemIconUrl(item.id)}" 
                         alt="${item.name}" 
                         class="detail-item-icon"
                         onerror="this.src='https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/1001.png'">
                    <div class="item-detail-info">
                        <div class="item-detail-price">
                            <span class="price-label">合計</span>
                            <span class="price-value">${item.price}G</span>
                            <span class="price-label">素材</span>
                            <span class="price-value">${item.price}G</span>
                            <span class="price-label">売却</span>
                            <span class="price-value">${item.sellPrice}G</span>
                        </div>
                        <div class="item-detail-category">${category.name} - ${category.subcategories[item.subcategory] || item.subcategory}</div>
                    </div>
                </div>
                
                <div class="item-detail-description">
                    <h3>アイテム説明</h3>
                    <div class="description-content">
                        ${item.fullDescription ? `<div class="full-description">${item.fullDescription}</div>` : ''}
                        ${item.plaintext ? `<div class="plaintext-description">${item.plaintext}</div>` : ''}
                    </div>
                </div>
                
                <div class="item-detail-stats">
                    <h3>付与ステータス</h3>
                    <div class="stats-grid">
                        ${Object.keys(item.stats || {}).map(stat => `
                            <div class="stat-item">
                                <span class="stat-name">${stat}</span>
                                <span class="stat-value">+${item.stats[stat]}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${item.buildsInto && item.buildsInto.length > 0 ? `
                    <div class="item-detail-evolutions">
                        <h3>進化先</h3>
                        <div class="evolutions-grid">
                            ${item.buildsInto.map(buildId => {
                                const buildItem = itemsData.items.find(i => i.id === buildId);
                                return buildItem ? `
                                    <div class="evolution-card" onclick="showItemDetail('${buildId}')">
                                        <img src="${getItemIconUrl(buildId)}" class="evolution-icon" alt="${buildItem.name}">
                                        <div class="evolution-name">${buildItem.name}</div>
                                    </div>
                                ` : '';
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${item.buildsFrom && item.buildsFrom.length > 0 ? `
                    <div class="item-detail-materials">
                        <h3>素材</h3>
                        <div class="materials-grid">
                            ${item.buildsFrom.map(materialId => {
                                const materialItem = itemsData.items.find(i => i.id === materialId);
                                return materialItem ? `
                                    <div class="material-card" onclick="showItemDetail('${materialId}')">
                                        <img src="${getItemIconUrl(materialId)}" class="material-icon" alt="${materialItem.name}">
                                        <div class="material-name">${materialItem.name}</div>
                                    </div>
                                ` : '';
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

// アイテム詳細を閉じる関数
function closeItemDetail() {
    const modal = document.querySelector('.item-detail-modal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

