// ==UserScript==
// @name         全局解除选中、复制与右键限制
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  解除所有站点的选中/复制/右键限制
// @author       yui酱
// @match        *://*/*
// @grant        none
// @license      MIT
// ==/UserScript==
 
(function() {
    'use strict';
 
    // 1. 覆盖全局 CSS，恢复文本选中与复制
    const style = document.createElement('style');
    style.textContent = `
        * {
            -webkit-user-select: auto !important;
            -moz-user-select: auto !important;
            -ms-user-select: auto !important;
            user-select: auto !important;
        }
    `;
    document.head.appendChild(style);
 
    // 2. 解绑可能阻止复制、选中、右键的事件
    const blockEvents = ['copy', 'cut', 'selectstart', 'mousedown'];
    blockEvents.forEach(evt => {
        document.addEventListener(evt, e => e.stopPropagation(), true);
        document[`on${evt}`] = null;
    });
 
    // 3. 恢复右键菜单
    document.addEventListener('contextmenu', e => e.stopPropagation(), true); // 放行 contextmenu 事件 :contentReference[oaicite:0]{index=0}
    document.body.oncontextmenu = null;
    document.documentElement.oncontextmenu = null;
    document.querySelectorAll('*').forEach(el => {
        if (el.hasAttribute('oncontextmenu')) {
            el.removeAttribute('oncontextmenu');
        }
    });
 
    // 4. 定义遮罩层清理函数（排除 Bilibili）
    function removeOverlays() {
        // 如果是 Bilibili 视频站点，直接跳过清理，保留弹幕层
        if (/\.bilibili\.com$/.test(location.hostname)) {
            return;
        }
        document.querySelectorAll('body *').forEach(el => {
            const st = window.getComputedStyle(el);
            if ((st.position === 'fixed' || st.position === 'absolute')
                && st.zIndex !== 'auto'
                && st.pointerEvents === 'none'    // 仅移除 pointer-events:none 的遮罩 :contentReference[oaicite:1]{index=1}
                && (st.backgroundColor === 'rgba(0, 0, 0, 0)' || parseFloat(st.opacity) < 0.1)) {
                el.remove();
            }
        });
    }
 
    // 5. 在页面加载与滚动时触发清理
    window.addEventListener('load', removeOverlays, true);
    window.addEventListener('scroll', removeOverlays, true);
})();
