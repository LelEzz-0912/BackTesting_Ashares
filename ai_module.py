import threading
import markdown
import pandas as pd
from tkinterweb import HtmlFrame
from openai import OpenAI
import tkinter as tk
import ttkbootstrap as ttk

# --- 基础配置 ---
API_KEY = ""
BASE_URL = "https://api.deepseek.com"

def set_ai_api_key(api_key):
    global API_KEY
    API_KEY = api_key

class StockAIEngine:
    def __init__(self, output_container, input_widget, send_button, stock_obj=None):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.input_widget = input_widget
        self.send_button = send_button
        self.stock_obj = stock_obj

        # --- 核心修复：避开初始化参数错误 ---
        # 1. 先创建原生滚动条
        self.yscrollbar = ttk.Scrollbar(output_container, orient=tk.VERTICAL)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.xscrollbar = ttk.Scrollbar(output_container, orient=tk.HORIZONTAL)
        self.xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 2. 创建 HtmlFrame，不带任何滚动参数
        self.html_view = HtmlFrame(output_container)
        self.html_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3. 后绑定：使用 tkinterweb 提供的配置接口
        # 很多版本下 HtmlFrame 实际上自带滚动条，如果显示了两个，可以把上面的 self.scrollbar 删掉
        # 如果需要手动绑定，则使用如下配置：
        try:
            self.html_view.config(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar.config(command=self.html_view.yview)
            self.html_view.config(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar.config(command=self.html_view.xview)
        except:
            # 如果 config 也报错，说明该版本强制内置了滚动条，我们直接忽略手动绑定即可
            self.yscrollbar.pack_forget()
            self.xscrollbar.pack_forget()

            # 初始上下文
        self.messages = self._build_context()
        self.full_md = "## Deepseek股票助手已就绪\n---\n"

        self.css_style = """
        <style>
            body { background-color: #1e1e1e; color: #d4d4d4; font-family: 微软雅黑; font-size: 18px; padding: 15px; }

            /* --- 新增：专门控制系统提示字体的样式 --- */
            blockquote { 
                font-size: 12px;           /* 调小字体，比如 11px 或 12px */
                color: #ce8d64;           /* 调淡颜色，使其不那么扎眼 */
                border-left: 2px solid #444444; 
                margin: 10px 0; 
                padding-left: 10px;
                font-style: italic;       /* 斜体，看起来更像辅助信息 */
            }

            /* 原有的其他样式保持不变 */
            table { border-collapse: collapse; width: 100%; margin: 10px 0; background: #252526; }
            th, td { border: 1px solid #454545; padding: 8px; text-align: left; }
            th { background: #333; color: #569cd6; }
            .user-msg { color: #569cd6; font-weight: bold; border-left: 3px solid #569cd6; padding-left: 10px; margin-top: 15px; }
        </style>
        """

        self._refresh_ui()
        self.send_button.config(command=self.handle_send)

    def _build_context(self):
        prompt = "你是一个专业的股票分析师。"
        if self.stock_obj:
            prompt += f"\n分析对象为{self.stock_obj.name}，数据如下：\n"
            for attr in dir(self.stock_obj):
                if not attr.startswith('__'):
                    val = getattr(self.stock_obj, attr)
                    if isinstance(val, pd.DataFrame) and not val.empty:
                        prompt += f"\n- {attr}:\n{val.to_markdown()}\n"
        return [{"role": "system", "content": prompt}]

        # --- 动态更新接口 ---
    def update_stock_instance(self, new_stock_obj):
        """外部调用此方法来注入新的股票数据"""
        self.stock_obj = new_stock_obj

        # --- 更新 AI 记忆逻辑 (保持不变) ---
        new_context = self._build_context()
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0] = new_context[0]
        else:
            self.messages.insert(0, new_context[0])

        # --- 直接使用 HTML 强行控制外观 ---
        stock_code = getattr(new_stock_obj, 'code', 'Unknown')
        sys_msg = f"""
<div style="margin: 15px 0; padding: 5px 10px; border-left: 2px solid #444; color: #888 !important; font-size: 14px !important; font-style: italic;">
    [系统通知] 已挂载股票实例: {stock_code}，Deepseek可进行深度分析
</div>
---
"""
        self.full_md += f"\n\n{sys_msg}"

        # 强制刷新
        self._refresh_ui(auto_scroll=True)

    def _refresh_ui(self, auto_scroll=True):
        """
        利用 HTML autofocus 和 锚点跳转 强制置底
        """
        html_body = markdown.markdown(self.full_md, extensions=['extra', 'codehilite', 'tables'])

        # 在 HTML 末尾添加一个带 ID 的输入框或锚点，并利用 JS 强制其进入视图
        full_html = f"""
        <html>
            {self.css_style}
            <body>
                {html_body}
                <div id="bottom_mark" style="height:1px;">.</div>
                <script>
                    window.scrollTo(0, document.body.scrollHeight);
                    document.getElementById('bottom_mark').scrollIntoView();
                </script>
            </body>
        </html>
        """

        # 渲染 HTML
        self.html_view.load_html(full_html)

        # 针对新版 tkinterweb 的双重保险：多段式强制滚动
        if auto_scroll:
            # 10ms: 初次尝试
            self.html_view.after(10, lambda: self.html_view.yview_moveto(1.0))
            # 50ms: 渲染中途
            self.html_view.after(50, lambda: self.html_view.yview_moveto(1.0))
            # 200ms: 确保排版结束后的最终固定
            self.html_view.after(200, lambda: self.html_view.yview_moveto(1.0))

    def _run_query(self):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.messages,
                stream=True
            )

            ai_reply = ""
            count = 0
            for chunk in response:
                text = chunk.choices[0].delta.content
                if text:
                    ai_reply += text
                    self.full_md += text
                    count += 1
                    # --- 关键：大幅降低刷新频率 ---
                    # 只有每 10 个 token 才刷新一次 UI
                    # 这样可以减少“跳回顶部”的触发次数，提高用户手动滚动的成功率
                    if count % 10 == 0:
                        self.input_widget.after(0, lambda: self._refresh_ui(True))

            # 结束时务必刷新一次
            self.input_widget.after(0, lambda: self._refresh_ui(True))
            self.messages.append({"role": "assistant", "content": ai_reply})
        finally:
            self.input_widget.after(0, lambda: self.send_button.config(state=tk.NORMAL, text="发送"))

    def handle_send(self):
        if isinstance(self.input_widget, tk.Text):
            content = self.input_widget.get("1.0", tk.END).strip()
        else:
            content = self.input_widget.get().strip()

        if not content: return

        self.input_widget.delete("1.0" if isinstance(self.input_widget, tk.Text) else 0, tk.END)
        self.send_button.config(state=tk.DISABLED, text="思考中")

        self.full_md += f"\n\n<div class='user-msg'>User: {content}</div>\n\n"
        self.messages.append({"role": "user", "content": content})
        self._refresh_ui()

        threading.Thread(target=self._run_query, daemon=True).start()

def attach_ai(output_container, input_widget, send_button, stock_instance=None):
    return StockAIEngine(output_container, input_widget, send_button, stock_instance)