from .config_manager import ConfigManager
from .subprocess_utilities import SubprocessUtilities

class GumPrompts:

    def __init__(self):
        self.config_manager = ConfigManager()
        self.subprocess_utilities = SubprocessUtilities()

    def gum_input(self, header, placeholder=None):
        """Prompt the user to input a value and return the input."""
        if placeholder is None:
            placeholder = ""
        sanitize_header = header.replace("'", "'\\''")
        sanitize_placeholder = placeholder.replace("'", "'\\''")
        gum_input = f"gum input\
            --header '{sanitize_header}'\
            --width 65\
            --header.foreground '{self.config_manager.primary_color}'\
            --cursor.foreground '{self.config_manager.cursor_color}'\
            --prompt '{self.config_manager.cursor_style}'\
            --prompt.foreground '{self.config_manager.prompt_color}'\
            --value '{sanitize_placeholder}'\
            --char-limit 0"

        _, gum_input_output = self.subprocess_utilities.run_and_capture_output(gum_input)

        return gum_input_output

    def gum_write(self, header, templated_text=None):
        """Prompt the user to write text and return the text."""
        if templated_text:
            body_from_env = templated_text
        else:
            body_from_env = " "
        gum_write = f"gum write\
            --header '{header}'\
            --header.foreground '{self.config_manager.primary_color}'\
            --cursor.foreground '{self.config_manager.cursor_color}'\
            --prompt.foreground '{self.config_manager.secondary_color}'\
            --char-limit 0\
            --value $'{body_from_env}'\
            --width 65\
            --height 10"

        _, gum_write_output = self.subprocess_utilities.run_and_capture_output(gum_write)

        return gum_write_output

    def gum_confirm(self, message):
        """Prompt the user to confirm an action and return the confirmation."""
        gum_confirm = f"gum confirm '{message}'\
            --prompt.foreground '{self.config_manager.primary_color}'\
            --selected.background '{self.config_manager.secondary_color}'\
            --unselected.background '{self.config_manager.tertiary_color}'"

        gum_confirm_process, _ = self.subprocess_utilities.run_and_capture_output(gum_confirm, store_exit_code=True)

        return gum_confirm_process != 1

    def gum_filter(self, filter_list, header, has_limit=True):
        """Filter a list of options and return the selected option."""

        gum_filter = f"gum filter {filter_list}\
            --text.foreground '{self.config_manager.prompt_color}'\
            --indicator '{self.config_manager.cursor_style}'\
            --indicator.foreground '{self.config_manager.cursor_color}'\
            --header '{header}'\
            --header.foreground '{self.config_manager.primary_color}'\
            --prompt '{self.config_manager.filter_prompt}'\
            --prompt.foreground '{self.config_manager.quaternary_color}'\
            --cursor-text.foreground '{self.config_manager.secondary_color}'\
            --match.foreground '{self.config_manager.tertiary_color}'\
            --height 10\
            --unselected-prefix.foreground '{self.config_manager.tertiary_color}'\
            --selected-indicator.foreground '{self.config_manager.tertiary_color}'"

        if not has_limit:
            gum_filter += " --no-limit"

        _, gum_filter_output = self.subprocess_utilities.run_and_capture_output(gum_filter)

        return gum_filter_output

    def gum_choose(self, choices):
        """Prompt the user to choose an option from a list and return the chosen option."""
        gum_choose = f"gum choose {choices}\
            --ordered\
            --cursor '{self.config_manager.cursor_style}'\
            --cursor.foreground '{self.config_manager.quaternary_color}'\
            --item.foreground '{self.config_manager.tertiary_color}'"

        _, gum_choose_output = self.subprocess_utilities.run_and_capture_output(gum_choose)

        return gum_choose_output
