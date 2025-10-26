/**
 * DDragon APIから直接アイテムデータを取得するアイテムページ
 */

let itemsData = {};
let filteredItems = [];
let currentSearchTerm = '';
let currentCategory = 'all';

// DOM要素
const searchInput = document.getElementById('searchInput');
const categoryButtons = document.querySelectorAll('.lane-btn[data-category]');
const itemsContainer = document.getElementById('itemsContainer');

// DDragon APIのバージョン
const DDragonVersion = '15.17.1';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadItemsFromDDragon();
    setupEventListeners();
});

// DDragon APIからアイテムデータを取得
async function loadItemsFromDDragon() {
    try {
        console.log('DDragon APIからアイテムデータを取得中...');
        
        const response = await fetch(`https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/data/ja_JP/item.json`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('DDragon APIレスポンス:', data);
        
        // アイテムデータを処理
        itemsData = data.data;
        console.log(`取得したアイテム数: ${Object.keys(itemsData).length}`);
        
        // フィルタリング可能なアイテムのみを抽出
        filteredItems = Object.values(itemsData).filter(item => {
            return item.gold && item.gold.purchasable && item.maps && item.maps['11']; // Summoner's Riftで購入可能
        });
        
        console.log(`フィルタリング後のアイテム数: ${filteredItems.length}`);
        
        // アイテムを表示
        renderItems();
        
    } catch (error) {
        console.error('アイテムデータの取得に失敗:', error);
        showError('アイテムデータの取得に失敗しました。ページを再読み込みしてください。');
    }
}

// イベントリスナー設定
function setupEventListeners() {
    // 検索入力
    searchInput.addEventListener('input', (e) => {
        currentSearchTerm = e.target.value.toLowerCase();
        filterAndRenderItems();
    });

    // カテゴリボタン
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            currentCategory = button.getAttribute('data-category');
            filterAndRenderItems();
        });
    });
}

// アイテムをフィルタリングして表示
function filterAndRenderItems() {
    let filtered = filteredItems;

    // 検索フィルタリング
    if (currentSearchTerm) {
        filtered = filtered.filter(item => {
            const name = item.name ? item.name.toLowerCase() : '';
            const plaintext = item.plaintext ? item.plaintext.toLowerCase() : '';
            return name.includes(currentSearchTerm) || plaintext.includes(currentSearchTerm);
        });
    }

    // カテゴリフィルタリング
    if (currentCategory !== 'all') {
        filtered = filtered.filter(item => {
            return item.tags && item.tags.includes(currentCategory);
        });
    }

    // 価格でソート
    filtered.sort((a, b) => {
        const priceA = a.gold ? a.gold.total : 0;
        const priceB = b.gold ? b.gold.total : 0;
        return priceA - priceB;
    });

    renderItems(filtered);
}

// アイテムを表示
function renderItems(items = filteredItems) {
    if (items.length === 0) {
        itemsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>"${currentSearchTerm}" に一致するアイテムが見つかりませんでした。</p>
                <p>別のキーワードで検索するか、カテゴリフィルターを変更してみてください。</p>
            </div>
        `;
        return;
    }

    const itemsHtml = `
        <div class="items-grid">
            ${items.map(item => `
                <div class="item-card" onclick="showItemDetail('${item.id}')">
                    <div class="item-header">
                        <img src="${getItemIconUrl(item.id)}" 
                             alt="${item.name}" 
                             class="item-icon"
                             onerror="this.style.display='none'">
                        <div class="item-title">
                            <h3>${item.name}</h3>
                            <div class="item-price">${item.gold ? item.gold.total + 'G' : '価格不明'}</div>
                        </div>
                    </div>
                    <div class="item-tags">
                        ${(item.tags || []).map(tag => `<span class="item-tag">${tag}</span>`).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    itemsContainer.innerHTML = itemsHtml;
}

// アイテム詳細を表示
function showItemDetail(itemId) {
    const item = itemsData[itemId];
    if (!item) return;

    const modal = document.createElement('div');
    modal.className = 'item-modal show';
    modal.innerHTML = `
        <div class="item-modal-content">
            <button class="item-modal-close" onclick="this.closest('.item-modal').remove()">×</button>
            <div class="item-modal-header">
                <img src="${getItemIconUrl(itemId)}" 
                     alt="${item.name}" 
                     class="item-modal-icon"
                     onerror="this.style.display='none'">
                <div class="item-modal-title">
                    <h2>${item.name}</h2>
                    <div class="item-modal-price">${item.gold ? item.gold.total + 'G' : '価格不明'}</div>
                </div>
            </div>
            <div class="item-modal-body">
                ${item.description ? `<div class="item-modal-description">${item.description}</div>` : ''}
                
                ${item.stats ? `
                    <div class="item-modal-stats">
                        <h4>ステータス</h4>
                        <ul>
                            ${Object.entries(item.stats).map(([key, value]) => 
                                `<li>${key}: ${value}</li>`
                            ).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${item.buildsInto && item.buildsInto.length > 0 ? `
                    <div class="item-modal-builds">
                        <h4>進化先</h4>
                        <div class="item-builds-list">
                            ${item.buildsInto.slice(0, 2).map(buildId => {
                                const buildItem = itemsData[buildId];
                                return buildItem ? `
                                    <div class="item-build-item">
                                        <img src="${getItemIconUrl(buildId)}" 
                                             alt="${buildItem.name}" 
                                             class="item-build-icon"
                                             onerror="this.style.display='none'">
                                        <span class="item-build-name">${buildItem.name}</span>
                                    </div>
                                ` : '';
                            }).join('')}
                            ${item.buildsInto.length > 2 ? `<div class="other-evolutions">他${item.buildsInto.length - 2}件</div>` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // モーダル外クリックで閉じる
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// アイテムアイコンURLを取得
function getItemIconUrl(itemId) {
    return `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/${itemId}.png`;
}

// エラー表示
function showError(message) {
    itemsContainer.innerHTML = `
        <div class="no-results">
            <h3>エラーが発生しました</h3>
            <p>${message}</p>
        </div>
    `;
}