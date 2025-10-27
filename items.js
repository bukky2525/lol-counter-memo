/**
 * LoL Guide風アイテム一覧ページ
 * DDragon APIから直接アイテムデータを取得
 */

let itemsData = {};
let filteredItems = [];
let currentSearchTerm = '';
let currentCategory = 'all';
let currentPriceRange = 'all';
let currentStatFilter = 'all';

// DOM要素
const searchInput = document.getElementById('searchInput');
const categorySelect = document.getElementById('categorySelect');
const priceSelect = document.getElementById('priceSelect');
const statSelect = document.getElementById('statSelect');
const clearFiltersBtn = document.getElementById('clearFilters');
const itemsContainer = document.getElementById('itemsContainer');
const resultsCount = document.getElementById('resultsCount');
const searchSuggestions = document.getElementById('searchSuggestions');
const itemModal = document.getElementById('itemModal');

// DDragon APIのバージョン
let DDragonVersion = '15.21.1';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadItemsFromDDragon();
    setupEventListeners();
});

// DDragon APIからアイテムデータを取得
async function loadItemsFromDDragon() {
    const versions = ['15.21.1', '15.20.1', '15.19.1', '15.18.1', '15.17.1'];
    
    for (const version of versions) {
        try {
            console.log(`DDragon APIからアイテムデータを取得中... (バージョン: ${version})`);
            const apiUrl = `https://ddragon.leagueoflegends.com/cdn/${version}/data/ja_JP/item.json`;
            console.log('API URL:', apiUrl);
            
            const response = await fetch(apiUrl);
            
            console.log('Response status:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('DDragon APIレスポンス:', data);
            
            // 成功した場合はバージョンを更新
            DDragonVersion = version;
        
        // アイテムデータを処理
        itemsData = data.data;
        console.log(`取得したアイテム数: ${Object.keys(itemsData).length}`);
        
        // 最初のアイテムの構造を確認
        const firstItemKey = Object.keys(itemsData)[0];
        const firstItem = itemsData[firstItemKey];
        console.log('最初のアイテム構造:', {
            key: firstItemKey,
            item: firstItem,
            id: firstItem.id,
                name: firstItem.name,
                stats: firstItem.stats,
                buildsInto: firstItem.buildsInto,
                description: firstItem.description
        });
        
        // フィルタリング可能なアイテムのみを抽出（IDを追加）
        filteredItems = Object.entries(itemsData)
            .filter(([id, item]) => {
                return item.gold && item.gold.purchasable && item.maps && item.maps['11']; // Summoner's Riftで購入可能
            })
            .map(([id, item]) => ({
                ...item,
                id: id // アイテムIDを追加
            }))
            .filter((item, index, array) => {
                // 重複を防ぐため、同じIDのアイテムは最初のもののみ残す
                return array.findIndex(i => i.id === item.id) === index;
            })
            .filter((item, index, array) => {
                // 同じ名前のアイテムも重複を防ぐ（例：「スコーチクロウの幼体」）
                return array.findIndex(i => i.name === item.name) === index;
            });
        
        console.log(`フィルタリング後のアイテム数: ${filteredItems.length}`);
        
        // 重複チェックの詳細ログ
        const duplicateNames = [];
        const nameCounts = {};
        filteredItems.forEach(item => {
            if (nameCounts[item.name]) {
                nameCounts[item.name]++;
                if (!duplicateNames.includes(item.name)) {
                    duplicateNames.push(item.name);
                }
            } else {
                nameCounts[item.name] = 1;
            }
        });
        
        if (duplicateNames.length > 0) {
            console.log('重複が見つかったアイテム名:', duplicateNames);
            duplicateNames.forEach(name => {
                console.log(`- ${name}: ${nameCounts[name]}件`);
            });
        } else {
            console.log('重複するアイテム名はありません');
        }
        
        // アイテムを表示
        renderItems();
        updateResultsCount(filteredItems.length);
        
            return; // 成功した場合は終了
            
    } catch (error) {
            console.error(`バージョン ${version} でのアイテムデータ取得に失敗:`, error);
            continue; // 次のバージョンを試す
        }
    }
    
    // すべてのバージョンが失敗した場合
    console.error('すべてのバージョンでアイテムデータの取得に失敗しました');
    showError('アイテムデータの取得に失敗しました。ネットワーク接続を確認してページを再読み込みしてください。');
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
    
    if (priceSelect) {
        priceSelect.addEventListener('change', (e) => {
            currentPriceRange = e.target.value;
            filterAndRenderItems();
        });
    }
    
    if (statSelect) {
        statSelect.addEventListener('change', (e) => {
            currentStatFilter = e.target.value;
            filterAndRenderItems();
        });
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            clearAllFilters();
        });
    }
    
    // 検索候補のクリックイベント
    if (searchSuggestions) {
        searchSuggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-item')) {
                const itemName = e.target.getAttribute('data-item-name');
                selectSuggestion(itemName);
            }
        });
    }
    
    // クリック外しで候補を隠す
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-wrapper')) {
            hideSearchSuggestions();
        }
    });
    
    // モーダル外クリックで閉じる
    if (itemModal) {
        itemModal.addEventListener('click', (e) => {
            if (e.target === itemModal) {
                closeItemModal();
            }
        });
    }
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

    // 価格帯フィルタリング
    if (currentPriceRange !== 'all') {
        filtered = filtered.filter(item => {
            const price = item.gold ? item.gold.total : 0;
            switch (currentPriceRange) {
                case '0-500':
                    return price >= 0 && price <= 500;
                case '500-1000':
                    return price > 500 && price <= 1000;
                case '1000-2000':
                    return price > 1000 && price <= 2000;
                case '2000-3000':
                    return price > 2000 && price <= 3000;
                case '3000+':
                    return price > 3000;
                default:
                    return true;
            }
        });
    }

    // ステータスフィルタリング
    if (currentStatFilter !== 'all') {
        filtered = filtered.filter(item => {
            if (!item.stats) return false;
            
            const statMap = {
                'attack': 'FlatPhysicalDamageMod',
                'ability': 'FlatMagicDamageMod',
                'health': 'FlatHPPoolMod',
                'mana': 'FlatMPPoolMod',
                'armor': 'FlatArmorMod',
                'magic': 'FlatSpellBlockMod',
                'speed': 'FlatMovementSpeedMod',
                'haste': 'rPercentCooldownMod'
            };
            
            const statKey = statMap[currentStatFilter];
            return statKey && item.stats[statKey] && item.stats[statKey] !== 0;
        });
    }

    // 価格でソート
    filtered.sort((a, b) => {
        const priceA = a.gold ? a.gold.total : 0;
        const priceB = b.gold ? b.gold.total : 0;
        return priceA - priceB;
    });

    renderItems(filtered);
    updateResultsCount(filtered.length);
}

