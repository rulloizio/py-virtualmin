
import tkinter as tk
from tkinter import ttk
import configparser
import json
from pathlib import Path, PurePath
import main

class VirtualminGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtualmin Data Viewer")
        self.geometry("1024x768")

        self.create_widgets()

    def create_widgets(self):
        # Button to fetch data
        self.fetch_button = ttk.Button(self, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(pady=10)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Treeview to display data
        self.tree = ttk.Treeview(self.main_frame, columns=("Value"), show="tree headings")
        self.tree.heading("#0", text="Server/Domain")
        self.tree.heading("Value", text="Status/Username")
        self.tree.pack(side=tk.LEFT, expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self.show_server_info)

        # Server info display
        self.server_info_frame = ttk.LabelFrame(self.main_frame, text="Server Information")
        self.server_info_frame.pack(side=tk.RIGHT, expand=True, fill="both", padx=10)

        self.server_info_tree = ttk.Treeview(self.server_info_frame, columns=("Value"), show="tree headings")
        self.server_info_tree.heading("#0", text="Property")
        self.server_info_tree.heading("Value", text="Value")
        self.server_info_tree.pack(expand=True, fill="both")

        # Status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def fetch_data(self):
        self.status_bar.config(text="Fetching data...")
        self.update_idletasks()

        config_dir = 'personal_data'
        virtualmin_ini_file = 'virtualmin.ini'
        
        c = Path(PurePath.joinpath(Path.cwd(), config_dir, virtualmin_ini_file))
        
        if not c.exists() or not c.is_file():
            self.status_bar.config(text=f"Error: Configuration file not found at {c}")
            return

        cfg = configparser.ConfigParser()
        cfg.read(c)

        host_dict = []
        # Clear previous data in the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)

        for host in cfg.sections():
            stato, details = main.getServerInformation(host, cfg)
            host_dict.append({'Server': host, 'stato': stato, 'deatils': details})
            
            # Insert server status into the treeview
            server_id = self.tree.insert("", "end", text=host, values=(stato,))

            if stato == 'success':
                sites = main.getDomainInformation(host, cfg)
                if sites:
                    # Create a node for the sites
                    sites_id = self.tree.insert(server_id, "end", text="Sites", values=(""))
                    for site in sites:
                        self.tree.insert(sites_id, "end", text=site['Dominio'], values=(site['Username'],))


        self.status_bar.config(text="Data fetched successfully.")

    def show_server_info(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item)
        # Check if the selected item is a server (a root item)
        if self.tree.parent(selected_item) == "":
            host = item['text']
            config_dir = 'personal_data'
            json_file_path = Path(PurePath.joinpath(Path.cwd(), config_dir, f"{host}.json"))

            if json_file_path.exists():
                with open(json_file_path, 'r') as f:
                    server_data = json.load(f)
                
                self.populate_server_info_tree(server_data)
            else:
                self.clear_server_info_tree()
                self.server_info_tree.insert("", "end", text="Error", values=("No information file found",))

    def populate_server_info_tree(self, data, parent=""):
        self.clear_server_info_tree()
        self._populate_tree(data, parent)

    def _populate_tree(self, data, parent=""):
        if isinstance(data, dict):
            for key, value in data.items():
                node = self.server_info_tree.insert(parent, "end", text=key, open=True)
                if key == 'output' and isinstance(value, str):
                    for line in value.splitlines():
                        if ':' in line:
                            prop, val = line.split(':', 1)
                            self.server_info_tree.insert(node, "end", text=prop.strip(), values=(val.strip(),))
                        else:
                            self.server_info_tree.insert(node, "end", text=line)
                else:
                    self._populate_tree(value, node)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                node = self.server_info_tree.insert(parent, "end", text=f"[{index}]", open=True)
                self._populate_tree(value, node)
        else:
            self.server_info_tree.item(parent, values=(data,))

    def clear_server_info_tree(self):
        for i in self.server_info_tree.get_children():
            self.server_info_tree.delete(i)


if __name__ == "__main__":
    app = VirtualminGUI()
    app.mainloop()
