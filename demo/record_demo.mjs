/**
 * AlphaInvestPro 全流程视频演示录制脚本（Playwright）
 *
 * 功能：自动打开应用，按章节逐步演示完整使用流程，并录制为可下载的视频文件。
 * 章节字幕与简短文档共用同一数据源（demo_content.mjs），
 * 运行 `npm run generate-doc` 可基于脚本内容生成可下载的 Markdown 简短文档。
 *
 * 演示章节：
 *   1. 项目简介
 *   2. 使用场景说明
 *   3. 核心功能演示
 *   4. AI 能力展示
 *   5. 输入、处理过程和输出结果
 *   6. 项目亮点说明
 *
 * 运行前提：
 *   - 后端已启动：http://localhost:8000
 *   - 前端已启动：http://localhost:3000
 *
 * 使用方法：
 *   cd demo
 *   npm install
 *   npx playwright install chromium
 *   npm run record
 *
 * 输出：demo/output/alphainvestpro_demo_zh.webm（可直接下载/分享，
 *       如需 mp4 可用 ffmpeg 转换：ffmpeg -i xxx.webm xxx.mp4）
 */

import { mkdirSync } from "node:fs";
import { chromium } from "playwright";

import { CHAPTERS, ENDING_CAPTION, REPORT_SECTION_CAPTIONS } from "./demo_content.mjs";

const APP_URL = process.env.APP_URL ?? "http://localhost:3000";
const OUTPUT_DIR = "output";
const OUTPUT_FILE = `${OUTPUT_DIR}/alphainvestpro_demo_zh.webm`;
const DEMO_TICKER = process.env.DEMO_TICKER ?? "NVDA";

/** 按章节号取字幕内容 */
const chapter = (num) => CHAPTERS.find((c) => c.num === num).caption;

/** 等待指定毫秒，控制演示节奏 */
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * 在页面底部注入中文字幕横幅（不拦截鼠标事件），
 * 让视频观看者清楚了解当前演示的章节与内容。
 */
async function showCaption(page, title, text, holdMs = 4500) {
  await page.evaluate(
    ({ title, text }) => {
      document.getElementById("demo-caption")?.remove();
      const el = document.createElement("div");
      el.id = "demo-caption";
      el.style.cssText = [
        "position:fixed", "left:50%", "bottom:24px", "transform:translateX(-50%)",
        "max-width:920px", "width:calc(100% - 48px)", "z-index:99999",
        "background:rgba(15,23,42,0.92)", "color:#fff", "border-radius:14px",
        "padding:14px 22px", "box-shadow:0 8px 30px rgba(0,0,0,0.35)",
        "font-family:'PingFang SC','Microsoft YaHei',sans-serif",
        "pointer-events:none", "backdrop-filter:blur(4px)",
      ].join(";");
      el.innerHTML =
        `<div style="font-size:17px;font-weight:700;color:#93c5fd;margin-bottom:4px">${title}</div>` +
        `<div style="font-size:14px;line-height:1.6;color:#e2e8f0">${text}</div>`;
      document.body.appendChild(el);
    },
    { title, text },
  );
  await wait(holdMs);
}

/** 移除字幕横幅 */
async function hideCaption(page) {
  await page.evaluate(() => document.getElementById("demo-caption")?.remove());
}

/** 平滑滚动到指定文本所在区域 */
async function scrollToText(page, text, holdMs = 3200) {
  const target = page.getByText(text, { exact: false }).first();
  await target.scrollIntoViewIfNeeded();
  await page.mouse.wheel(0, -120); // 略微上移，避免内容贴边
  await wait(holdMs);
}

