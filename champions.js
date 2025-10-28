/**
 * チャンピオン図鑑ページ
 * DDragon APIから直接チャンピオンデータを取得
 */

let championsData = {};
let filteredChampions = [];
let currentSearchTerm = '';
let currentTag = 'all';
let currentLane = 'all';
let championImages = {}; // champion_images.jsonのデータ

// DOM要素
const searchInput = document.getElementById('searchInput');
const laneSelect = document.getElementById('laneSelect');
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
    
    // チャンピオン情報とカウンターデータを同時に読み込み
    Promise.all([
        fetch('champion_images.json').then(r => r.json()),
        fetch('counter_data.json').then(r => r.json())
    ])
        .then(([imagesData, counterData]) => {
            console.log('チャンピオンデータ読み込み成功');
            
            // champion_imagesを保存
            championImages = imagesData;
            
            // champion_images.jsonのデータをチャンピオンリストに変換
            filteredChampions = Object.entries(imagesData).map(([japaneseName, englishName]) => {
                // カウンターデータからレーン情報を取得
                const lanes = counterData[japaneseName] || [];
                const laneTags = lanes.map(l => l.lane);
                
                // チャンピオンのロールタグを追加（実装のため固定値）
                const roleTags = getChampionRoleTags(japaneseName);
                
                return {
                    id: englishName,
                    name: japaneseName,
                    title: '',
                    tags: [...roleTags, ...laneTags],
                    stats: {}
                };
            });
            
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

// 検索マッチング関数
function matchesSearch(championName, searchQuery) {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    
    // 入力が半角英数字のみかチェック（ローマ字入力判定）
    const isRomajiInput = /^[a-z0-9]+$/i.test(searchQuery);
    
    if (isRomajiInput) {
        // ローマ字入力の場合は前方一致
        // 1. 英語名での検索（前方一致）- 優先
        const englishName = championImages[championName];
        if (englishName && englishName.toLowerCase().startsWith(query)) return true;
        
        // 2. ローマ字→ひらがな変換して検索（前方一致）
        const inputHiragana = romajiToHiragana(query);
        const championHiragana = katakanaToHiragana(championName);
        if (championHiragana.startsWith(inputHiragana)) return true;
        
        // 3. ローマ字変換での検索（前方一致）- フォールバック
        const romaji = katakanaToRomaji(championName);
        if (romaji.startsWith(query)) return true;
    } else {
        // 日本語入力の場合は部分一致
        // 1. 日本語名での部分一致（カタカナ）
        if (championName.toLowerCase().includes(query)) return true;
        
        // 2. ひらがなでの検索
        const hiragana = katakanaToHiragana(championName);
        if (hiragana.toLowerCase().includes(query)) return true;
        
        // 3. ひらがな入力をカタカナに変換して検索
        const katakana = hiraganaToKatakana(searchQuery);
        if (championName.includes(katakana)) return true;
    }
    
    return false;
}

// チャンピオンのロールタグを取得
function getChampionRoleTags(championName) {
    const roleMapping = {
        // Fighter
        'エイトロックス': ['Fighter'], 'アクシャン': ['Fighter'], 'アリスタ': ['Fighter'], 'アンベッサ': ['Fighter'],
        'カミール': ['Fighter'], 'ダリウス': ['Fighter'], 'ダイアナ': ['Fighter'], 'ドクター・ムンド': ['Fighter'],
        'フィオラ': ['Fighter'], 'ガレン': ['Fighter'], 'グウェン': ['Fighter'], 'ヘカリム': ['Fighter'],
        'イレリア': ['Fighter'], 'ジャックス': ['Fighter'], 'ジェイス': ['Fighter'], 'ケイル': ['Fighter'],
        'ケイン': ['Fighter'], 'ケネン': ['Fighter'], 'リー・シン': ['Fighter'], 'ナサス': ['Fighter'],
        'ノーチラス': ['Fighter'], 'オラフ': ['Fighter'], 'パンテオン': ['Fighter'], 'レネクトン': ['Fighter'],
        'レンガー': ['Fighter'], 'リヴェン': ['Fighter'], 'ランブル': ['Fighter'], 'セト': ['Fighter'],
        'シェン': ['Fighter'], 'シンジド': ['Fighter'], 'サイオン': ['Fighter'], 'シンドラ': ['Fighter'],
        'トリンダメア': ['Fighter'], 'アーゴット': ['Fighter'], 'ヴァイ': ['Fighter'], 'ヴィエゴ': ['Fighter'],
        'ブラッドミア': ['Fighter'], 'ボリベア': ['Fighter'], 'ワーウィック': ['Fighter'], 'ウーコン': ['Fighter'],
        'シン・ジャオ': ['Fighter'], 'ヤスオ': ['Fighter'], 'ヨネ': ['Fighter'], 'ヴェイン': ['Fighter'],
        
        // Tank
        'アリスター': ['Tank'], 'アムム': ['Tank'], 'ブラウム': ['Tank'], 'ガリオ': ['Tank'],
        'マルファイト': ['Tank'], 'マオカイ': ['Tank'], 'ノーチラス': ['Tank'], 'オーン': ['Tank'],
        'ラムス': ['Tank'], 'サイオン': ['Tank'], 'タリック': ['Tank'], 'ヌヌ＆ウィルンプ': ['Tank'],
        
        // Mage
        'エイトロックス': ['Mage'], 'アーリ': ['Mage'], 'アニー': ['Mage'], 'ブランド': ['Mage'],
        'ベイガー': ['Mage'], 'ヴェックス': ['Mage'], 'ビクター': ['Mage'], 'ブラッドミア': ['Mage'],
        'ザイラ': ['Mage'], 'ジグス': ['Mage'], 'ゾーイ': ['Mage'],
        
        // Assassin
        'アカリ': ['Assassin'], 'イブリン': ['Assassin'], 'エコー': ['Assassin'], 'フィズ': ['Assassin'],
        'カサディン': ['Assassin'], 'カタリナ': ['Assassin'], 'カ＝ジックス': ['Assassin'], 'ケイン': ['Assassin'],
        'キンドレッド': ['Assassin'], 'レブ': ['Assassin'], 'ナフイリー': ['Assassin'], 'タロン': ['Assassin'],
        'ゼド': ['Assassin'],
        
        // Marksman
        'エイプヘリオス': ['Marksman'], 'アッシュ': ['Marksman'], 'ケイトリン': ['Marksman'], 'コーキ': ['Marksman'],
        'ドレイヴン': ['Marksman'], 'エズリアル': ['Marksman'], 'ジン': ['Marksman'], 'ジンクス': ['Marksman'],
        'カイ＝サ': ['Marksman'], 'カリスタ': ['Marksman'], 'キンドレッド': ['Marksman'], 'ルシアン': ['Marksman'],
        'ミス・フォーチュン': ['Marksman'], 'ニーラ': ['Marksman'], 'サミーラ': ['Marksman'], 'セナ': ['Marksman'],
        'シヴィア': ['Marksman'], 'トリスターナ': ['Marksman'], 'トゥイッチ': ['Marksman'], 'ヴァルス': ['Marksman'],
        'ヴェイン': ['Marksman'], 'ゼリ': ['Marksman'], 'ザヤ': ['Marksman'],
        
        // Support
        'アリスター': ['Support'], 'ブラウム': ['Support'], 'ブリッツクランク': ['Support'], 'ジャンナ': ['Support'],
        'カルマ': ['Support'], 'レオナ': ['Support'], 'ルル': ['Support'], 'ルックス': ['Support'],
        'ナミ': ['Support'], 'ナウティラス': ['Support'], 'レネター': ['Support'], 'ラカン': ['Support'],
        'ラクサン': ['Support'], 'シェン': ['Support'], 'ソナ': ['Support'], 'ソラカ': ['Support'],
        'スウェイン': ['Support'], 'タリック': ['Support'], 'スレッシュ': ['Support'], 'ツイステッド・フェイト': ['Support'],
        'ユーミ': ['Support'], 'ザヤ': ['Support'], 'セラフィーン': ['Support'], 'ミリオ': ['Support'],
        'セナ': ['Support'], 'パイク': ['Support'],
    };
    
    return roleMapping[championName] || [];
}

// イベントリスナー設定
function setupEventListeners() {
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchTerm = e.target.value;
            filterAndRenderChampions();
        });
    }
    
    if (laneSelect) {
        laneSelect.addEventListener('change', (e) => {
            currentLane = e.target.value;
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
            return matchesSearch(champion.name, currentSearchTerm);
        });
    }

    // レーンフィルタリング
    if (currentLane !== 'all') {
        filtered = filtered.filter(champion => {
            return champion.tags && champion.tags.includes(currentLane);
        });
    }

    // ロールフィルタリング
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

    // スキル情報を取得
    fetchChampionSkills(champion.id).then(skills => {
        displayChampionModal(champion, skills);
    });
}