// アイテムを表示
function renderItems(items = filteredItems) {
    console.log('renderItems called with', items.length, 'items');
    console.log('First item structure:', items[0]);
    
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
                    
                    <div class="item-description">
                        <p>${getItemDescription(item)}</p>
                    </div>
                    
                    <div class="item-main-stats">
                        <h4>主要ステータス</h4>
                        <div class="main-stats-list">
                            ${getMainStats(item)}
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

    // description からHTMLタグを除去して本文のみ取得
    const cleanDescription = item.description 
        ? stripHtmlTags(item.description) 
        : item.plaintext || '説明なし';

    // モーダル要素を更新
    document.getElementById('modalItemIcon').src = getItemIconUrl(itemId);
    document.getElementById('modalItemIcon').alt = item.name;
    document.getElementById('modalItemName').textContent = item.name;
    document.getElementById('modalItemPrice').textContent = item.gold ? item.gold.total + 'G' : '価格不明';
    document.getElementById('modalItemDescription').textContent = cleanDescription;
    
    // ステータスを表示
    const statsHtml = getFormattedStats(item);
    document.getElementById('modalStatsGrid').innerHTML = statsHtml;
    
    // モーダルを表示
    itemModal.classList.add('show');
}

// モーダルを閉じる
function closeItemModal() {
    itemModal.classList.remove('show');
}

