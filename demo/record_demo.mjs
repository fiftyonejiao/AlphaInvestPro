/**
 * AlphaInvestPro 全流程视频演示录制脚本（Playwright）
 *
 * 功能：自动打开应用，按章节逐步演示完整使用流程，并录制为可下载的视频文件。
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

const APP_URL = process.env.APP_URL ?? "http://localhost:3000";
const OUTPUT_DIR = "output";
const OUTPUT_FILE = `${OUTPUT_DIR}/alphainvestpro_demo_zh.webm`;
const DEMO_TICKER = process.env.DEMO_TICKER ?? "NVDA";

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
  await showCaption(
    page,
    "① 项目简介 — AlphaInvestPro",
    "AlphaInvestPro 是一款仅供研究使用的 AI 智能投资分析工作台：输入股票代码，即可获得结构化的投资备忘录，" +
      "涵盖商业质量、护城河、估值、风险与最终结论。所有数字来自确定性计算，AI 只负责叙述，绝不编造数据。",
    6000,
  );

  // ---------- 第 2 章：使用场景说明 ----------
  console.log("【第 2 章】使用场景说明…");
  await showCaption(
    page,
    "② 使用场景说明",
    "适合希望进行有纪律股票研究的个人投资者、需要结构化分析框架的初学者、想快速产出研究原型的产品经理与创业者，" +
      "以及探索 AI 辅助投资研究的开发者。仪表盘实时展示报告数量、观察列表、数据与大模型运行模式。",
    6000,
  );
  await hideCaption(page);

  // ---------- 第 3 章：核心功能演示 ----------
  console.log("【第 3 章】核心功能演示：新建分析任务…");
  await page.getByRole("link", { name: "新建分析" }).click();
  await page.locator("#ticker").waitFor();
  await showCaption(
    page,
    "③ 核心功能演示 — 新建分析",
    "四种分析模式可选：快速筛查、完整备忘录、风险审视、估值检查。下面输入股票代码，选择「完整备忘录」模式，" +
      "并将报告语言设置为简体中文。",
    5000,
  );

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
  await showCaption(
    page,
    "③ 核心功能演示 — 可视化 Agent 工作流",
    "分析过程完全透明：输入规范化 → 公司识别 → 快速筛查 → 商业质量 → 护城河 → 管理层与资本配置 → 估值 → " +
      "逆向/风险审视 → 多空观点 → 最终备忘录，每一步实时推送进度（SSE），拒绝黑盒。",
    5500,
  );

  // ---------- 第 4 章：AI 能力展示 ----------
  console.log("【第 4 章】AI 能力展示…");
  await showCaption(
    page,
    "④ AI 能力展示",
    "多步骤智能体编排 + DeepSeek 大模型叙述层：评分、清单与估值区间全部由确定性算法计算，" +
      "大模型只基于已验证的数据撰写解读，从机制上杜绝「AI 编造数字」。数据缺失时自动降级为明确标注的模拟模式。",
    6000,
  );

  // 等待分析完成，报告自动呈现
  console.log("【第 4 章】等待分析完成，生成结构化报告…");
  await page.getByText("证据与数据来源").first().waitFor({ timeout: 90000 });
  await wait(1000);

  // ---------- 第 5 章：输入、处理过程和输出结果 ----------
  console.log("【第 5 章】展示输出结果：逐节浏览结构化报告…");
  await showCaption(
    page,
    "⑤ 输入 → 处理 → 输出",
    `输入仅需一个股票代码（${DEMO_TICKER}），处理过程为刚才的十步智能体流水线，输出是一份完整的结构化投资报告。` +
      "顶部为最终结论与置信度，下面逐节浏览。",
    5500,
  );

  await scrollToText(page, "快速筛查清单");
  await showCaption(page, "⑤ 输出 — 快速筛查清单", "六项通过/未通过的基本面体检，每项均附具体数据依据。", 3800);

  await scrollToText(page, "商业质量");
  await showCaption(page, "⑤ 输出 — 商业质量与护城河", "0-10 分确定性评分，附证据列表与风险提示。", 3800);

  await scrollToText(page, "估值");
  await showCaption(
    page,
    "⑤ 输出 — 估值与假设表",
    "给出低/基准/高三档合理价值区间，每一条假设都标明名称、取值与数据来源，完全可审计、可复核。",
    4500,
  );

  await scrollToText(page, "风险与逆向审视");
  await showCaption(page, "⑤ 输出 — 风险与逆向审视", "主要风险、论点致命项，以及查理·芒格式的逆向提问。", 3800);

  await scrollToText(page, "多头观点");
  await showCaption(page, "⑤ 输出 — 多空观点对照", "多头与空头论据并排呈现，强制平衡视角。", 3500);

  await scrollToText(page, "最终备忘录");
  await showCaption(
    page,
    "⑤ 输出 — 最终投资备忘录",
    "以 Markdown 渲染的完整备忘录，支持一键导出 Markdown / JSON，方便留档与二次加工。",
    4500,
  );

  await scrollToText(page, "证据与数据来源");
  await showCaption(
    page,
    "⑤ 输出 — 证据与数据来源",
    "每条数据都记录提供方与获取时间戳；演示环境未配置数据源密钥，因此全部明确标注为「模拟数据」。",
    4500,
  );
  await hideCaption(page);

  // ---------- 第 6 章：项目亮点说明 ----------
  console.log("【第 6 章】项目亮点：观察列表 + 报告历史 + 双语切换…");
  await page.getByText("最终结论").first().scrollIntoViewIfNeeded();
  await wait(600);
  await page.getByRole("button", { name: "加入观察列表" }).click();
  await wait(1200);

  await page.getByRole("link", { name: "观察列表" }).click();
  await page.getByText(DEMO_TICKER).first().waitFor();
  await showCaption(
    page,
    "⑥ 项目亮点 — 观察列表",
    "一键把标的加入观察列表，持续跟踪最近结论，等待更好的价格或更多证据。",
    4000,
  );

  await page.getByRole("link", { name: "报告" }).click();
  await page.getByText("报告", { exact: false }).first().waitFor();
  await showCaption(
    page,
    "⑥ 项目亮点 — 报告历史",
    "所有分析报告自动归档，随时回看公司、模式、结论、置信度与生成时间。",
    4000,
  );

  // 双语切换演示：中文 → English → 中文
  await showCaption(
    page,
    "⑥ 项目亮点 — 中英双语一键切换",
    "整个界面支持简体中文与 English 即时切换，不刷新页面、不丢失状态。现在切换到英文看看效果。",
    4200,
  );
  await page.getByRole("button", { name: "English" }).click();
  await wait(2500);
  await page.getByRole("button", { name: "简体中文" }).click();
  await wait(1500);

  await showCaption(
    page,
    "演示结束 — AlphaInvestPro",
    "亮点回顾：可视化智能体工作流｜确定性计算 + AI 叙述｜估值假设全透明｜证据与时间戳留痕｜中英双语｜" +
      "仅供研究，不构成投资建议。感谢观看！",
    6000,
  );

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
