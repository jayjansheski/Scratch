import sublime
import sublime_plugin
import re
import os
from time import strftime


def getPath():
    s = sublime.load_settings("Scratch.sublime-settings")
    save_path = s.get("save_path", "~/Documents/Scratch")
    save_path = os.path.expanduser(save_path)
    return save_path


def getExtension():
    s = sublime.load_settings("Scratch.sublime-settings")
    save_extension = s.get("extension", ".Scratch")
    return save_extension


def getFilenameType():
    s = sublime.load_settings("Scratch.sublime-settings")
    save_filename_type = s.get("filename_type", "number")
    return save_filename_type


def getFilenameFormat():
    s = sublime.load_settings("Scratch.sublime-settings")
    save_filename_format = s.get("filename_format", "%0d")
    return save_filename_format


class SyntaxPreSaveCommand(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if not view.file_name().startswith(getPath()):
            return

        # If first line is a file extension:
        infile_re = re.match(r"\.\w+$", view.substr(view.line(0)))
        filename_re = re.match(r"(.+)(\.\w+)$", view.file_name())

        if infile_re and filename_re and infile_re.group() != filename_re.group(2):
            new_name = filename_re.group(1) + infile_re.group()
            os.rename(view.file_name(), new_name)
            with open(new_name, 'r') as fin:
                data = fin.read().splitlines(True)
            with open(new_name, 'w') as fout:
                fout.writelines(data[1:])
            sublime.active_window().run_command("close")
            sublime.active_window().open_file(new_name)


class ScratchCommand(sublime_plugin.WindowCommand):
    def run(self):
        save_path = getPath()
        save_extension = getExtension()
        save_filename_type = getFilenameType()
        save_filename_format = getFilenameFormat()

        # Ensure directory exists
        try:
            os.mkdir(getPath())
        except OSError:
            pass

        if save_filename_type == "date":
            file_root = strftime(save_filename_format)
        else:
            new_int = self._getNextInt(save_path)
            file_root = save_filename_format % new_int

        full_path = save_path + "/" + file_root + save_extension
        self.window.open_file(full_path)

    def _getNextInt(self, directory):
        """Return the next highest integer to be used for a filename in directory"""
        files = os.listdir(directory)
        max = -1

        for file_name in files:
            m = re.match(r"(\d+).", file_name)
            if m and int(m.group(1)) > max:
                max = int(m.group(1))

        return max + 1
