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
let DDragonVersion = '14.24.1';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadChampionsFromDDragon();
    setupEventListeners();
});

// チャンピオンデータを読み込み
function loadChampionsFromDDragon() {
    console.log('チャンピオンデータを読み込み中...');
    
    // ローカルのchampion_images.jsonから読み込み
    fetch('champion_images.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('チャンピオンデータ読み込み成功');
            
            // champion_images.jsonのデータをチャンピオンリストに変換
            filteredChampions = Object.entries(data).map(([japaneseName, englishName]) => ({
                id: englishName,
                name: japaneseName,
                title: '',  // DDragonから詳細を取得できない場合は空
                tags: [],   // デフォルトで空
                stats: {}   // デフォルトで空
            }));
            
            // チャンピオンデータを保存（モーダル表示用）
            championsData = {};
            filteredChampions.forEach(champion => {
                championsData[champion.id] = champion;
            });
            
            console.log(`チャンピオン数: ${filteredChampions.length}`);
            
            // チャンピオンを表示
            renderChampions();
            updateResultsCount(filteredChampions.length);
        })
        .catch(error => {
            console.error('チャンピオンデータの読み込みに失敗しました:', error);
            showError('チャンピオンデータの読み込みに失敗しました。ページを再読み込みしてください。');
        });
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

    // タグフィルタリング（チャンピオンデータにタグ情報がない場合はスキップ）
    if (currentTag !== 'all' && filtered.length > 0 && filtered[0].tags && filtered[0].tags.length > 0) {
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
                    
                    ${champion.tags && champion.tags.length > 0 ? `
                    <div class="champion-tags">
                        ${champion.tags.map(tag => `<span class="champion-tag">${tag}</span>`).join('')}
                    </div>
                    ` : ''}
                    
                    ${champion.stats && Object.keys(champion.stats).length > 0 ? `
                    <div class="champion-stats">
                        ${champion.stats.hp ? `
                        <div class="stat-row">
                            <span class="stat-label">HP:</span>
                            <span class="stat-value">${champion.stats.hp}</span>
                        </div>
                        ` : ''}
                        ${champion.stats.attackdamage ? `
                        <div class="stat-row">
                            <span class="stat-label">攻撃力:</span>
                            <span class="stat-value">${champion.stats.attackdamage}</span>
                        </div>
                        ` : ''}
                        ${champion.stats.armor ? `
                        <div class="stat-row">
                            <span class="stat-label">防御力:</span>
                            <span class="stat-value">${champion.stats.armor}</span>
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
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
            <p class="modal-champion-title">${champion.title || '情報なし'}</p>
            <div class="modal-tags">
                ${champion.tags && champion.tags.length > 0 
                    ? champion.tags.map(tag => `<span class="modal-tag">${tag}</span>`).join('') 
                    : '<span class="modal-tag">情報なし</span>'}
            </div>
        </div>
    `;
    
    // モーダルボディを更新
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="modal-section">
            <h4>チャンピオン情報</h4>
            <p>このチャンピオンの詳細情報はDDragon APIから取得されています。</p>
            <p><strong>日本語名:</strong> ${champion.name}</p>
            <p><strong>英語名:</strong> ${champion.id}</p>
            ${champion.blurb ? `<p><strong>説明:</strong> ${champion.blurb}</p>` : ''}
        </div>
        
        ${champion.stats && Object.keys(champion.stats).length > 0 ? `
        <div class="modal-section">
            <h4>基本ステータス</h4>
            <div class="modal-stats-grid">
                ${champion.stats.hp ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">HP:</span>
                    <span class="modal-stat-value">${champion.stats.hp}</span>
                </div>
                ` : ''}
                ${champion.stats.hpregen ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">体力回復:</span>
                    <span class="modal-stat-value">${champion.stats.hpregen.toFixed(2)}</span>
                </div>
                ` : ''}
                ${champion.stats.attackdamage ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">攻撃力:</span>
                    <span class="modal-stat-value">${champion.stats.attackdamage}</span>
                </div>
                ` : ''}
                ${champion.stats.attackspeed ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">攻撃速度:</span>
                    <span class="modal-stat-value">${champion.stats.attackspeed.toFixed(3)}</span>
                </div>
                ` : ''}
                ${champion.stats.armor ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">物理防御:</span>
                    <span class="modal-stat-value">${champion.stats.armor}</span>
                </div>
                ` : ''}
                ${champion.stats.spellblock ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">魔法防御:</span>
                    <span class="modal-stat-value">${champion.stats.spellblock}</span>
                </div>
                ` : ''}
                ${champion.stats.movespeed ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">移動速度:</span>
                    <span class="modal-stat-value">${champion.stats.movespeed}</span>
                </div>
                ` : ''}
                ${champion.stats.attackrange ? `
                <div class="modal-stat-item">
                    <span class="modal-stat-label">攻撃範囲:</span>
                    <span class="modal-stat-value">${champion.stats.attackrange}</span>
                </div>
                ` : ''}
            </div>
        </div>
        ` : '<p class="modal-section">ステータス情報なし</p>'}
        
        ${champion.info && Object.keys(champion.info).length > 0 ? `
        <div class="modal-section">
            <h4>詳細情報</h4>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">難易度:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info.difficulty || 0)}
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">攻撃:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info.attack || 0)}
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">防御:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info.defense || 0)}
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">魔法:</span>
                    <span class="info-value">
                        ${'⭐'.repeat(champion.info.magic || 0)}
                    </span>
                </div>
            </div>
        </div>
        ` : ''}
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

