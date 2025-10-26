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
            filterAndRenderItems();
        });
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            currentCategory = e.target.value;
            filterAndRenderItems();
        });
    }
}

// アイテムをフィルタリングして表示
function filterAndRenderItems() {
    let filtered = [...filteredItems];
    
    // 検索フィルター
    if (currentSearchTerm) {
        filtered = filtered.filter(item => {
            return item.name.toLowerCase().includes(currentSearchTerm) ||
                   item.plaintext.toLowerCase().includes(currentSearchTerm) ||
                   item.description.toLowerCase().includes(currentSearchTerm);
        });
    }
    
    // カテゴリフィルター
    if (currentCategory !== 'all') {
        filtered = filtered.filter(item => {
            return item.tags && item.tags.includes(currentCategory);
        });
    }
    
    // 価格順でソート
    filtered.sort((a, b) => (a.gold.total || 0) - (b.gold.total || 0));
    
    renderFilteredItems(filtered);
}

// フィルタリングされたアイテムを表示
function renderFilteredItems(items) {
    if (!itemsContainer) return;
    
    // 結果数を更新
    if (resultsCount) {
        resultsCount.textContent = `検索結果: ${items.length}個`;
    }
    
    if (items.length === 0) {
        itemsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>条件を変更して再度検索してください。</p>
            </div>
        `;
        return;
    }
    
    // アイテムカードを生成
    const itemsHtml = items.map(item => createItemCard(item)).join('');
    
    itemsContainer.innerHTML = `
        <div class="items-grid">
            ${itemsHtml}
        </div>
    `;
}

// アイテムカードを作成
function createItemCard(item) {
    const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/${item.image.full}`;
    const price = item.gold.total || 0;
    const sellPrice = item.gold.sell || 0;
    
    // ステータス情報を取得
    const stats = getItemStats(item);
    
    // タグを表示用に変換
    const tags = item.tags ? item.tags.map(tag => getTagDisplayName(tag)).join(', ') : '';
    
    return `
        <div class="item-card" onclick="showItemDetail('${item.image.full.replace('.png', '')}')">
            <div class="item-header">
                <img src="${iconUrl}" 
                     alt="${item.name}" 
                     class="item-icon"
                     onerror="this.src='https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/1001.png'">
                <div class="item-price">${price}G</div>
            </div>
            <div class="item-content">
                <h3 class="item-name">${item.name}</h3>
                <p class="item-description">${item.plaintext || '基本アイテム'}</p>
                ${stats ? `<div class="item-stats">${stats}</div>` : ''}
                ${tags ? `<div class="item-tags">${tags}</div>` : ''}
            </div>
        </div>
    `;
}

// アイテムのステータス情報を取得
function getItemStats(item) {
    if (!item.stats) return '';
    
    const stats = [];
    const statMapping = {
        'FlatHPPoolMod': '体力',
        'FlatMPPoolMod': 'マナ',
        'FlatArmorMod': '物理防御',
        'FlatSpellBlockMod': '魔法防御',
        'FlatPhysicalDamageMod': '攻撃力',
        'FlatMagicDamageMod': '魔法攻撃力',
        'FlatMovementSpeedMod': '移動速度',
        'PercentAttackSpeedMod': '攻撃速度',
        'FlatCritChanceMod': 'クリティカル率',
        'PercentLifeStealMod': 'ライフステール'
    };
    
    Object.entries(item.stats).forEach(([key, value]) => {
        if (value && value !== 0 && statMapping[key]) {
            const displayValue = value > 1 ? Math.round(value) : (value * 100).toFixed(1) + '%';
            stats.push(`${statMapping[key]}: +${displayValue}`);
        }
    });
    
    return stats.length > 0 ? stats.join('<br>') : '';
}

// タグの表示名を取得
function getTagDisplayName(tag) {
    const tagMapping = {
        'Boots': 'ブーツ',
        'Health': '体力',
        'HealthRegen': '体力回復',
        'Mana': 'マナ',
        'ManaRegen': 'マナ回復',
        'Armor': '物理防御',
        'SpellBlock': '魔法防御',
        'Damage': '攻撃力',
        'SpellDamage': '魔法攻撃力',
        'AttackSpeed': '攻撃速度',
        'CriticalStrike': 'クリティカル',
        'LifeSteal': 'ライフステール',
        'SpellVamp': 'スペルヴァンプ',
        'CooldownReduction': 'クールダウン短縮',
        'Consumable': '消費アイテム',
        'Vision': '視界',
        'GoldPer': 'ゴールド獲得',
        'Lane': 'レーン',
        'Jungle': 'ジャングル',
        'Active': 'アクティブ',
        'Trinket': 'トリンケット'
    };
    
    return tagMapping[tag] || tag;
}

// アイテム詳細を表示
function showItemDetail(itemId) {
    const item = itemsData[itemId];
    if (!item) return;
    
    const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/item/${item.image.full}`;
    const price = item.gold.total || 0;
    const sellPrice = item.gold.sell || 0;
    const stats = getItemStats(item);
    const tags = item.tags ? item.tags.map(tag => getTagDisplayName(tag)).join(', ') : '';
    
    // モーダルを作成
    const modal = document.createElement('div');
    modal.className = 'item-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeItemDetail()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h2>${item.name}</h2>
                <button class="close-btn" onclick="closeItemDetail()">×</button>
            </div>
            <div class="modal-body">
                <div class="item-detail-header">
                    <img src="${iconUrl}" alt="${item.name}" class="detail-icon">
                    <div class="item-detail-info">
                        <div class="price-info">
                            <span class="price-label">購入価格:</span>
                            <span class="price-value">${price}G</span>
                        </div>
                        <div class="price-info">
                            <span class="price-label">売却価格:</span>
                            <span class="price-value">${sellPrice}G</span>
                        </div>
                    </div>
                </div>
                <div class="item-detail-description">
                    <h3>説明</h3>
                    <p>${item.description || item.plaintext || '説明なし'}</p>
                </div>
                ${stats ? `
                    <div class="item-detail-stats">
                        <h3>ステータス</h3>
                        <div class="stats-content">${stats}</div>
                    </div>
                ` : ''}
                ${tags ? `
                    <div class="item-detail-tags">
                        <h3>カテゴリ</h3>
                        <p>${tags}</p>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

// アイテム詳細を閉じる
function closeItemDetail() {
    const modal = document.querySelector('.item-modal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

// エラー表示
function showError(message) {
    if (itemsContainer) {
        itemsContainer.innerHTML = `
            <div class="error-message">
                <h3>エラー</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// 初期表示
function renderItems() {
    filterAndRenderItems();
}
