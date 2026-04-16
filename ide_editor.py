import string
from keyword import kwlist

# ============================================================
# 代码高亮模块 - 直接粘贴到你的代码中
# 在 custom_strategy_text 创建之后，调用 setup_syntax_highlight(custom_strategy_text)
# ============================================================

def setup_syntax_highlight(workArea):
    """为指定的ScrolledText控件添加语法高亮和自动缩进功能"""

    bifs = dir(__builtins__) if isinstance(__builtins__, dict) is False else list(__builtins__.keys())
    kws = kwlist

    # 配置颜色标签
    workArea.tag_config('bif',     foreground='purple')   # 内置函数：紫色
    workArea.tag_config('kw',      foreground='orange')   # 关键字：橙色
    workArea.tag_config('comment', foreground='red')      # 注释：红色
    workArea.tag_config('string',  foreground='green')    # 字符串：绿色

    def apply_highlight(event=None):
        """重新对全文进行语法高亮"""
        # 记录当前光标位置
        current_line_num, current_col_num = map(int, workArea.index('insert').split('.'))

        lines = workArea.get('1.0', 'end').rstrip('\n').splitlines(keepends=True)

        # 清除旧内容并重新写入，同时加标记
        workArea.delete('1.0', 'end')

        for line in lines:
            flag1, flag2, flag3 = False, False, False  # flag1:在单词中, flag2:双引号字符串, flag3:单引号字符串
            for index, ch in enumerate(line):
                if ch == '"' and not flag2:
                    flag3 = not flag3
                    workArea.insert('insert', ch, 'string')
                elif ch == "'" and not flag3:
                    flag2 = not flag2
                    workArea.insert('insert', ch, 'string')
                elif flag2 or flag3:
                    workArea.insert('insert', ch, 'string')
                else:
                    if ch not in string.ascii_letters + '_':
                        if flag1:
                            flag1 = False
                            # 获取刚插入的单词
                            start = index - 1
                            while start > 0 and line[start - 1] in string.ascii_letters + '_':
                                start -= 1
                            word = line[start:index]
                            # 删除刚插入的普通字符，重新加标记插入
                            # 由于已经逐字插入，这里补充对上一个词的标记（见下方重构版本）
                        if ch == '#':
                            workArea.insert('insert', line[index:], 'comment')
                            break
                        else:
                            workArea.insert('insert', ch)
                    else:
                        if not flag1:
                            flag1 = True
                        workArea.insert('insert', ch)
            else:
                # 处理行尾还在单词中的情况
                pass

        workArea.mark_set('insert', f'{current_line_num}.{current_col_num}')

    def process_key(event):
        """处理按键：回车自动缩进 + 退格智能删除空格"""
        current_line_num, current_col_num = map(int, workArea.index('insert').split('.'))

        if event.keycode == 13:  # 回车键
            last_line_num = current_line_num - 1
            last_line = workArea.get(f'{last_line_num}.0', 'insert').rstrip()
            num = len(last_line) - len(last_line.lstrip(' '))
            if (last_line.endswith(':') or
                (':' in last_line and last_line.split(':')[-1].strip().startswith('#'))):
                num += 4
            elif last_line.strip().startswith(('return', 'break', 'continue', 'pass', 'raise')):
                num = max(0, num - 4)
            workArea.insert('insert', ' ' * num)

        elif event.keysym == 'BackSpace':
            current_line = workArea.get(
                f'{current_line_num}.0',
                f'{current_line_num}.{current_col_num}'
            )
            num = len(current_line) - len(current_line.rstrip(' '))
            num = min(3, num)
            if num > 1:
                workArea.delete(
                    f'{current_line_num}.{current_col_num - num}',
                    f'{current_line_num}.{current_col_num}'
                )

        else:
            # 对全文重新着色
            lines = workArea.get('1.0', 'end').rstrip('\n').splitlines(keepends=True)
            workArea.delete('1.0', 'end')

            for line in lines:
                flag1, flag2, flag3 = False, False, False
                start = 0
                i = 0
                while i < len(line):
                    ch = line[i]
                    if ch == '"' and not flag2:
                        if flag1:
                            word = line[start:i]
                            tag = 'bif' if word in bifs else ('kw' if word in kws else '')
                            workArea.insert('insert', word, tag)
                            flag1 = False
                        flag3 = not flag3
                        workArea.insert('insert', ch, 'string')
                    elif ch == "'" and not flag3:
                        if flag1:
                            word = line[start:i]
                            tag = 'bif' if word in bifs else ('kw' if word in kws else '')
                            workArea.insert('insert', word, tag)
                            flag1 = False
                        flag2 = not flag2
                        workArea.insert('insert', ch, 'string')
                    elif flag2 or flag3:
                        workArea.insert('insert', ch, 'string')
                    elif ch == '#':
                        if flag1:
                            word = line[start:i]
                            tag = 'bif' if word in bifs else ('kw' if word in kws else '')
                            workArea.insert('insert', word, tag)
                            flag1 = False
                        workArea.insert('insert', line[i:], 'comment')
                        break
                    elif ch in string.ascii_letters + '_':
                        if not flag1:
                            flag1 = True
                            start = i
                    else:
                        if flag1:
                            word = line[start:i]
                            tag = 'bif' if word in bifs else ('kw' if word in kws else '')
                            workArea.insert('insert', word, tag)
                            flag1 = False
                        workArea.insert('insert', ch)
                    i += 1

                if flag1:
                    word = line[start:]
                    tag = 'bif' if word in bifs else ('kw' if word in kws else '')
                    workArea.insert('insert', word, tag)

            workArea.mark_set('insert', f'{current_line_num}.{current_col_num}')

    workArea.bind('<KeyRelease>', process_key)


# ============================================================
# 调用方式（在你创建 custom_strategy_text 之后加这一行）：
# setup_syntax_highlight(custom_strategy_text)
# ============================================================


import sys
import io
import tkinter as tk
from tkinter import scrolledtext

#
def run_custom_code():
    code = custom_strategy_text.get("1.0", "end-1c")  # 获取文本框内容

    # 捕获输出
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        exec(code, {})  # 在隔离命名空间中运行
        output = buffer.getvalue()
    except Exception as e:
        output = f"错误：{e}"
    finally:
        sys.stdout = old_stdout

    # 显示结果（假设你有一个output_text控件）
    output_text.config(state='normal')
    output_text.delete("1.0", "end")
    output_text.insert("end", output)
    output_text.config(state='disabled')
