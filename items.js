/**
 * DDragon APIから直接アイテムデータを取得するアイテムページ
 */

let itemsData = {};
let filteredItems = [];
let currentSearchTerm = '';
let currentCategory = 'all';

// DOM要素
const searchInput = document.getElementById('searchInput');
const categorySelect = document.getElementById('categorySelect');
const itemsContainer = document.getElementById('itemsContainer');
const resultsCount = document.getElementById('resultsCount');
const searchSuggestions = document.getElementById('searchSuggestions');

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
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchTerm = e.target.value.toLowerCase();
            showSearchSuggestions(e.target.value);
            filterAndRenderItems();
        });
        
        searchInput.addEventListener('focus', () => {
            if (searchInput.value) {
                showSearchSuggestions(searchInput.value);
            }
        });
        
        searchInput.addEventListener('blur', () => {
            // 少し遅延させてクリックイベントを処理
            setTimeout(() => {
                hideSearchSuggestions();
            }, 200);
        });
        
        // キーボードナビゲーション
        searchInput.addEventListener('keydown', handleSearchKeydown);
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            currentCategory = e.target.value;
            filterAndRenderItems();
        });
    }
    
    // クリック外しで候補を隠す
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-wrapper')) {
            hideSearchSuggestions();
        }
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

// 検索候補を表示
function showSearchSuggestions(query) {
    if (!query.trim()) {
        hideSearchSuggestions();
        return;
    }

    const suggestions = getSearchSuggestions(query);
    
    if (suggestions.length === 0) {
        hideSearchSuggestions();
        return;
    }

    const suggestionsHtml = suggestions.map(item => `
        <div class="suggestion-item" data-item-name="${item.name}">
            <img src="${getItemIconUrl(item.id)}" 
                 alt="${item.name}" 
                 class="suggestion-icon"
                 onerror="this.style.display='none'">
            <span class="suggestion-name">${item.name}</span>
            <span class="suggestion-price">${item.gold ? item.gold.total + 'G' : ''}</span>
            <span class="suggestion-category">${(item.tags || []).join(', ')}</span>
        </div>
    `).join('');

    searchSuggestions.innerHTML = suggestionsHtml;
    searchSuggestions.classList.add('show');
}

// 検索候補を非表示
function hideSearchSuggestions() {
    searchSuggestions.classList.remove('show');
}

// 検索候補を取得
function getSearchSuggestions(query) {
    const filtered = filteredItems.filter(item => {
        const name = item.name ? item.name.toLowerCase() : '';
        const plaintext = item.plaintext ? item.plaintext.toLowerCase() : '';
        return name.includes(query.toLowerCase()) || plaintext.includes(query.toLowerCase());
    });

    // 価格でソートして上位10件を返す
    return filtered
        .sort((a, b) => {
            const priceA = a.gold ? a.gold.total : 0;
            const priceB = b.gold ? b.gold.total : 0;
            return priceA - priceB;
        })
        .slice(0, 10);
}

// 候補を選択
function selectSuggestion(itemName) {
    searchInput.value = itemName;
    currentSearchTerm = itemName.toLowerCase();
    hideSearchSuggestions();
    filterAndRenderItems();
}

// キーボードナビゲーション
let selectedSuggestionIndex = -1;

function handleSearchKeydown(e) {
    const suggestions = searchSuggestions.querySelectorAll('.suggestion-item');
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
            updateSuggestionSelection(suggestions);
            break;
        case 'ArrowUp':
            e.preventDefault();
            selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
            updateSuggestionSelection(suggestions);
            break;
        case 'Enter':
            e.preventDefault();
            if (selectedSuggestionIndex >= 0 && suggestions[selectedSuggestionIndex]) {
                const itemName = suggestions[selectedSuggestionIndex].getAttribute('data-item-name');
                selectSuggestion(itemName);
            }
            break;
        case 'Escape':
            hideSearchSuggestions();
            selectedSuggestionIndex = -1;
            break;
    }
}

function updateSuggestionSelection(suggestions) {
    suggestions.forEach((suggestion, index) => {
        suggestion.classList.toggle('active', index === selectedSuggestionIndex);
    });
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