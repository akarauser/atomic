import calendar
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Click
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Input, Label, OptionList

from .utils._logger import logger
from .utils._validation import config_args


class EditCellScreen(ModalScreen):
    DEFAULT_CSS = """
    EditCellScreen {
        align: center middle;
    }

    #cell-editor-container {
        border: none;
        width: auto;
        height: auto;
        background: $panel;
        padding: 1 1;
        border: thick $primary;

        & > Input#cell-editor {
            width: 38;
            margin: 1;
        }
        & > Label#cell-editor-title {
        margin-left: 2;
        }
    }
    """

    def __init__(
        self,
        cell_value: Any,
    ) -> None:
        super().__init__()
        self.cell_value = cell_value

    def compose(self) -> ComposeResult:
        with Vertical(id="cell-editor-container"):
            yield Label("Enter the new habit", id="cell-editor-title")
            yield Input(id="cell-editor")

    def on_mount(self) -> None:
        """Mounting Input widget."""
        cell_input = self.query_one(Input)
        cell_input.value = ""
        cell_input.focus()

    def on_click(self, event: Click) -> None:
        """Close the screen if the user clicks outside the modal content"""
        clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
        if clicked is self:
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """If submitted the text, it will shown on DataTable."""
        main_screen = self.app.get_screen("main")
        self.table = main_screen.query_one(DataTable)
        self.table.update_cell_at(
            self.table.cursor_coordinate,
            event.value,
            update_width=True,
        )
        self._save_data()
        self.app.pop_screen()
        self.notify("Habit updated!")
        logger.info("Habit name updated.")

    def _save_data(self):
        current_month = datetime.now().strftime("%b")
        current_year = datetime.now().strftime("%y")
        current_profile_path = Path("data\\profiles.json")
        try:
            with current_profile_path.open("r", encoding="utf-8") as file:
                self.current_profile_file = json.load(file)
                self.current_profile = self.current_profile_file["current"]
            self.data_file_path = Path(
                "data\\"
                + self.current_profile
                + "\\"
                + str(current_month)
                + current_year
                + ".json"
            )
            columns = [
                col_metadata.label.plain for col_metadata in self.table.columns.values()
            ]
            rows = [self.table.get_row(row_key) for row_key in self.table.rows]
            table_data = {}

            for index, _ in enumerate(self.table.rows):
                local_data_table = {}
                table_data[(str(index + 1))] = local_data_table
                for i in range(len(columns)):
                    local_data_table[columns[i]] = rows[index][i]
            with self.data_file_path.open("w", encoding="utf-8") as file:
                json.dump(table_data, file, indent=4)
        except Exception as e:
            logger.error(e)


class PriorityScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Close the screen")]

    DEFAULT_CSS = """
    PriorityScreen {
        align: center middle;
    }

    #levels-option-container {
        border: none;
        width: 40;
        height: auto;
        background: $panel;
        padding: 1 1;
        border: thick $primary;
    }
    """

    def __init__(
        self,
        cell_value: Any,
    ) -> None:
        super().__init__()
        self.cell_value = cell_value

    def compose(self) -> ComposeResult:
        with Vertical(id="levels-option-container"):
            yield OptionList(
                "Low",
                "Medium",
                "High",
                name="Select the priorty level",
            )

    def on_mount(self) -> None:
        """Mounting the Select widget for levels list."""
        cell_input = self.query_one(OptionList)
        cell_input.focus()

    def on_click(self, event: Click) -> None:
        """Close the screen if the user clicks outside the modal content"""
        clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
        if clicked is self:
            self.app.pop_screen()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """If any option chosen from the levels list, it will be get updated on main screen."""

        main_screen = self.app.get_screen("main")
        self.table = main_screen.query_one(DataTable)
        self.table.update_cell_at(
            self.table.cursor_coordinate,
            event.option.prompt,
            update_width=True,
        )
        try:
            self._save_data()
        except Exception as e:
            logger.error(e)
        self.app.pop_screen()

    def _save_data(self):
        current_month = datetime.now().strftime("%b")
        current_year = datetime.now().strftime("%y")
        current_profile_path = Path("data\\profiles.json")
        try:
            with current_profile_path.open("r", encoding="utf-8") as file:
                self.current_profile_file = json.load(file)
                self.current_profile = self.current_profile_file["current"]
            self.data_file_path = Path(
                "data\\"
                + self.current_profile
                + "\\"
                + str(current_month)
                + current_year
                + ".json"
            )
            columns = [
                col_metadata.label.plain for col_metadata in self.table.columns.values()
            ]
            rows = [self.table.get_row(row_key) for row_key in self.table.rows]
            table_data = {}

            for index, _ in enumerate(self.table.rows):
                local_data_table = {}
                table_data[(str(index + 1))] = local_data_table
                for i in range(len(columns)):
                    local_data_table[columns[i]] = rows[index][i]
            with self.data_file_path.open("w", encoding="utf-8") as file:
                json.dump(table_data, file, indent=4)
        except Exception as e:
            logger.error(e)


