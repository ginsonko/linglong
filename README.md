# 玲珑工坊官网

玲珑工坊（万能创作终端 0.6.0 商业版）的官方网站。纯静态页面，不依赖任何被墙的外部资源，可放在任意静态托管上。

## 目录

- `site/` — 网站本体（直接把整个目录上传即完成部署）
  - `index.html` — 首页
  - `stories/cheng.html` — 用户成功故事详情模板（程总篇，内容待主人提供）
  - `assets/css/site.css` — 全部样式
  - `assets/js/config.js` — **上线前只需要改这一个文件**（链接、下载地址、价格页等）
  - `assets/js/site.js` — 交互脚本
  - `assets/fonts/` — 自托管、已按页面文字子集化的字体
  - `assets/img/` — 图片（WebP + AVIF）
- `scripts/` — 构建脚本（本地用，不需要上传）
  - `make-art.py` — 从概念图抠立绘、导出 WebP/AVIF
  - `make-icons.py` — 生成 favicon / 图标 / 分享图
  - `make-fonts.py` — 按页面实际用到的文字做字体子集
  - `check-words.py` — 禁用词与广告法用词检查
  - `shots.js` — 桌面 / 手机整页截图（用本机 Edge）
- `DEPLOY.md` — 部署说明

## 本地预览

```
py -3 -m http.server 5408 --directory site
```

打开 http://localhost:5408 。

## 改文案后

```
py -3 scripts/make-fonts.py    # 重新子集化字体
py -3 scripts/check-words.py   # 过一遍用词检查
```
