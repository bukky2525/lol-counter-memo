/**
 * チャンピオン図鑑ページ
 * DDragon APIから直接チャンピオンデータを取得
 */

let championsData = {};
let filteredChampions = [];
let currentSearchTerm = '';
let currentTag = 'all';

// DOM要素
const searchInput = document.getElementById('searchInput');
const tagSelect = document.getElementById('tagSelect');
const clearFiltersBtn = document.getElementById('clearFilters');
const championsContainer = document.getElementById('championsContainer');
const resultsCount = document.getElementById('resultsCount');
const championModal = document.getElementById('championModal');

// DDragon APIのバージョン
let DDragonVersion = '25.21';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadChampionsFromDDragon();
    setupEventListeners();
});

// DDragon APIからチャンピオンデータを取得
async function loadChampionsFromDDragon() {
    const versions = ['25.21', '25.20', '25.19', '25.18', '25.17'];
    
    for (const version of versions) {
        try {
            console.log(`DDragon APIからチャンピオンデータを取得中... (バージョン: ${version})`);
            const apiUrl = `https://ddragon.leagueoflegends.com/cdn/${version}/data/ja_JP/champion.json`;
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
        
        // チャンピオンデータを処理
        championsData = data.data;
        console.log(`取得したチャンピオン数: ${Object.keys(championsData).length}`);
        
        // チャンピオンリストを作成
        filteredChampions = Object.values(championsData);
        
        console.log(`フィルタリング後のチャンピオン数: ${filteredChampions.length}`);
        
        // チャンピオンを表示
        renderChampions();
        updateResultsCount(filteredChampions.length);
        
            return; // 成功した場合は終了
            
    } catch (error) {
            console.error(`バージョン ${version} でのチャンピオンデータ取得に失敗:`, error);
            continue; // 次のバージョンを試す
        }
    }
    
    // すべてのバージョンが失敗した場合
    console.error('すべてのバージョンでチャンピオンデータの取得に失敗しました');
    showError('チャンピオンデータの取得に失敗しました。ネットワーク接続を確認してページを再読み込みしてください。');
}

// イベントリスナー設定
function setupEventListeners() {
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchTerm = e.target.value.toLowerCase();
            filterAndRenderChampions();
        });
    }
    
    if (tagSelect) {
        tagSelect.addEventListener('change', (e) => {
            currentTag = e.target.value;
            filterAndRenderChampions();
        });
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            clearAllFilters();
        });
    }
    
    // モーダル外クリックで閉じる
    if (championModal) {
        championModal.addEventListener('click', (e) => {
            if (e.target === championModal) {
                closeChampionModal();
            }
        });
    }
}

// チャンピオンをフィルタリングして表示
function filterAndRenderChampions() {
    let filtered = filteredChampions;

    // 検索フィルタリング
    if (currentSearchTerm) {
        filtered = filtered.filter(champion => {
            const name = champion.name ? champion.name.toLowerCase() : '';
            const id = champion.id ? champion.id.toLowerCase() : '';
            const title = champion.title ? champion.title.toLowerCase() : '';
            const tags = champion.tags ? champion.tags.join(' ').toLowerCase() : '';
            return name.includes(currentSearchTerm) || 
                   id.includes(currentSearchTerm) || 
                   title.includes(currentSearchTerm) ||
                   tags.includes(currentSearchTerm);
        });
    }

    // タグフィルタリング
    if (currentTag !== 'all') {
        filtered = filtered.filter(champion => {
            return champion.tags && champion.tags.includes(currentTag);
        });
    }

    // IDでソート
    filtered.sort((a, b) => {
        return a.name.localeCompare(b.name);
    });

    renderChampions(filtered);
    updateResultsCount(filtered.length);
}