async function main() {
  mkdirSync(OUTPUT_DIR, { recursive: true });

  console.log("【录制开始】启动浏览器并开启视频录制…");
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: OUTPUT_DIR, size: { width: 1280, height: 720 } },
    locale: "zh-CN",
  });
  const page = await context.newPage();

  // ---------- 准备：打开应用并切换到简体中文界面 ----------
  console.log("【准备】打开应用首页，切换到简体中文界面…");
  await page.goto(`${APP_URL}/dashboard`, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "简体中文" }).click();
  await page.getByRole("link", { name: "仪表盘" }).waitFor();
  await wait(1200);

  // ---------- 第 1 章：项目简介 ----------
  console.log("【第 1 章】项目简介…");
  await showCaption(page, chapter(1).title, chapter(1).text, 6000);

  // ---------- 第 2 章：使用场景说明 ----------
  console.log("【第 2 章】使用场景说明…");
  await showCaption(page, chapter(2).title, chapter(2).text, 6000);
  await hideCaption(page);

  // ---------- 第 3 章：核心功能演示 ----------
  console.log("【第 3 章】核心功能演示：新建分析任务…");
  await page.getByRole("link", { name: "新建分析" }).click();
  await page.locator("#ticker").waitFor();
  await showCaption(page, chapter(3).form.title, chapter(3).form.text, 5000);

  // 逐字输入股票代码，模拟真实操作
  await page.locator("#ticker").click();
  await page.locator("#ticker").pressSequentially(DEMO_TICKER, { delay: 180 });
  await wait(800);
  await page.getByRole("button", { name: /完整备忘录/ }).first().click();
  await wait(800);
  await page.locator("#report-language").selectOption("zh-CN");
  await wait(1000);

  console.log("【第 3 章】启动分析，观察可视化 Agent 时间线…");
  await page.getByRole("button", { name: "开始分析" }).click();
  await page.getByText("Agent 时间线").waitFor({ timeout: 20000 });
  await showCaption(page, chapter(3).timeline.title, chapter(3).timeline.text, 5500);

  // ---------- 第 4 章：AI 能力展示 ----------
  console.log("【第 4 章】AI 能力展示…");
  await showCaption(page, chapter(4).title, chapter(4).text, 6000);

  // 等待分析完成，报告自动呈现
  console.log("【第 4 章】等待分析完成，生成结构化报告…");
  await page.getByText("证据与数据来源").first().waitFor({ timeout: 90000 });
  await wait(1000);

  // ---------- 第 5 章：输入、处理过程和输出结果 ----------
  console.log("【第 5 章】展示输出结果：逐节浏览结构化报告…");
  await showCaption(
    page,
    chapter(5).title,
    chapter(5).text.replace("{ticker}", DEMO_TICKER),
    5500,
  );

  for (const section of REPORT_SECTION_CAPTIONS) {
    await scrollToText(page, section.anchor);
    await showCaption(page, section.title, section.text, section.holdMs);
  }
  await hideCaption(page);

  // ---------- 第 6 章：项目亮点说明 ----------
  console.log("【第 6 章】项目亮点：观察列表 + 报告历史 + 双语切换…");
  await page.getByText("最终结论").first().scrollIntoViewIfNeeded();
  await wait(600);
  await page.getByRole("button", { name: "加入观察列表" }).click();
  await wait(1200);

  await page.getByRole("link", { name: "观察列表" }).click();
  await page.getByText(DEMO_TICKER).first().waitFor();
  await showCaption(page, chapter(6).watchlist.title, chapter(6).watchlist.text, 4000);

  await page.getByRole("link", { name: "报告" }).click();
  await page.getByText("报告", { exact: false }).first().waitFor();
  await showCaption(page, chapter(6).reports.title, chapter(6).reports.text, 4000);

  // 双语切换演示：中文 → English → 中文
  await showCaption(page, chapter(6).bilingual.title, chapter(6).bilingual.text, 4200);
  await page.getByRole("button", { name: "English" }).click();
  await wait(2500);
  await page.getByRole("button", { name: "简体中文" }).click();
  await wait(1500);

  await showCaption(page, ENDING_CAPTION.title, ENDING_CAPTION.text, 6000);

  // ---------- 收尾：保存视频 ----------
  console.log("【收尾】关闭浏览器并保存视频…");
  const video = page.video();
  await context.close();
  if (video) {
    await video.saveAs(OUTPUT_FILE);
    await video.delete(); // 清理 Playwright 生成的随机文件名副本
    console.log(`【完成】演示视频已保存：demo/${OUTPUT_FILE}`);
  }
  await browser.close();
}

main().catch((err) => {
  console.error("【录制失败】", err);
  process.exit(1);
});
