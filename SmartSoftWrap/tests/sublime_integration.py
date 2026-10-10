"""Run in Sublime as a temporary package, not with system Python.

Command: smart_soft_wrap_run_tests, args: output (absolute JSON path),
baseline (true before installing the package).
"""
import json
import os
import tempfile
import traceback

import sublime
import sublime_plugin


PLAIN = "Packages/Text/Plain text.tmLanguage"
CASES = [
    ("english_can_split", "characters", True),
    ("chinese_after_space", "characters", True),
    ("chinese_after_english", "characters", True),
    ("preserve_english_word", "words", False),
]


class SmartSoftWrapRunTestsCommand(sublime_plugin.WindowCommand):
    def run(self, output, baseline=False):
        self.output = output
        self.baseline = baseline
        self.original_sheet = self.window.active_sheet()
        self.results = []
        self.index = 0
        self.next_case()

    def next_case(self):
        if self.index == len(CASES):
            if self.baseline:
                self.finish()
            else:
                self.extra_checks()
                self.begin_custom_syntax_check()
            return
        self.view = self.window.new_file(syntax=PLAIN)
        self.view.set_scratch(True)
        self.view.set_name("SmartSoftWrap temporary test")
        if not self.baseline:
            self.view.run_command("smart_soft_wrap_set_mode", {"mode": "off"})
        self.view.settings().set("smart_soft_wrap_mode", "off")
        self.view.assign_syntax(PLAIN)
        self.view.run_command("append", {"characters": "a" * 2000})
        self.view.settings().set("font_face", "Consolas")
        self.view.settings().set("font_size", 24)
        self.view.settings().set("indent_subsequent_lines", False)
        self.view.settings().set("word_wrap", True)
        self.view.settings().set("wrap_width", 0)
        sublime.set_timeout(self.prepare_case, 250)

    def prepare_case(self):
        # Measure the viewport with a neutral ASCII line. Fixtures leave three
        # columns for a six-letter word, independently of the plugin's logic.
        origin_y = self.view.text_to_layout(0)[1]
        capacity = next(i for i in range(1, 2000) if self.view.text_to_layout(i)[1] > origin_y)
        name, mode, first_row = CASES[self.index]
        if name in ("english_can_split", "preserve_english_word"):
            prefix = "a" * (capacity - 4) + " "
            content = prefix + "hajimi"
            point = len(prefix)
        elif name == "chinese_after_space":
            prefix = "a" * (capacity - 5) + " "
            content = prefix + "哈基米" * 4
            point = len(prefix)
        else:
            prefix = "a" * (capacity - 12) + " hajimi"
            content = prefix + "哈基米" * 4
            point = len(prefix)
        self.case = (name, content, mode, point, first_row)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, self.view.size()))
        self.view.run_command("insert", {"characters": content})
        if not self.baseline:
            self.view.run_command("smart_soft_wrap_set_mode", {"mode": mode})
        sublime.set_timeout(self.check_case, 250)

    def check_case(self):
        name, content, mode, point, first_row = self.case
        try:
            origin = self.view.text_to_layout(0)
            # At a soft-wrap boundary text_to_layout(point) can report the END
            # of the previous visual row. Inspect the following character.
            start = self.view.text_to_layout(point + 1)
            end = self.view.text_to_layout(len(content) - 1)
            same_row = abs(start[1] - origin[1]) < 1
            require(same_row == first_row, (
                "Expected sequence start on first row: {}; got {}; "
                "origin={}, start={}, end={}".format(first_row, same_row, origin, start, end)
            ))
            require(end[1] > origin[1], "Expected visual wrapping")
            require(self.view.substr(sublime.Region(0, self.view.size())) == content, "Buffer text changed")
            require(self.view.rowcol(self.view.size())[0] == 0, "A real newline was inserted")
            self.results.append({"name": name, "passed": True, "start": start, "end": end})
        except Exception:
            tokens = self.view.extract_tokens_with_scopes(sublime.Region(max(0, point - 2), min(self.view.size(), point + 8)))
            self.results.append({
                "name": name, "passed": False, "error": traceback.format_exc(),
                "syntax": self.view.syntax().path,
                "mode": self.view.settings().get("smart_soft_wrap_mode"),
                "tokens": [(r.a, r.b, scope) for r, scope in tokens],
            })
        finally:
            self.view.close()
        self.index += 1
        self.next_case()

    def record(self, name, callback):
        try:
            callback()
            self.results.append({"name": name, "passed": True})
        except Exception:
            self.results.append({"name": name, "passed": False, "error": traceback.format_exc()})

    def extra_checks(self):
        self.record("restore_original_state_and_buffer", self.check_restore)
        self.record("do_not_replace_python_syntax", self.check_code_syntax)
        self.record("keep_combining_marks_and_emoji_together", self.check_clusters)

    def check_restore(self):
        view = self.window.new_file(syntax=PLAIN)
        view.set_scratch(True)
        try:
            view.run_command("smart_soft_wrap_set_mode", {"mode": "off"})
            view.assign_syntax(PLAIN)
            view.settings().set("word_wrap", False)
            view.settings().set("wrap_width", 42)
            text = "哈基米 hajimi\n第二行 e\u0301 👩‍💻"
            view.run_command("append", {"characters": text})
            view.sel().clear()
            view.sel().add(sublime.Region(2, 5))
            before_count = view.change_count()
            before_dirty = view.is_dirty()
            original_path = view.syntax().path
            for mode in ("characters", "words", "characters", "off"):
                view.run_command("smart_soft_wrap_set_mode", {"mode": mode})
                require(view.substr(sublime.Region(0, view.size())) == text, "Text changed on mode switch")
                require(view.change_count() == before_count, "Mode switch changed edit history")
                require(view.is_dirty() == before_dirty, "Mode switch changed dirty state")
                require([(r.a, r.b) for r in view.sel()] == [(2, 5)], "Selection changed")
                if mode != "off":
                    require(view.settings().get("wrap_width") == 0, "Width does not follow viewport")
                    require(view.settings().get("word_wrap") is True, "Soft wrapping not enabled")
            require(view.syntax().path == original_path, "Original syntax not restored")
            require(view.settings().get("word_wrap") is False, "Original wrap flag not restored")
            require(view.settings().get("wrap_width") == 42, "Original wrap width not restored")
            require(view.settings().get("smart_soft_wrap_previous") is None, "Snapshot not cleared")
            # Returning to this view must not auto-enable it after explicit off.
            if self.original_sheet:
                self.window.focus_sheet(self.original_sheet)
            self.window.focus_view(view)
            require(view.syntax().path == original_path, "Explicit off was ignored on activation")
        finally:
            view.close()

    def check_code_syntax(self):
        view = self.window.new_file(syntax="Packages/Python/Python.sublime-syntax")
        view.set_scratch(True)
        try:
            view.assign_syntax("Packages/Python/Python.sublime-syntax")
            path = view.syntax().path
            if self.original_sheet:
                self.window.focus_sheet(self.original_sheet)
            self.window.focus_view(view)
            view.run_command("smart_soft_wrap_set_mode", {"mode": "characters"})
            require(view.syntax().path == path, "Python syntax was replaced")
        finally:
            view.close()

    def check_clusters(self):
        view = self.window.new_file(syntax=PLAIN)
        view.set_scratch(True)
        try:
            view.run_command("append", {"characters": "a\u0301👩‍💻🇨🇳👍🏽"})
            for mode in ("characters", "words"):
                view.run_command("smart_soft_wrap_set_mode", {"mode": mode})
                tokens = view.extract_tokens_with_scopes(sublime.Region(0, view.size()))
                spans = [(region.a, region.b) for region, scope in tokens]
                require(spans == [(0, 2), (2, 5), (5, 7), (7, 9)], "Unexpected {} cluster boundaries: {}".format(mode, spans))
        finally:
            view.close()

    def begin_custom_syntax_check(self):
        candidates = sublime.find_resources("Custom Plain Text.sublime-syntax")
        require(len(candidates) == 1, "Expected one custom syntax fixture: {}".format(candidates))
        self.custom_syntax_path = candidates[0]
        self.view = self.window.new_file(syntax="SmartSoftWrap Custom Plain Text Fixture")
        self.view.set_scratch(True)
        self.view.assign_syntax(self.custom_syntax_path)
        self.view.run_command("append", {"characters": "HELLO custom text"})
        sublime.set_timeout(self.check_custom_syntax, 250)

    def check_custom_syntax(self):
        def check():
            view = self.view
            path = self.custom_syntax_path
            require(view.syntax() is not None and view.syntax().path == path, "Custom plain-text syntax was replaced or not loaded: {}; actual={}; setting={}; resource={}".format(path, view.syntax(), view.settings().get("syntax"), sublime.load_resource(path)))
            if self.original_sheet:
                self.window.focus_sheet(self.original_sheet)
            self.window.focus_view(view)
            view.run_command("smart_soft_wrap_set_mode", {"mode": "characters"})
            require(view.syntax().path == path, "Custom plain-text syntax was replaced")
        self.record("do_not_replace_custom_plain_text_syntax", check)
        self.view.close()
        self.begin_auto_enable_check()

    def begin_auto_enable_check(self):
        self.view = self.window.new_file(syntax=PLAIN)
        self.view.set_scratch(True)
        # on_new runs before the requested syntax is assigned; the production
        # callback deliberately waits until the next editor event-loop turn.
        sublime.set_timeout(self.check_auto_enable, 250)

    def check_auto_enable(self):
        def check():
            require(self.view.syntax().scope == "text.plain.smart_soft_wrap.characters", "New plain-text view was not enabled automatically")
        self.record("auto_enable_plain_text", check)
        self.view.close()
        self.begin_reflow()

    def begin_reflow(self):
        self.view = self.window.new_file(syntax=PLAIN)
        self.view.set_scratch(True)
        self.view.set_name("SmartSoftWrap temporary reflow test")
        self.reflow_text = "abcdefghij" * 5
        self.view.run_command("append", {"characters": self.reflow_text})
        self.view.run_command("smart_soft_wrap_set_mode", {"mode": "characters"})
        self.view.settings().set("font_face", "Consolas")
        self.view.settings().set("font_size", 12)
        sublime.set_timeout(self.check_wide_reflow, 250)

    def check_wide_reflow(self):
        self.wide_y = self.view.text_to_layout(len(self.reflow_text) - 1)[1]
        self.view.settings().set("font_size", 48)
        sublime.set_timeout(self.check_narrow_reflow, 250)

    def check_narrow_reflow(self):
        def check():
            narrow_y = self.view.text_to_layout(len(self.reflow_text) - 1)[1]
            require(narrow_y > self.wide_y, "Text did not reflow when available columns decreased")
            require(self.view.substr(sublime.Region(0, self.view.size())) == self.reflow_text, "Reflow changed text")
            require(self.view.settings().get("wrap_width") == 0, "Reflow is using a fixed width")
        self.record("viewport_reflow_without_text_changes", check)
        self.view.close()
        self.begin_file_check()

    def begin_file_check(self):
        self.original_bytes = "哈基米 hajimi\r\n第二行 e\u0301 👩‍💻\r\n".encode("utf-8-sig")
        with tempfile.NamedTemporaryFile(prefix="smart-soft-wrap-", suffix=".txt", delete=False) as stream:
            self.file_path = stream.name
            stream.write(self.original_bytes)
        self.view = self.window.open_file(self.file_path)
        self.file_attempts = 0
        sublime.set_timeout(self.check_file_bytes, 250)

    def check_file_bytes(self):
        if self.view.is_loading() and self.file_attempts < 20:
            self.file_attempts += 1
            sublime.set_timeout(self.check_file_bytes, 250)
            return
        def check():
            require(not self.view.is_loading(), "Timed out loading fixture")
            require(self.view.syntax().scope == "text.plain.smart_soft_wrap.characters", "Loaded txt was not enabled automatically")
            text = self.view.substr(sublime.Region(0, self.view.size()))
            for mode in ("words", "characters", "off"):
                self.view.run_command("smart_soft_wrap_set_mode", {"mode": mode})
                require(not self.view.is_dirty(), "Plugin dirtied the loaded file")
                require(self.view.substr(sublime.Region(0, self.view.size())) == text, "Loaded text changed")
            self.view.run_command("save")
            with open(self.file_path, "rb") as stream:
                require(stream.read() == self.original_bytes, "Saved bytes, CRLF or BOM changed")
        self.record("loaded_txt_auto_enable_and_saved_bytes_unchanged", check)
        self.view.close()
        os.remove(self.file_path)
        self.finish()

    def finish(self):
        if self.original_sheet and self.original_sheet.view():
            self.window.focus_sheet(self.original_sheet)
        with open(self.output, "w", encoding="utf-8") as stream:
            json.dump({"build": sublime.version(), "baseline": self.baseline, "results": self.results}, stream, ensure_ascii=False, indent=2)


def require(condition, message):
    # Sublime's optimized plugin host disables Python's assert statements.
    if not condition:
        raise AssertionError(message)
