# 玲珑工坊官网 · 部署说明

本站是**纯静态页面**：没有后端、没有构建步骤、没有第三方统计或追踪脚本，所有字体和图片全部自托管。把 `site/` 目录里的内容原样上传到任何静态托管（Nginx、OSS + CDN、宝塔、GitHub Pages 均可）就完成部署。

## 一、上传什么

只上传 `site/` 目录的内容（保持目录结构）：

```
site/
├── index.html              # 首页
├── stories/cheng.html      # 成功故事详情模板（程总篇，内容待补）
└── assets/
    ├── css/site.css
    ├── js/config.js        # ★ 上线前改这一个文件
    ├── js/site.js
    ├── fonts/*.woff2       # 已按页面文字子集化
    └── img/*               # WebP / PNG / JPG
```

`scripts/`、`.gitignore`、`README.md`、本文件是开发用的，**不要上传**。

## 二、上线前改配置（必须）

打开 `site/assets/js/config.js`，填上真实地址：

| 字段 | 说明 |
|---|---|
| `links.register` / `links.login` | 注册页、登录页地址 |
| `links.pricing` | 实时价格页 |
| `links.support` | 客服 / 联系方式页 |
| `links.free_edition` | 免费版（万能创作终端）发布页，已预填 GitHub |
| `downloads.*.url` / `file` / `size` / `sha256` | 三个安装包的直链与校验值 |
| `film.url` / `film.url_mobile` | 首页作品短片 mp4 直链 |

**留空的字段页面会自动显示「即将开放」**，不会出现坏链接。可以先上线、后补链接。

## 三、服务器建议设置（非必须，有则更快）

1. **开启 gzip / brotli**：对 `html css js` 启用即可（woff2、webp、jpg 已经是压缩格式，不用再加）。
2. **缓存头**：
   - `assets/fonts/`、`assets/img/`：长缓存，如 `Cache-Control: public, max-age=2592000`（30 天）。改图后请改文件名或加版本号。
   - `index.html`、`stories/*.html`、`config.js`：短缓存或不缓存，如 `Cache-Control: no-cache`，方便改文案和配置立即生效。
3. **正确的 Content-Type**：`.woff2` 应为 `font/woff2`；`.webp` 应为 `image/webp`。主流服务器默认已带。
4. **HTTPS**：页面里没用任何 http 资源，直接全站 HTTPS 即可。

Nginx 参考片段：

```nginx
location /assets/fonts/ { expires 30d; add_header Cache-Control "public"; }
location /assets/img/   { expires 30d; add_header Cache-Control "public"; }
location ~* \.(html|js)$ { add_header Cache-Control "no-cache"; }
gzip on;
gzip_types text/css application/javascript text/html;
```

## 四、改文案 / 换图之后

在开发仓库里操作，再重新上传：

```
py -3 scripts/make-fonts.py     # 文案有改动：重新子集化字体
py -3 scripts/check-words.py    # 过一遍禁用词与广告法用词
py -3 scripts/make-art.py       # 立绘有新版：重新抠图出 WebP
py -3 scripts/make-icons.py     # 需要重做图标 / 分享图时
node scripts/shots.js           # 重新出整页截图（需先起本地预览）
```

本地预览：`py -3 -m http.server 5408 --directory site`，打开 http://localhost:5408 。

## 五、验收清单

- [ ] 首页与故事页在手机、电脑上各打开一遍，逐屏过目
- [ ] `py -3 scripts/check-words.py` 无输出告警
- [ ] Lighthouse 移动端性能 ≥ 90
- [ ] `config.js` 里的链接全部确认（留空的确认就是要显示「即将开放」）
- [ ] 成功故事页的数字和原话已经本人确认、授权留底（见 stories/cheng.html 末尾的材料清单）
