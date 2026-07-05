# AlphaInvestPro 演示视频录制脚本

使用 Playwright 自动打开应用并录制一段完整的中文视频演示。配套简短演示文档见 [`DEMO_DOC.md`](DEMO_DOC.md)，内容按章节覆盖：

1. 项目简介
2. 使用场景说明
3. 核心功能演示
4. AI 能力展示
5. 输入、处理过程和输出结果
6. 项目亮点说明

## 运行前提

- 后端已启动：`http://localhost:8000`
- 前端已启动：`http://localhost:3000`

## 使用方法

```bash
cd demo
npm install
npx playwright install chromium
npm run record
```

## 输出

视频保存在 `demo/output/alphainvestpro_demo_zh.webm`，可直接下载或分享。

如需 mp4 格式：

```bash
ffmpeg -i output/alphainvestpro_demo_zh.webm output/alphainvestpro_demo_zh.mp4
```

## 可选环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_URL` | `http://localhost:3000` | 前端地址 |
| `DEMO_TICKER` | `NVDA` | 演示用股票代码 |