// チャンピオンを表示
function renderChampions(champions = filteredChampions) {
    console.log('renderChampions called with', champions.length, 'champions');
    
    if (champions.length === 0) {
        championsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>"${currentSearchTerm}" に一致するチャンピオンが見つかりませんでした。</p>
                <p>別のキーワードで検索するか、タグフィルターを変更してみてください。</p>
            </div>
        `;
        return;
    }

    const championsHtml = `
        <div class="champions-grid">
            ${champions.map(champion => `
                <div class="champion-card" onclick="showChampionDetail('${champion.id}')">
                    <div class="champion-card-header">
                        <img src="${getChampionIconUrl(champion.id)}" 
                             alt="${champion.name}" 
                             class="champion-icon"
                             onerror="this.style.display='none'">
                        <div class="champion-card-title">
                            <h3>${champion.name}</h3>
                            <p class="champion-title">${champion.title || ''}</p>
                        </div>
                    </div>
                    
                    <div class="champion-tags">
                        ${(champion.tags || []).map(tag => `<span class="champion-tag">${tag}</span>`).join('')}
                    </div>
                    
                    <div class="champion-stats">
                        <div class="stat-row">
                            <span class="stat-label">HP:</span>
                            <span class="stat-value">${champion.stats?.hp || 'N/A'}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">攻撃力:</span>
                            <span class="stat-value">${champion.stats?.attackdamage || 'N/A'}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">防御力:</span>
                            <span class="stat-value">${champion.stats?.armor || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    championsContainer.innerHTML = championsHtml;
}

// チャンピオン詳細を表示
function showChampionDetail(championId) {
    const champion = championsData[championId];
    if (!champion) return;

    // モーダルヘッダーを更新
    const modalHeader = document.getElementById('modalHeader');
    modalHeader.innerHTML = `
        <img src="${getChampionIconUrl(champion.id)}" alt="${champion.name}" class="modal-champion-icon">
        <div class="modal-champion-info">
            <h2>${champion.name}</h2>
            <p class="modal-champion-title">${champion.title || ''}</p>
            <div class="modal-tags">
                ${(champion.tags || []).map(tag => `<span class="modal-tag">${tag}</span>`).join('')}
            </div>
        </div>
    `;
    
    // モーダルボディを更新
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="modal-section">
            <h4>チャンピオンの説明</h4>
            <p>${champion.blurb || '説明なし'}</p>
        </div>
        
        <div class="modal-section">
            <h4>基本ステータス</h4>
            <div class="modal-stats-grid">
                <div class="modal-stat-item">
                    <span class="modal-stat-label">HP:</span>
                    <span class="modal-stat-value">${champion.stats?.hp || 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">体力回復:</span>
                    <span class="modal-stat-value">${champion.stats?.hpregen ? champion.stats.hpregen.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">攻撃力:</span>
                    <span class="modal-stat-value">${champion.stats?.attackdamage || 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">攻撃速度:</span>
                    <span class="modal-stat-value">${champion.stats?.attackspeed ? champion.stats.attackspeed.toFixed(3) : 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">体力:</span>
                    <span class="modal-stat-value">${champion.stats?.armor || 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">魔法防御:</span>
                    <span class="modal-stat-value">${champion.stats?.spellblock || 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">移動速度:</span>
                    <span class="modal-stat-value">${champion.stats?.movespeed || 'N/A'}</span>
                </div>
                <div class="modal-stat-item">
                    <span class="modal-stat-label">攻撃範囲:</span>
                    <span class="modal-stat-value">${champion.stats?.attackrange || 'N/A'}</span>
                </div>
            </div>
        </div>
        
        <div class="modal-section">
            <h4>詳細情報</h4>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">難易度:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info?.difficulty || 0)}
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">攻撃:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info?.attack || 0)}
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">防御:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info?.defense || 0)}
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">魔法:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info?.magic || 0)}
                    </span>
                </div>
            </div>
        </div>
    `;
    
    // モーダルを表示
    championModal.classList.add('show');
}

// モーダルを閉じる
function closeChampionModal() {
    championModal.classList.remove('show');
}

// チャンピオンアイコンURLを取得
function getChampionIconUrl(championId) {
    return `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/champion/${championId}.png`;
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
    currentTag = 'all';
    
    searchInput.value = '';
    tagSelect.value = 'all';
    
    filterAndRenderChampions();
}

// エラー表示
function showError(message) {
    championsContainer.innerHTML = `
        <div class="no-results">
            <h3>エラーが発生しました</h3>
            <p>${message}</p>
        </div>
    `;
}

