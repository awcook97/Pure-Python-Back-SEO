import dearpygui.dearpygui as dpg


class Add_InfoWidget:
    def __init__(self, parent, name="More Info") -> None:
        self.myID: int | str = dpg.add_tree_node(parent=parent, label=name)

    def update(self, data) -> None:
        dpg.delete_item(self.myID, children_only=True)
        self.add_info(data, self.myID)

    def add_info(self, info, parent) -> None:
        if type(info) is dict:
            for k, v in info.items():
                ki: int | str = dpg.add_tree_node(label=k, parent=parent)
                self.add_info(v, ki)
        elif type(info) is list:
            for i in info:
                self.add_info(i, parent)
        else:
            # dpg.add_button(label=val, parent=parent, user_data=val, callback=lambda:dpg.set_clipboard_text(val))
            with dpg.group(horizontal=True, parent=parent):
                dpg.add_button(
                    label="Copy",
                    user_data=info,
                    callback=lambda: dpg.set_clipboard_text(info),
                    small=True,
                )
                dpg.add_text(info, wrap=0)
