// ==UserScript==
// @name         全局解除网页无法选中、复制文本，与右键限制
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  针对所有网站，解除禁止选中、复制、右键菜单等限制
// @author       yui酱
// @match        *://*/*
// @grant        none
// @license      MIT
// ==/UserScript==
 
(function() {
    'use strict';
 
    // 1. 覆盖全局 CSS，恢复选中、复制功能
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
 
    // 2. 解绑可能阻止复制、选中、右键菜单的事件
    const blockEvents = ['copy', 'cut', 'selectstart', 'mousedown'];
    blockEvents.forEach(evt => {
        document.addEventListener(evt, e => e.stopPropagation(), true);
        document[`on${evt}`] = null;
    });
 
    // 3. 恢复右键菜单：彻底放行 contextmenu 事件并移除内联禁用
    document.addEventListener('contextmenu', e => e.stopPropagation(), true);  // 捕获阶段放行 :contentReference[oaicite:0]{index=0}
    document.body.oncontextmenu = null;                                       // 清除可能的 inline handler
    document.documentElement.oncontextmenu = null;
    // 移除所有元素的 oncontextmenu 属性，防止内联脚本阻止右键
    document.querySelectorAll('*').forEach(el => {
        if (el.hasAttribute('oncontextmenu')) {
            el.removeAttribute('oncontextmenu');
        }
    });
 
    // 4. 定期清理可能的遮罩层，恢复页面可交互性
    function removeOverlays() {
        document.querySelectorAll('body *').forEach(el => {
            const st = window.getComputedStyle(el);
            if ((st.position === 'fixed' || st.position === 'absolute')
                && st.zIndex !== 'auto'
                && st.pointerEvents === 'none'
                && (st.backgroundColor === 'rgba(0, 0, 0, 0)' || parseFloat(st.opacity) < 0.1)) {
                el.remove();
            }
        });
    }
    window.addEventListener('load', removeOverlays, true);
    window.addEventListener('scroll', removeOverlays, true);
})();
