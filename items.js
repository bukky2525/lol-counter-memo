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
        
        // 最初のアイテムの構造を確認
        const firstItemKey = Object.keys(itemsData)[0];
        const firstItem = itemsData[firstItemKey];
        console.log('最初のアイテム構造:', {
            key: firstItemKey,
            item: firstItem,
            id: firstItem.id,
            name: firstItem.name
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
            });
        
        console.log(`フィルタリング後のアイテム数: ${filteredItems.length}`);
        
        // アイテムを表示
        renderItems();
        updateResultsCount(filteredItems.length);
        
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
    updateResultsCount(filtered.length);
}

// アイテムを表示
function renderItems(items = filteredItems) {
    console.log('renderItems called with', items.length, 'items');
    console.log('itemsContainer:', itemsContainer);
    
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
                    <div class="item-stats">
                        ${getItemStats(item)}
                    </div>
                    <div class="item-tags">
                        ${(item.tags || []).map(tag => `<span class="item-tag">${tag}</span>`).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    console.log('Setting innerHTML, itemsHtml length:', itemsHtml.length);
    itemsContainer.innerHTML = itemsHtml;
    console.log('innerHTML set successfully');
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

    // バフ効果を取得
    const buffEffects = getBuffEffects(item);
    
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
                <div class="item-modal-description">
                    <h4>説明</h4>
                    <p>${cleanDescription}</p>
                </div>
                
                ${item.stats || item.description ? `
                    <div class="item-modal-stats">
                        <h4>ステータス</h4>
                        <div class="stats-grid">
                            ${getFormattedStatsOnly(item.stats, item.description)}
                        </div>
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

// HTMLタグを除去
function stripHtmlTags(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

// バフ効果を取得（「移動速度: +25」形式）
function getBuffEffects(item) {
    const effects = [];
    
    // statsからバフ効果を取得
    if (item.stats) {
        const statMap = {
            // 防御系
            'FlatPhysicalDamageMod': { name: '攻撃力', isPercentage: false },
            'FlatMagicDamageMod': { name: '魔力', isPercentage: false },
            'FlatHPPoolMod': { name: '体力', isPercentage: false },
            'FlatMPPoolMod': { name: 'マナ', isPercentage: false },
            'FlatArmorMod': { name: '物理防御', isPercentage: false },
            'FlatSpellBlockMod': { name: '魔法防御', isPercentage: false },
            'FlatHPRegenMod': { name: '体力自動回復', isPercentage: false },
            'FlatMPRegenMod': { name: 'マナ自動回復', isPercentage: false },
            'PercentArmorMod': { name: '物理防御', isPercentage: true },
            'PercentSpellBlockMod': { name: '魔法防御', isPercentage: true },
            'PercentHPPoolMod': { name: '体力', isPercentage: true },
            'PercentMPPoolMod': { name: 'マナ', isPercentage: true },
            
            // 攻撃系
            'FlatAttackSpeedMod': { name: '攻撃速度', isPercentage: true },
            'PercentAttackSpeedMod': { name: '攻撃速度', isPercentage: true },
            'FlatCritChanceMod': { name: 'クリティカル', isPercentage: true },
            'FlatCritDamageMod': { name: 'クリティカルダメージ', isPercentage: true },
            'PercentLifeStealMod': { name: 'ライフステール', isPercentage: true },
            'PercentSpellVampMod': { name: 'スペルヴァンプ', isPercentage: true },
            'rFlatArmorPenetrationMod': { name: '物理防御貫通', isPercentage: false },
            'rPercentArmorPenetrationMod': { name: '物理防御貫通', isPercentage: true },
            
            // 魔法系
            'rFlatMagicPenetrationMod': { name: '魔法防御貫通', isPercentage: false },
            'rPercentMagicPenetrationMod': { name: '魔法防御貫通', isPercentage: true },
            'rPercentCooldownMod': { name: 'スキルヘイスト', isPercentage: true },
            
            // 移動・その他
            'FlatMovementSpeedMod': { name: '移動速度', isPercentage: false },
            'PercentMovementSpeedMod': { name: '移動速度', isPercentage: true },
            'rFlatGoldPer10Mod': { name: 'ゴールド獲得', isPercentage: false },
            'FlatEXPBonus': { name: '経験値獲得', isPercentage: false },
            'PercentEXPBonus': { name: '経験値獲得', isPercentage: true },
            
            // 行動妨害耐性
            'rFlatTimeDeadMod': { name: '復活時間短縮', isPercentage: false },
            'rPercentTimeDeadMod': { name: '復活時間短縮', isPercentage: true }
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
                
                const sign = displayValue > 0 ? '+' : '';
                effects.push(`${stat.name}: ${sign}${displayValue}${stat.isPercentage ? '%' : ''}`);
            }
        });
    }
    
    // descriptionからバフ効果を抽出
    if (item.description) {
        const descriptionEffects = extractBuffEffectsFromDescription(item.description);
        effects.push(...descriptionEffects);
    }
    
    return effects;
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

// フォーマット済みステータスのみを取得（重複を完全に防ぐ）
function getFormattedStatsOnly(stats, description) {
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
    if (stats) {
        Object.entries(stats).forEach(([key, value]) => {
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
    if (description) {
        const descriptionEffects = extractBuffEffectsFromDescription(description);
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

// エラー表示
function showError(message) {
    itemsContainer.innerHTML = `
        <div class="no-results">
            <h3>エラーが発生しました</h3>
            <p>${message}</p>
        </div>
    `;
}