import tkinter as tk
from tkinter import messagebox
import random
import time
from queue import Queue

class RouterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Router Management")

        self.ports = [None] * 24
        self.users = ["user" + str(i) for i in range(1, 24)]
        self.admins = ["admin" + str(i) for i in range(1, 5)]
        self.queue = Queue()
        self.connected_users = set()
        self.connected_admins = set()

        self.create_main_screen()
        self.start_simulation()

    def create_main_screen(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        tk.Label(self.main_frame, text="Router Ports Status").pack(pady=10)

        self.port_frame = tk.Frame(self.main_frame)
        self.port_frame.pack(pady=10)

        self.port_labels = []
        for i in range(24):
            port_label = tk.Label(self.port_frame, text=f"Port {i+1}: Free", bg="lightgrey", width=20)
            port_label.grid(row=i//8, column=i%8, padx=5, pady=5)
            self.port_labels.append(port_label)

        self.queue_label = tk.Label(self.main_frame, text="Queue: ")
        self.queue_label.pack(pady=10)

    def start_simulation(self):
        # Connect all users and admins initially
        for user in self.users + self.admins:
            self.connect_user(user)

        # Start the simulation
        self.root.after(1000, self.simulate)

    def simulate(self):
        # Randomly select a few users to disconnect
        users_to_disconnect = random.sample(self.users + self.admins, random.randint(1, 5))
        for user in users_to_disconnect:
            disconnect_time = random.randint(1, 2)
            self.root.after(disconnect_time * 1000, self.disconnect_user, user)

        # Schedule the next simulation step
        self.root.after(4000, self.simulate)

    def connect_user(self, user):
        if "admin" in user:
            if user in self.connected_admins:
                return
            port = self.find_free_port()
            if port is not None:
                self.ports[port] = user
                self.connected_admins.add(user)
                self.update_port_label(port, user)
            else:
                self.disconnect_random_user()
                port = self.find_free_port()
                if port is not None:
                    self.ports[port] = user
                    self.connected_admins.add(user)
                    self.update_port_label(port, user)
        else:
            if user in self.connected_users:
                return
            port = self.find_free_port()
            if port is not None:
                self.ports[port] = user
                self.connected_users.add(user)
                self.update_port_label(port, user)
            else:
                self.queue.put(user)
                self.update_queue_label()

    def disconnect_user(self, user):
        for i in range(24):
            if self.ports[i] == user:
                self.ports[i] = None
                self.update_port_label(i, None)
                if "admin" in user:
                    self.connected_admins.remove(user)
                else:
                    self.connected_users.remove(user)
                wait_time = random.randint(0, 10) * 1000
                self.root.after(wait_time, self.add_to_queue, user)
                self.root.after(1000, self.check_queue)
                if "admin" in user:
                    self.ensure_admin_connected()
                break

    def add_to_queue(self, user):
        if user not in self.queue.queue:
            self.queue.put(user)
            self.update_queue_label()

    def disconnect_random_user(self):
        users = [i for i, user in enumerate(self.ports) if user is not None and "admin" not in user]
        if users:
            port = random.choice(users)
            disconnected_user = self.ports[port]
            self.ports[port] = None
            self.connected_users.remove(disconnected_user)
            self.update_port_label(port, None)
            self.queue.put(disconnected_user)
            self.update_queue_label()
            self.check_queue()

    def find_free_port(self):
        for i in range(24):
            if self.ports[i] is None:
                return i
        return None

    def update_port_label(self, port, user):
        if user is None:
            self.port_labels[port].config(text=f"Port {port+1}: Free", bg="grey")
        elif "admin" in user:
            self.port_labels[port].config(text=f"Port {port+1}: Admin", bg="red")
        else:
            self.port_labels[port].config(text=f"Port {port+1}: {user}", bg="green")

    def update_queue_label(self):
        queue_list = list(self.queue.queue)
        self.queue_label.config(text=f"Queue: {', '.join(queue_list)}")

    def check_queue(self):
        while not self.queue.empty():
            user = self.queue.get()
            port = self.find_free_port()
            if port is not None:
                self.ports[port] = user
                if "admin" in user:
                    self.connected_admins.add(user)
                else:
                    self.connected_users.add(user)
                self.update_port_label(port, user)
            else:
                self.queue.put(user)
                break
        self.update_queue_label()

    def ensure_admin_connected(self):
        admin_connected = any("admin" in user for user in self.ports if user is not None)
        if not admin_connected:
            admin = random.choice(self.admins)
            self.connect_user(admin)

if __name__ == "__main__":
    root = tk.Tk()
    app = RouterApp(root)
    root.mainloop()