class HelpScreen(ModalScreen[None]):
    BINDINGS = [("escape", "app.pop_screen", "Close the screen")]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-screen-container {
        width: auto;
        max-width: 70%;
        height: auto;
        max-height: 70%;
        background: $panel;
        align: center middle;
        padding: 2 4;

        & > Label#exit {
            margin-top: 1;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help-screen-container"):
            yield Label(Text("Press ESC to exit.\n", style="italic"), id="exit")
            yield Label(
                "You can add new row with `a` and remove selected row with `r`."
            )
            yield Label("You can add your new habit from `Habit` column.")
            yield Label(
                "You can choose difficulty of the habit from 'Prio' column.\n* Different levels will give you 1/2/3 experience points."
            )
            yield Label("You can mark/unmark habits from day columns.")
            yield Label(
                "You can start gaining 'Gold' by marking at least three consecutive days.\n* Different levels will give you 5/10/15 gold."
            )


class SidebarWidget(Widget):
    DEFAULT_CSS = """
    SidebarWidget {
        width: 32;
        layer: sidebar;
        dock: left;
        offset-x: -100%;

        background: $primary;
        border-right: vkey $background;

        transition: offset 200ms;

        &.-visible {
            offset-x: 0;
        }

        & > Vertical {
            margin: 1 2;
            align: center middle;
        }
        & > Vertical > Label {
            width: 100%;
            text-align: center;
        }
    }
    """
    current_title = reactive("0", recompose=True)
    current_level = reactive("0", recompose=True)
    current_experience = reactive("0", recompose=True)
    current_gold = reactive("0", recompose=True)

    def compose(self) -> ComposeResult:
        self._get_data()
        self._calculate_stats()
        with Vertical():
            yield Label(
                Text(
                    f"{self.current_profile}".upper(),
                    style=config_args.colors["profile_name"],
                )
            )
            yield Label(Text(f"{self.current_title}\n", style="italic"))
            yield Label(f"Level: {self.current_level}")
            yield Label(
                f"Experience: {self.current_experience}/{config_args.experience[int(self.current_level) - 1]}"
            )
            yield Label(f"Gold: {self.current_gold}")

    def on_mount(self) -> None:
        """Mounting refresher for data."""
        self.set_interval(0.1, self._calculate_stats)

    def _get_data(self):
        """Pull data from the JSON files."""
        current_month = datetime.now().strftime("%b")
        current_year = datetime.now().strftime("%y")
        self.profiles_path = Path("data\\profiles.json")
        try:
            with self.profiles_path.open("r", encoding="utf-8") as file:
                self.profiles_file = json.load(file)
                self.current_profile = self.profiles_file["current"]

            self.data_file_path = Path(
                "data\\"
                + self.current_profile
                + "\\"
                + str(current_month)
                + current_year
                + ".json"
            )
            with self.data_file_path.open("r", encoding="utf-8") as file:
                self.data_file = json.load(file)

            if not self.profiles_file["profiles"].get(self.current_profile):
                self.profile_title = config_args.titles[0]
                self.profile_level = 1
                self.profile_experience = 0
                self.profile_gold = 0

                self.profiles_file["profiles"][self.current_profile] = {
                    "title": self.profile_title,
                    "level": self.profile_level,
                    "experience": self.profile_experience,
                    "gold": self.profile_gold,
                }
                with self.profiles_path.open("w", encoding="utf-8") as file:
                    json.dump(self.profiles_file, file, indent=4)
            else:
                self.profile_level = self.profiles_file["profiles"][
                    self.current_profile
                ]["title"]
                self.profile_level = self.profiles_file["profiles"][
                    self.current_profile
                ]["level"]
                self.profile_experience = self.profiles_file["profiles"][
                    self.current_profile
                ]["experience"]
                self.profile_experience = self.profiles_file["profiles"][
                    self.current_profile
                ]["gold"]

        except Exception as e:
            logger.error(e)

    def _calculate_stats(self):
        """Calculate and save title, level, experience and gold."""
        # Read current state
        with self.data_file_path.open("r", encoding="utf-8") as file:
            self.data_file = json.load(file)

        # Calculate current experience and level
        total_level = 0
        total_experience = 0
        for _, values in self.data_file.items():
            if "Low" in values.values():
                for value in values.values():
                    if value == "X":
                        total_experience += 1
            elif "Medium" in values.values():
                for value in values.values():
                    if value == "X":
                        total_experience += 2

            elif "High" in values.values():
                for value in values.values():
                    if value == "X":
                        total_experience += 3
            else:
                for value in values.values():
                    if value == "X":
                        total_experience += 1

        for i, experience in enumerate(config_args.experience, start=1):
            if total_experience < experience:
                total_level = i
                break

        # Calculate current gold
        total_gold = 0
        for row in self.data_file:
            streaks = list(self.data_file[row].values())
            streak_count = list(zip(streaks, streaks[1:], streaks[2:])).count(
                ("X", "X", "X")
            )
            if "Low" in streaks:
                total_gold += 5 * 1 * streak_count
            elif "Medium" in streaks:
                total_gold += 5 * 2 * streak_count
            elif "High" in streaks:
                total_gold += 5 * 3 * streak_count
            else:
                total_gold += 5 * 1 * streak_count

        # Dump data
        self.profile_title = config_args.titles[total_level - 1]
        self.profile_level = total_level
        self.profile_experience = total_experience
        self.profile_gold = total_gold

        self.profiles_file["profiles"][self.current_profile] = {
            "title": self.profile_title,
            "level": self.profile_level,
            "experience": self.profile_experience,
            "gold": self.profile_gold,
        }
        try:
            with self.profiles_path.open("w", encoding="utf-8") as file:
                json.dump(self.profiles_file, file, indent=4)
        except Exception as e:
            logger.error(e)

        # Update shown experience
        self.current_title = self.profile_title
        self.current_level = self.profile_level
        self.current_experience = self.profile_experience
        self.current_gold = self.profile_gold


class TrackerContainer(Horizontal):
    BINDINGS = [
        ("a", "add_habit", "Add habit"),
        ("r", "remove_habit", "Remove habit"),
        ("s", "toggle_sidebar", "Show profile"),
        ("h", "show_help", "Help"),
    ]
    DEFAULT_CSS = """
        TrackerContainer {
            width: 100%;
            height: 100%;
        }
    """
    show_sidebar = reactive(False)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield DataTable(
                fixed_columns=1, zebra_stripes=True, header_height=2, id="tracker-table"
            )
        yield SidebarWidget()
        yield Footer()

    def on_mount(self) -> None:
        """Mounting main DataTable."""
        self.table = self.query_one(DataTable)
        self._setup_table()
        self._load_data()
        self.table.focus()
        self.sidebar = self.query_one(SidebarWidget)

    def on_data_table_cell_selected(
        self,
        event: DataTable.CellSelected,
    ) -> None:
        """Depending on selection of column type, you can input the task name or it will mark X."""

        try:
            cell_value = event.value
            if event.coordinate.column == 0:
                self.app.push_screen(EditCellScreen(cell_value))
            elif event.coordinate.column == 1:
                self.app.push_screen(PriorityScreen(cell_value))
            else:
                cell_value = "" if event.value == "X" else "X"
                self.table.update_cell(
                    event.cell_key.row_key, event.cell_key.column_key, cell_value
                )
            self._save_data()
        except Exception as e:
            logger.error(e)

    def _setup_table(self):
        today = date.today()
        days_count = calendar.monthrange(today.year, today.month)[1]
        self.table.add_column(
            Text("Habit", style=config_args.colors["default_text"]), width=30
        )
        self.table.add_column(
            Text("Prio", style=config_args.colors["default_text"]), width=4
        )
        for day in range(1, days_count + 1):
            if day == today.day:
                self.table.add_column(
                    Text(
                        f"{datetime(today.year, today.month, day).strftime('%a')} {str(day)}",
                        style=config_args.colors["today"],
                        overflow="fold",
                    ),
                    width=3,
                )
            else:
                self.table.add_column(
                    Text(
                        f"{datetime(today.year, today.month, day).strftime('%a')} {str(day)}",
                        style=config_args.colors["default_text"],
                        overflow="fold",
                    ),
                    width=3,
                )
        logger.info("Table setup completed.")

    def _load_data(self):
        # Profiles file
        current_month = datetime.now().strftime("%b")
        current_year = datetime.now().strftime("%y")
        current_profile_path = Path("data\\profiles.json")
        with current_profile_path.open("r", encoding="utf-8") as file:
            self.current_profile_file = json.load(file)
            self.current_profile = self.current_profile_file["current"]

        # Data file
        try:
            self.data_file_path = Path(
                "data\\"
                + self.current_profile
                + "\\"
                + str(current_month)
                + current_year
                + ".json"
            )
            with self.data_file_path.open("r", encoding="utf-8") as file:
                for _, values in json.load(file).items():
                    self.table.add_row(*values.values())
            logger.info("Table loaded succesfully.")
        except Exception as e:
            logger.error(e)

    def _save_data(self):
        columns = [
            col_metadata.label.plain for col_metadata in self.table.columns.values()
        ]
        rows = [self.table.get_row(row_key) for row_key in self.table.rows]
        table_data = {}

        for index, _ in enumerate(self.table.rows):
            local_data_table = {}
            table_data[(str(index + 1))] = local_data_table
            for i in range(len(columns)):
                local_data_table[columns[i]] = rows[index][i]

        try:
            with self.data_file_path.open("w", encoding="utf-8") as file:
                json.dump(table_data, file, indent=4)
        except Exception as e:
            logger.error(e)

    def action_add_habit(self):
        """Adds new row."""
        empty_days = [""] * (len(self.table.columns))
        self.table.add_row(*empty_days)
        self._save_data()
        self.notify("New row added!")

    def action_remove_habit(self):
        """Removes the selected row."""
        row_key, _ = self.table.coordinate_to_cell_key(self.table.cursor_coordinate)
        self.table.remove_row(row_key)
        self._save_data()
        self.notify("Selected row deleted!")

    def action_show_help(self):
        """Shows the HelpScreen."""
        self.app.push_screen(HelpScreen())

    def action_toggle_sidebar(self) -> None:
        """Toggle the sidebar visibility."""
        self.show_sidebar = not self.show_sidebar

    def watch_show_sidebar(self, show_sidebar: bool) -> None:
        """Set or unset visible class when reactive changes."""
        self.query_one(SidebarWidget).set_class(show_sidebar, "-visible")


class AppScreen(Screen):
    def compose(self) -> ComposeResult:
        yield TrackerContainer()


class ProfileLoginScreen(ModalScreen[str]):
    DEFAULT_CSS = """
    ProfileLoginScreen {
        align: center middle;
    }

    ProfileLoginScreen > Vertical {
        background: $panel;
        height: auto;
        width: auto;
        border: thick $primary;
    }

    ProfileLoginScreen > Vertical > * {
        width: auto;
        height: auto;
    }

    ProfileLoginScreen Input {
        width: 40;
        margin: 1;
    }

    ProfileLoginScreen Label {
        margin-left: 2;
    }
    """

    def __init__(self, initial: str | None = None) -> None:
        """Initialise the input dialog."""
        super().__init__()
        self._prompt = "Profile Name"
        self._initial = initial

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        with Vertical(), Vertical(id="input"):
            yield Label(self._prompt)
            yield Input(self._initial or "")

    def on_mount(self) -> None:
        """Set up the dialog."""
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Accept and return the input."""
        self.query_one(Input)
        input = event.value
        self.dismiss(input)


class AtomicApp(App):
    SCREENS = {"profile": ProfileLoginScreen, "main": AppScreen}
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        """Mounting Profile Name screen."""
        self.profile_files_creation()

    @work
    async def profile_files_creation(self):
        """Pushing ProfileScreen and receives the data and it will push the main AppScreen."""

        # Get profile name and create folder if not exist
        self.profile_name: str = await self.push_screen_wait("profile")
        self.profile_name = self.profile_name.strip().casefold()
        profile_folder_path = Path(f"data\\{self.profile_name}")
        if not profile_folder_path.exists():
            os.makedirs(profile_folder_path)

        # Create or update current section of profiles.json
        try:
            self.profiles_path = Path("data\\profiles.json")
            if not self.profiles_path.exists():
                profiles = {"current": "", "profiles": {}}
                with self.profiles_path.open("w", encoding="utf-8") as file:
                    json.dump(profiles, file, indent=4)
        except Exception as e:
            logger.error(e)

        try:
            with self.profiles_path.open("r", encoding="utf-8") as file:
                self.current_profile_file = json.load(file)
                self.current_profile_file["current"] = self.profile_name
                with self.profiles_path.open("w", encoding="utf-8") as f:
                    json.dump(self.current_profile_file, f, indent=4)
        except Exception as e:
            logger.error(e)

        current_month = datetime.now().strftime("%b")
        current_year = datetime.now().strftime("%y")
        self.data_file_path = Path(
            "data\\"
            + self.profile_name
            + "\\"
            + str(current_month)
            + current_year
            + ".json"
        )
        if not self.data_file_path.exists():
            data = {}
            with self.data_file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        # Push the main screen
        if self.profile_name:
            self.notify(f"Loaded profile: {self.profile_name}")
            self.push_screen("main")


def run():
    app = AtomicApp()
    app.run()


if __name__ == "__main__":
    run()
