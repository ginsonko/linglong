/* 整页截图：桌面 1440 + 手机 390，用本机 Edge（playwright-core 从 heart-joint6 引用）。
   用法：set NODE_PATH=C:\Users\Administrator\Documents\Codex\omni-wt\heart-joint6\node_modules
         node scripts\shots.js [url]
*/
const path = require('path');
const { chromium } = require('playwright-core');

const BASE = process.argv[2] || 'http://127.0.0.1:5408';
const OUT = process.argv[3] || 'I:\\omni-tmp\\v060\\site\\shots';
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

(async () => {
  const fs = require('fs');
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });
  try {
    // 桌面 1440
    let page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });
    await page.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
    await page.evaluate(() => new Promise(r => {
      // 触发所有懒加载与 reveal，再滚回顶部
      let y = 0;
      const step = () => {
        y += 700;
        window.scrollTo(0, y);
        if (y < document.body.scrollHeight) setTimeout(step, 60);
        else setTimeout(() => { window.scrollTo(0, 0); setTimeout(r, 400); }, 500);
      };
      step();
    }));
    // fullPage 截图里 fixed 顶栏会在视口位置重复出现，改成 absolute 只在顶部出现一次；
    // 快速滚动时 IO 回调可能还没来得及触发，强制所有 reveal 到位，保证截图所见即最终状态
    await page.addStyleTag({ content: '.topbar{position:absolute !important} html{scroll-behavior:auto !important}' });
    await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'home-1440-full.png'), fullPage: true });
    console.log('home-1440-full.png');
    await page.close();

    // 手机 390
    page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await page.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
    await page.evaluate(() => new Promise(r => {
      let y = 0;
      const step = () => {
        y += 500;
        window.scrollTo(0, y);
        if (y < document.body.scrollHeight) setTimeout(step, 60);
        else setTimeout(() => { window.scrollTo(0, 0); setTimeout(r, 400); }, 500);
      };
      step();
    }));
    await page.addStyleTag({ content: '.topbar{position:absolute !important} html{scroll-behavior:auto !important}' });
    await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'home-390-full.png'), fullPage: true });
    console.log('home-390-full.png');
    await page.close();

    // 故事模板页（桌面）
    page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
    await page.goto(BASE + '/stories/cheng.html', { waitUntil: 'networkidle' });
    await page.screenshot({ path: path.join(OUT, 'story-cheng-1440-full.png'), fullPage: true });
    console.log('story-cheng-1440-full.png');
    await page.close();
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