// HTMLタグを除去
function stripHtmlTags(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

// フォーマット済みステータスを取得
function getFormattedStats(item) {
    const formatted = [];
    const addedStats = new Set(); // 重複を防ぐためのSet
    
    const statMap = {
        'FlatPhysicalDamageMod': { name: '攻撃力', suffix: '' },
        'FlatMagicDamageMod': { name: '魔力', suffix: '' },
        'FlatHPPoolMod': { name: '体力', suffix: '' },
        'FlatMPPoolMod': { name: 'マナ', suffix: '' },
        'FlatArmorMod': { name: '物理防御', suffix: '' },
        'FlatSpellBlockMod': { name: '魔法防御', suffix: '' },
        'FlatMovementSpeedMod': { name: '移動速度', suffix: '' },
        'PercentAttackSpeedMod': { name: '攻撃速度', suffix: '%' },
        'FlatCritChanceMod': { name: 'クリティカル', suffix: '%' },
        'PercentLifeStealMod': { name: 'ライフステール', suffix: '%' },
        'FlatHPRegenMod': { name: '体力自動回復', suffix: '' },
        'FlatMPRegenMod': { name: 'マナ自動回復', suffix: '' },
        'rPercentCooldownMod': { name: 'スキルヘイスト', suffix: '%' }
    };
    
    // statsからステータスを取得
    if (item.stats) {
    Object.entries(item.stats).forEach(([key, value]) => {
        if (value && value !== 0 && statMap[key]) {
            const stat = statMap[key];
            let displayValue = value;
            
            // パーセンテージの場合は100倍して表示
            if (stat.suffix === '%' && value < 1) {
                displayValue = Math.round(value * 100);
                } else if (!stat.suffix) {
                    displayValue = Math.round(value);
                }
                
                const statNameKey = stat.name; // 名前のみをキーとして使用
                
                // 重複チェック（名前でチェック）
                if (!addedStats.has(statNameKey)) {
                    addedStats.add(statNameKey);
                    formatted.push(`<div class="stat-row"><span class="stat-name">${stat.name}:</span><span class="stat-value">${displayValue}${stat.suffix}</span></div>`);
                }
            }
        });
    }
    
    // descriptionからステータスを取得（statsにない場合の補完）
    if (item.description) {
        const descriptionEffects = extractBuffEffectsFromDescription(item.description);
        descriptionEffects.forEach(effect => {
            // 効果を解析（例：「マナ自動回復: +50%」から名前と値を分離）
            const parts = effect.split(': ');
            if (parts.length === 2) {
                const effectName = parts[0];
                const effectValue = parts[1];
                
                // 重複チェック（名前でチェック）
                if (!addedStats.has(effectName)) {
                    addedStats.add(effectName);
                    formatted.push(`<div class="stat-row"><span class="stat-name">${effectName}:</span><span class="stat-value">${effectValue}</span></div>`);
                }
            }
        });
    }
    
    return formatted.join('');
}

// descriptionからバフ効果を抽出
function extractBuffEffectsFromDescription(description) {
    const effects = [];
    const cleanDesc = stripHtmlTags(description);
    
    // パーセンテージバフ効果のパターンマッチング
    const buffPatterns = [
        { pattern: /基本マナ自動回復(\d+)%/, name: 'マナ自動回復' },
        { pattern: /基本体力自動回復(\d+)%/, name: '体力自動回復' },
        { pattern: /移動速度(\d+)/, name: '移動速度' },
        { pattern: /攻撃速度(\d+)%/, name: '攻撃速度' },
        { pattern: /クリティカル率(\d+)%/, name: 'クリティカル' },
        { pattern: /ライフステール(\d+)%/, name: 'ライフステール' },
        { pattern: /物理防御(\d+)/, name: '物理防御' },
        { pattern: /魔法防御(\d+)/, name: '魔法防御' },
        { pattern: /体力(\d+)/, name: '体力' },
        { pattern: /マナ(\d+)/, name: 'マナ' },
        { pattern: /攻撃力(\d+)/, name: '攻撃力' },
        { pattern: /魔力(\d+)/, name: '魔力' },
        { pattern: /スキルヘイスト(\d+)%/, name: 'スキルヘイスト' },
        { pattern: /クールダウン短縮(\d+)%/, name: 'スキルヘイスト' },
        { pattern: /クールダウン(\d+)%/, name: 'スキルヘイスト' }
    ];
    
    buffPatterns.forEach(({ pattern, name }) => {
        const match = cleanDesc.match(pattern);
        if (match) {
            const value = match[1];
            const isPercentage = pattern.source.includes('%');
            effects.push(`${name}: +${value}${isPercentage ? '%' : ''}`);
        }
    });
    
    return effects;
}


// アイテムのステータスを取得（カード表示用）
function getItemStats(item) {
    const stats = [];
    const addedStats = new Set(); // 重複を防ぐためのSet
    
    // statsからバフ効果を取得
    if (item.stats) {
        const statMap = {
            'FlatPhysicalDamageMod': { name: '攻撃力', suffix: '', isPercentage: false },
            'FlatMagicDamageMod': { name: '魔力', suffix: '', isPercentage: false },
            'FlatHPPoolMod': { name: '体力', suffix: '', isPercentage: false },
            'FlatMPPoolMod': { name: 'マナ', suffix: '', isPercentage: false },
            'FlatArmorMod': { name: '物理防御', suffix: '', isPercentage: false },
            'FlatSpellBlockMod': { name: '魔法防御', suffix: '', isPercentage: false },
            'FlatMovementSpeedMod': { name: '移動速度', suffix: '', isPercentage: false },
            'PercentAttackSpeedMod': { name: '攻撃速度', suffix: '%', isPercentage: true },
            'FlatCritChanceMod': { name: 'クリティカル', suffix: '%', isPercentage: true },
            'PercentLifeStealMod': { name: 'ライフステール', suffix: '%', isPercentage: true },
            'FlatHPRegenMod': { name: '体力自動回復', suffix: '', isPercentage: false },
            'FlatMPRegenMod': { name: 'マナ自動回復', suffix: '', isPercentage: false },
            'rPercentCooldownMod': { name: 'スキルヘイスト', suffix: '%', isPercentage: true }
        };
        
        Object.entries(item.stats).forEach(([key, value]) => {
            if (value && value !== 0 && statMap[key]) {
                const stat = statMap[key];
                let displayValue = value;
                
                // パーセンテージの場合は100倍して表示
                if (stat.isPercentage && value < 1 && value > -1) {
                    displayValue = Math.round(value * 100);
                } else if (!stat.isPercentage) {
                    displayValue = Math.round(value);
                }
                
                const statNameKey = stat.name; // 名前のみをキーとして使用
                
                // 重複チェック（名前でチェック）
                if (!addedStats.has(statNameKey)) {
                    addedStats.add(statNameKey);
                    const sign = displayValue > 0 ? '+' : '';
                    stats.push(`<span class="stat-item">${stat.name}: ${sign}${displayValue}${stat.suffix}</span>`);
                }
            }
        });
    }
    
    // descriptionからバフ効果を取得（statsにない場合の補完）
    if (item.description) {
        const descriptionEffects = extractBuffEffectsFromDescription(item.description);
        descriptionEffects.forEach(effect => {
            // 効果名を抽出（例：「マナ自動回復: +50%」から「マナ自動回復」）
            const effectName = effect.split(':')[0];
            
            // 重複チェック（名前でチェック）
            if (!addedStats.has(effectName)) {
                addedStats.add(effectName);
                stats.push(`<span class="stat-item">${effect}</span>`);
            }
        });
    }
    
    return stats.slice(0, 3).join(''); // 最大3つのステータスを表示
}

// アイテムアイコンURLを取得
function getItemIconUrl(itemId) {
    // アイテムIDが存在しない場合は空文字を返す
    if (!itemId) {
        console.warn('itemId is undefined or null:', itemId);
        return '';
    }
    // アイテムIDが数値の場合は文字列に変換
    const id = itemId.toString();
    return `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/${id}.png`;
}

// 検索数を更新
function updateResultsCount(count) {
    if (resultsCount) {
        resultsCount.textContent = `検索結果: ${count}件`;
    }
}

// フィルターをクリア
function clearAllFilters() {
    currentSearchTerm = '';
    currentCategory = 'all';
    currentPriceRange = 'all';
    currentStatFilter = 'all';
    
    searchInput.value = '';
    categorySelect.value = 'all';
    priceSelect.value = 'all';
    statSelect.value = 'all';
    
    hideSearchSuggestions();
    filterAndRenderItems();
}

// アイテムの説明を取得
function getItemDescription(item) {
    if (item.plaintext) {
        return item.plaintext;
    }
    if (item.description) {
        return stripHtmlTags(item.description).substring(0, 100) + '...';
    }
    return '説明なし';
}

// 主要ステータスを取得
function getMainStats(item) {
    const stats = [];
    const addedStats = new Set();
    
    console.log('getMainStats called for item:', item.name, 'stats:', item.stats);
    
    const statMap = {
        'FlatPhysicalDamageMod': { name: '攻撃力', suffix: '' },
        'FlatMagicDamageMod': { name: '魔力', suffix: '' },
        'FlatHPPoolMod': { name: '体力', suffix: '' },
        'FlatMPPoolMod': { name: 'マナ', suffix: '' },
        'FlatArmorMod': { name: '物理防御', suffix: '' },
        'FlatSpellBlockMod': { name: '魔法防御', suffix: '' },
        'FlatMovementSpeedMod': { name: '移動速度', suffix: '' },
        'PercentAttackSpeedMod': { name: '攻撃速度', suffix: '%' },
        'FlatCritChanceMod': { name: 'クリティカル', suffix: '%' },
        'PercentLifeStealMod': { name: 'ライフステール', suffix: '%' },
        'FlatHPRegenMod': { name: '体力自動回復', suffix: '' },
        'FlatMPRegenMod': { name: 'マナ自動回復', suffix: '' },
        'rPercentCooldownMod': { name: 'スキルヘイスト', suffix: '%' }
    };
    
    // statsからステータスを取得
    if (item.stats) {
        Object.entries(item.stats).forEach(([key, value]) => {
            if (value && value !== 0 && statMap[key]) {
                const stat = statMap[key];
                let displayValue = value;
                
                // パーセンテージの場合は100倍して表示
                if (stat.suffix === '%' && value < 1) {
                    displayValue = Math.round(value * 100);
                } else if (!stat.suffix) {
                    displayValue = Math.round(value);
                }
                
                if (!addedStats.has(stat.name)) {
                    addedStats.add(stat.name);
                    const sign = displayValue > 0 ? '+' : '';
                    stats.push(`<span class="main-stat">${stat.name}+${displayValue}${stat.suffix}</span>`);
                }
            }
        });
    }
    
    // descriptionからステータスを取得（statsにない場合の補完）
    if (item.description) {
        const descriptionEffects = extractBuffEffectsFromDescription(item.description);
        descriptionEffects.forEach(effect => {
            const effectName = effect.split(':')[0];
            if (!addedStats.has(effectName)) {
                addedStats.add(effectName);
                stats.push(`<span class="main-stat">${effect}</span>`);
            }
        });
    }
    
    console.log('getMainStats result:', stats);
    return stats.slice(0, 3).join(''); // 最大3つのステータスを表示
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