// チャンピオンのスキル情報を取得（簡易版）
async function fetchChampionSkills(championId) {
    try {
        // DDragon APIから詳細情報を取得
        const apiUrl = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/data/ja_JP/champion/${championId}.json`;
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            return [];
        }
        
        const data = await response.json();
        const championData = data.data[championId];
        
        if (championData && championData.spells) {
            return championData.spells.map((spell, index) => ({
                id: spell.id,
                name: spell.name,
                description: spell.description,
                image: `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/spell/${spell.id}.png`
            }));
        }
        
        return [];
    } catch (error) {
        console.error('スキル情報の取得に失敗:', error);
        return [];
    }
}

// モーダルを表示
function displayChampionModal(champion, skills) {
    // モーダルヘッダーを更新
    const modalHeader = document.getElementById('modalHeader');
    modalHeader.innerHTML = `
        <img src="${getChampionIconUrl(champion.id)}" alt="${champion.name}" class="modal-champion-icon">
        <div class="modal-champion-info">
            <h2>${champion.name}</h2>
            ${champion.title ? `<p class="modal-champion-title">${champion.title}</p>` : ''}
        </div>
    `;
    
    // モーダルボディを更新
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        ${champion.tags && champion.tags.length > 0 ? `
        <div class="modal-section">
            <h4>メインロール</h4>
            <div class="modal-tags">
                ${champion.tags.map(tag => `<span class="modal-tag">${tag}</span>`).join('')}
            </div>
        </div>
        ` : ''}
        
        <div class="modal-section">
            <h4>説明</h4>
            <p>${champion.blurb || '説明は現在利用できません。'}</p>
        </div>
        
        ${skills && skills.length > 0 ? `
        <div class="modal-section">
            <h4>スキル</h4>
            <div class="skills-container">
                ${skills.map((skill, index) => `
                    <div class="skill-item">
                        <div class="skill-icon-container">
                            <img src="${skill.image}" alt="${skill.name}" class="skill-icon" onerror="this.style.display='none'">
                            <span class="skill-number">${index + 1}</span>
                        </div>
                        <div class="skill-info">
                            <h5 class="skill-name">${skill.name}</h5>
                            <p class="skill-description">${skill.description}</p>
                        </div>
                        <a href="https://www.leagueoflegends.com/ja-jp/champions/${champion.id.toLowerCase()}/" target="_blank" rel="noopener noreferrer" class="skill-video-link">
                            📹 動画を見る
                        </a>
                    </div>
                `).join('')}
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
    currentLane = 'all';
    
    searchInput.value = '';
    laneSelect.value = 'all';
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

