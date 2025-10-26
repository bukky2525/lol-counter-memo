/**
 * メインアプリケーションロジック
 */

// グローバル変数
let counterData = {};
let championImages = {};
const DDragonVersion = '14.24.1';
let currentLane = 'all';
let searchTerm = '';

// DOM要素
const searchBox = document.getElementById('searchBox');
const laneButtons = document.querySelectorAll('.lane-btn');
const championsContainer = document.getElementById('championsContainer');

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    setupEventListeners();
});

// データ読み込み
function loadData() {
    Promise.all([
        fetch('counter_data.json')
            .then(response => {
                console.log('counter_data.json response status:', response.status);
                if (!response.ok) {
                    throw new Error(`counter_data.json: HTTP ${response.status}`);
                }
                return response.json();
            }),
        fetch('champion_images.json')
            .then(response => {
                console.log('champion_images.json response status:', response.status);
                if (!response.ok) {
                    throw new Error(`champion_images.json: HTTP ${response.status}`);
                }
                return response.json();
            })
    ])
        .then(([counterDataJson, championImagesJson]) => {
            console.log('データ読み込み成功');
            console.log('チャンピオン数:', Object.keys(counterDataJson).length);
            counterData = counterDataJson;
            championImages = championImagesJson;
            renderChampions();
        })
        .catch(error => {
            console.error('データの読み込みに失敗しました:', error);
            championsContainer.innerHTML = `
                <div class="no-results">
                    <h3>データの読み込みに失敗しました</h3>
                    <p>エラー: ${error.message}</p>
                    <p>ブラウザのコンソール（F12）でエラー詳細を確認してください。</p>
                </div>
            `;
        });
}

// イベントリスナー設定
function setupEventListeners() {
    // レーンフィルターボタン
    laneButtons.forEach(button => {
        button.addEventListener('click', () => {
            laneButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            currentLane = button.getAttribute('data-lane');
            renderChampions();
        });
    });

    // 検索ボックス
    searchBox.addEventListener('input', (e) => {
        searchTerm = e.target.value.toLowerCase();
        renderChampions();
    });
}

// チャンピオンアイコンURLを取得
function getChampionIconUrl(championName) {
    const englishName = championImages[championName] || championName;
    return `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/champion/${englishName}.png`;
}

// OP.GG URLを生成
function getOpggUrl(championName, lane) {
    const englishName = championImages[championName] || championName;
    // チャンピオン名を小文字に変換し、特殊文字を処理
    const formattedName = englishName.toLowerCase()
        .replace(/'/g, '')  // アポストロフィを削除
        .replace(/\s+/g, ''); // スペースを削除
    
    return `https://www.op.gg/champions/${formattedName}/${lane}/build`;
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

// チャンピオンデータを描画
function renderChampions() {
    championsContainer.innerHTML = '';
    let visibleCount = 0;

    const laneNames = {
        'top': 'トップ',
        'jungle': 'ジャングル',
        'mid': 'ミッド',
        'adc': 'ボット',
        'support': 'サポート'
    };

    Object.keys(counterData).sort().forEach(champion => {
        counterData[champion].forEach(data => {
            // レーンフィルタリング
            if (currentLane !== 'all' && data.lane !== currentLane) {
                return;
            }

            // 検索フィルタリング（メインチャンピオンのみ）
            if (searchTerm) {
                const championMatch = matchesSearch(champion, searchTerm);
                if (!championMatch) {
                    return;
                }
            }

            const championItem = document.createElement('div');
            championItem.className = 'champion-item';
            
            // カウンターリストを画像付きで生成
            const countersHtml = data.counters.map(counter => 
                `<span class="counter-item">
                    <img src="${getChampionIconUrl(counter)}" 
                         alt="${counter}" 
                         class="counter-icon"
                         onerror="this.style.display='none'">
                    ${counter}
                </span>`
            ).join('');
            
            championItem.innerHTML = `
                <div class="champion-header">
                    <img src="${getChampionIconUrl(champion)}" 
                         alt="${champion}" 
                         class="champion-icon champion-icon-clickable"
                         data-champion="${champion}"
                         data-lane="${data.lane}"
                         onerror="this.style.display='none'">
                    <div class="champion-title">
                        <h3>${champion}（${laneNames[data.lane]}）</h3>
                    </div>
                </div>
                <ul>
                    <li><b>カウンター:</b><br>${countersHtml}</li>
                </ul>
            `;
            
            // チャンピオンアイコンにクリックイベントを追加
            championsContainer.appendChild(championItem);
            const championIcon = championItem.querySelector('.champion-icon-clickable');
            if (championIcon) {
                championIcon.addEventListener('click', function() {
                    const championName = this.getAttribute('data-champion');
                    const lane = this.getAttribute('data-lane');
                    const opggUrl = getOpggUrl(championName, lane);
                    window.open(opggUrl, '_blank');
                });
            }
            
            visibleCount++;
        });
    });

    // 結果が見つからない場合のメッセージ
    if (visibleCount === 0) {
        championsContainer.innerHTML = `
            <div class="no-results">
                <h3>検索結果が見つかりません</h3>
                <p>"${searchTerm}" に一致するチャンピオンが見つかりませんでした。</p>
                <p>別のキーワードで検索するか、レーンフィルターを変更してみてください。</p>
            </div>
        `;
    }
}

