# AlphaInvestPro 演示视频录制脚本

使用 Playwright 自动打开应用并录制一段完整的中文视频演示，并可基于同一脚本内容生成可下载的 Markdown 简短文档。内容按章节覆盖：

1. 项目简介
2. 使用场景说明
3. 核心功能演示
4. AI 能力展示
5. 输入、处理过程和输出结果
6. 项目亮点说明

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `demo_content.mjs` | 演示内容单一数据源（视频字幕 + 文档正文） |
| `record_demo.mjs` | 录制演示视频（读取 `demo_content.mjs`） |
| `generate_doc.mjs` | 基于脚本内容生成可下载的简短 Markdown 文档 |
| `DEMO_DOC.md` | 自动生成的文档（仓库内同步副本） |

## 运行前提（录制视频）

- 后端已启动：`http://localhost:8000`
- 前端已启动：`http://localhost:3000`

## 使用方法

```bash
cd demo
npm install
npx playwright install chromium

# 录制演示视频
npm run record

# 基于脚本内容生成可下载的简短 Markdown 文档（无需启动应用）
npm run generate-doc
```

## 输出

- 视频：`demo/output/alphainvestpro_demo_zh.webm`，可直接下载或分享。
- 文档：`demo/output/alphainvestpro_demo_doc_zh.md`（可下载副本）与 `demo/DEMO_DOC.md`（仓库副本）。

如需 mp4 格式：

```bash
ffmpeg -i output/alphainvestpro_demo_zh.webm output/alphainvestpro_demo_zh.mp4
```

## 可选环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_URL` | `http://localhost:3000` | 前端地址 |
| `DEMO_TICKER` | `NVDA` | 演示用股票代码 |
