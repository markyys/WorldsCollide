import menus.pregame_track_scroll_area as scroll_area
from data.text.text2 import text_value
import instruction.f0 as f0

class FlagsRewardItems(scroll_area.ScrollArea):
    MENU_NUMBER = 16

    def __init__(self, item_ids):
        self.number_items = len(item_ids)
        self.lines = []

        self.lines.append(scroll_area.Line(f"Item Rewards ({self.number_items})", f0.set_blue_text_color))
        self.lines.append(scroll_area.Line(f"Checks may reward any of:", f0.set_gray_text_color))

        item_lines = FlagsRewardItems._format_items_menu(item_ids)

        for list_value in item_lines:
            padding = scroll_area.WIDTH - (len(list_value))
            self.lines.append(scroll_area.Line(f"{' ' * padding}{list_value}", f0.set_user_text_color))

        super().__init__()

    def _format_items_menu(item_ids):
        from constants.items import id_name
        COLUMN_WIDTHS = [13, 12]
        item_lines = []

        # Step through each spell by the number of columns
        for item_idx in range(0, len(item_ids), len(COLUMN_WIDTHS)):
            current_line = ''
            # Populate each column on the line
            for col in range(0, len(COLUMN_WIDTHS)):
                if(item_idx + col < len(item_ids)):
                    a_item_id = item_ids[item_idx + col]
                    icon = FlagsRewardItems._get_item_icon(a_item_id)
                    item_str = f"{icon}{id_name[a_item_id]}"
                    padding = COLUMN_WIDTHS[col] - len(item_str)
                    current_line += f"{item_str}{' ' * padding}"
                else:
                    # No spell, add padding
                    current_line += f"{' ' * COLUMN_WIDTHS[col]}"
            # Write the line
            item_lines.append(current_line)
        return item_lines

    def _get_item_icon(item_id):
        from constants.spells import black_magic_ids, gray_magic_ids, white_magic_ids
        from data.text.text2 import text_value
        icon = ''
        # Potentially this could be used to get the appropriate icon for each item type using the same code from
        # the remove learnable spells menu class
        return icon