/ ==UserScript==
// @name         全局解除选中、复制与右键限制
// @namespace    http://tampermonkey.net/
// @version      1.3
// @description  按域名精细控制：开启或排除解除选中、复制、右键限制及遮罩层清理功能（这下一版发布完成之后应该就不会更新了，在思考怎么做一个大家一起添加域名的方法，这个功能做出来之后应该就真的不会再更新了）
// @author       yui酱
// @match        *://*/*
// @grant        none
// @license      MIT
// ==/UserScript==
 
(function() {
    'use strict';
 
    // —— 1. 配置区 ——
    // 定义各功能的目标网站列表
    //如果正则表达式不会写的话，可以让AI帮你写，把你需要排除的网址给AI
    //提示词：写个用于油猴匹配这个网址的正则：（这里放网址）
    const unlockSelectCopySites = [
        /\.bilibili\.com$/,
        /(^|\.)example\.com$/
        // 在此添加需要解除选中/复制限制的网站的正则表达式
    ];
 
    const unlockContextSites = [
        /(^|\.)example\.com$/,
        /(^|\.)another-example\.com$/,
        /\.nicovideo\.com$/
        // 在此添加需要解除右键限制的网站的正则表达式
    ];
 
    const unlockOverlaySites = [
        /(^|\.)example\.com$/,
        /(^|\.)another-example\.com$/
        // 在此添加需要清理遮罩层的网站的正则表达式
    ];
 
    // 默认规则：对所有其它站点都完全解除
    const defaultRule = {
        unlockSelectCopy: true,
        unlockContext: true,
        unlockOverlay: true
    };
 
    // 获取当前域名
    const hostname = location.hostname;
 
    // 判断当前网站是否匹配某个规则
    function isMatch(rules) {
        return rules.some(rule => rule.test(hostname));
    }
 
    // 构建当前网站的规则
    const rule = {
        unlockSelectCopy: isMatch(unlockSelectCopySites),
        unlockContext: isMatch(unlockContextSites),
        unlockOverlay: isMatch(unlockOverlaySites)
    };
 
    // 如果当前网站不在任何规则中，使用默认规则
    if (!rule.unlockSelectCopy && !rule.unlockContext && !rule.unlockOverlay) {
        Object.assign(rule, defaultRule);
    }
 
    // —— 2. 根据规则执行解除“选中与复制” ——
    if (rule.unlockSelectCopy) {
        // 覆盖 CSS 强制恢复文本选中
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
 
        // 解绑阻止复制/剪切的事件
        ['copy', 'cut', 'selectstart', 'mousedown'].forEach(evt => {
            document.addEventListener(evt, e => e.stopPropagation(), true);
            document[`on${evt}`] = null;
        });
    }
 
    // —— 3. 根据规则执行恢复右键 ——
    if (rule.unlockContext) {
        document.addEventListener('contextmenu', e => e.stopPropagation(), true);
        document.body.oncontextmenu = null;
        document.documentElement.oncontextmenu = null;
        document.querySelectorAll('*').forEach(el => {
            if (el.hasAttribute('oncontextmenu')) el.removeAttribute('oncontextmenu');
        });
    }
 
    // —— 4. 遮罩层清理 ——
    function removeOverlays() {
        if (!rule.unlockOverlay) return;
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
