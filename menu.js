/**
 * サイドメニューの制御
 */

document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const closeBtn = document.getElementById('closeBtn');

    // メニューを開く
    function openMenu() {
        sidebar.classList.add('open');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden'; // スクロールを無効化
    }

    // メニューを閉じる
    function closeMenu() {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
        document.body.style.overflow = ''; // スクロールを有効化
    }

    // イベントリスナー
    if (menuToggle) {
        menuToggle.addEventListener('click', openMenu);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
    }

    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }

    // ESCキーでメニューを閉じる
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });
});

