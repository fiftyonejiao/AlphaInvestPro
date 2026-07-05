/**
 * 基于演示脚本内容生成可下载的简短 Markdown 文档
 *
 * 数据来源与视频录制脚本（record_demo.mjs）完全一致（demo_content.mjs），
 * 保证「视频演示」与「文档」永远同步。
 *
 * 使用方法：
 *   cd demo
 *   npm run generate-doc
 *
 * 输出：
 *   - demo/output/alphainvestpro_demo_doc_zh.md （可下载/分发副本）
 *   - demo/DEMO_DOC.md                          （仓库内同步副本）
 */

import { mkdirSync, writeFileSync } from "node:fs";

import { APP_NAME, CHAPTERS, DISCLAIMER } from "./demo_content.mjs";

const OUTPUT_DIR = "output";
const DOWNLOAD_FILE = `${OUTPUT_DIR}/alphainvestpro_demo_doc_zh.md`;
const REPO_FILE = "DEMO_DOC.md";

function render() {
  const lines = [];
  lines.push(`# ${APP_NAME} 演示文档（简版）`);
  lines.push("");
  lines.push("> 本文档由演示脚本内容自动生成（`npm run generate-doc`），与录制视频（`record_demo.mjs`）章节一一对应，可作为讲解词或独立阅读材料。");
  lines.push(`> 声明：${DISCLAIMER}`);
  lines.push("");
  for (const ch of CHAPTERS) {
    lines.push(`## ${ch.num}. ${ch.title}`);
    lines.push("");
    lines.push(ch.doc.trim());
    lines.push("");
  }
  return lines.join("\n");
}

const markdown = render();
mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(DOWNLOAD_FILE, markdown, "utf-8");
writeFileSync(REPO_FILE, markdown, "utf-8");
console.log(`【完成】简短文档已生成：demo/${DOWNLOAD_FILE}（可下载）与 demo/${REPO_FILE}（仓库副本）`);
