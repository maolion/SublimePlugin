import sublime, sublime_plugin
import project

from project import MESSAGE, DEBUG,XError

class JProjectOpenInExploreCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command( "open_dir", {
            "dir" : dirs[0]
        } )

    def is_visible(self, dirs):
        return len(dirs) > 0
