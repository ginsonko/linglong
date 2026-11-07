/*
 * 玲珑工坊官网配置。上线前只需要改这一个文件。
 * 留空的链接，页面会显示「即将开放」，不会出现坏链接。
 */
window.LL_CONFIG = {
  product: {
    name: '玲珑工坊',
    english: 'LINGLONG STUDIO',
    version: '0.6.2',
    channel: ''
  },
  links: {
    register: 'https://yinziapi.top/sign-up',
    login: 'https://yinziapi.top/sign-in',
    pricing: 'https://yinziapi.top/pricing',
    recharge: 'https://yinziapi.top/wallet',
    support: '',    // 客服 / 联系方式页
    free_edition: 'https://github.com/ginsonko/omnicreator/releases'
  },
  downloads: {
    win_setup: { label: 'Windows 安装版', note: 'Windows 10 / 11，64 位（推荐）', file: 'LinglongStudio-0.6.2-Setup.exe', size: '300 MB',
      url: 'https://workflow.yinziapi.top/download/LinglongStudio-0.6.2-Setup.exe',
      alt_url: 'https://github.com/ginsonko/linglong/releases/download/v0.6.2/LinglongStudio-0.6.2-Setup.exe', alt_label: '备用下载（GitHub）',
      sha256: '71c725af56154a7e0bfcbf493660d0ffb42457f6c89d4eb84e815c259ab94375' },
    win_portable: { label: 'Windows 免安装版', note: 'Windows 10 / 11，64 位，双击就能用', file: 'LinglongStudio-0.6.2-Portable.exe', size: '176 MB',
      url: 'https://workflow.yinziapi.top/download/LinglongStudio-0.6.2-Portable.exe',
      alt_url: 'https://github.com/ginsonko/linglong/releases/download/v0.6.2/LinglongStudio-0.6.2-Portable.exe', alt_label: '备用下载（GitHub）',
      sha256: 'ba52c14fbeb1e7b0d624cccd8463b2c4a0fe87315a1e4523b559ff6f149e2472' },
    mac_arm64: { label: 'macOS · Apple 芯片', note: 'M1 及以后的 Mac，macOS 13 及以上', file: '', url: '', size: '', sha256: '' },
    mac_x64: { label: 'macOS · Intel', note: 'Intel 处理器的 Mac，macOS 13 及以上', file: '', url: '', size: '', sha256: '' }
  },
  // 首页作品短片：mp4 / webm 直链。留空时只显示封面和「即将上线」。
  film: {
    url: '',
    url_mobile: '',
    title: '作品短片'
  },
  community: {
    qq_group: '',
    contact: ''
  }
};
