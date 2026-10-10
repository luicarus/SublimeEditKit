"""Provide plain-text soft wrapping without editing buffer contents."""
import sublime
import sublime_plugin


SYNTAXES = {
    "characters": "Packages/SmartSoftWrap/Soft Wrap Characters.sublime-syntax",
    "words": "Packages/SmartSoftWrap/Soft Wrap Words.sublime-syntax",
}
PLAIN_SYNTAX = "Packages/Text/Plain text.tmLanguage"
MODE_KEY = "smart_soft_wrap_mode"
PREVIOUS_KEY = "smart_soft_wrap_previous"
_loaded = False


def _eligible(view):
    if not view.is_valid() or view.is_loading() or view.settings().get("is_widget"):
        return False
    syntax = view.syntax()
    return syntax is not None and (
        syntax.path == PLAIN_SYNTAX or syntax.path in SYNTAXES.values()
    )


def _enable(view, mode):
    if mode not in SYNTAXES or not _eligible(view):
        return
    settings = view.settings()
    if settings.get(PREVIOUS_KEY) is None:
        syntax = view.syntax()
        settings.set(PREVIOUS_KEY, {
            "syntax": syntax.path if syntax.path not in SYNTAXES.values() else PLAIN_SYNTAX,
            "word_wrap": settings.get("word_wrap"),
            "wrap_width": settings.get("wrap_width"),
        })
    settings.set(MODE_KEY, mode)
    view.assign_syntax(SYNTAXES[mode])
    settings.set("word_wrap", True)
    settings.set("wrap_width", 0)


def _restore(view):
    settings = view.settings()
    previous = settings.get(PREVIOUS_KEY)
    settings.set(MODE_KEY, "off")
    if not previous:
        return
    syntax = view.syntax()
    if syntax is not None and syntax.path in SYNTAXES.values():
        original = sublime.syntax_from_path(previous["syntax"])
        view.assign_syntax(original or PLAIN_SYNTAX)
    for key in ("word_wrap", "wrap_width"):
        if previous[key] is None:
            settings.erase(key)
        else:
            settings.set(key, previous[key])
    settings.erase(PREVIOUS_KEY)


def _auto_enable(view):
    if not _loaded or not _eligible(view):
        return
    if view.settings().get(MODE_KEY) == "off":
        return
    config = sublime.load_settings("SmartSoftWrap.sublime-settings")
    if config.get("auto_enable", True):
        mode = view.settings().get(MODE_KEY, config.get("default_mode", "characters"))
        _enable(view, mode if mode in SYNTAXES else "characters")


def plugin_loaded():
    global _loaded
    _loaded = True
    for window in sublime.windows():
        for view in window.views():
            _auto_enable(view)


def plugin_unloaded():
    global _loaded
    _loaded = False
    for window in sublime.windows():
        for view in window.views():
            if view.settings().get(PREVIOUS_KEY):
                mode = view.settings().get(MODE_KEY)
                _restore(view)
                # Preserve the mode across a plugin code reload.
                view.settings().set(MODE_KEY, mode)


class SmartSoftWrapSetModeCommand(sublime_plugin.TextCommand):
    def run(self, edit, mode="characters"):
        if mode == "off":
            _restore(self.view)
        else:
            _enable(self.view, mode)

    def is_enabled(self, mode="characters"):
        if mode == "off":
            return bool(self.view.settings().get(PREVIOUS_KEY))
        return mode in SYNTAXES and _eligible(self.view)


class SmartSoftWrapListener(sublime_plugin.EventListener):
    def on_new(self, view):
        sublime.set_timeout(lambda: _auto_enable(view), 0)

    def on_load(self, view):
        _auto_enable(view)

    def on_activated(self, view):
        _auto_enable(view)
