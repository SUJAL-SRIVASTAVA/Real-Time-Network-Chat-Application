import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import os

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Chat App")
        self.root.geometry("600x500")
        
        self.nickname = None
        self.clients = {}
        
        # Theme
        self.dark_mode = False
        
        # Nickname Entry
        self.nick_label = tk.Label(root, text="Enter Nickname:")
        self.nick_label.pack()
        self.nick_entry = tk.Entry(root)
        self.nick_entry.pack()
        self.nick_button = tk.Button(root, text="Set Nickname", command=self.set_nickname)
        self.nick_button.pack()
        
        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15, state='disabled')
        self.chat_display.pack(pady=10)
        
        # Message Entry
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        
        self.server_button = tk.Button(btn_frame, text="Start Server", command=self.start_server, bg="green", fg="white")
        self.server_button.grid(row=0, column=0, padx=5)
        
        self.client_button = tk.Button(btn_frame, text="Connect Client", command=self.start_client, bg="blue", fg="white")
        self.client_button.grid(row=0, column=1, padx=5)
        
        self.send_button = tk.Button(root, text="Send Message", command=self.send_message, bg="purple", fg="white")
        self.send_button.pack(pady=5)
        
        self.file_button = tk.Button(root, text="Send File", command=self.send_file, bg="orange", fg="white")
        self.file_button.pack(pady=5)
        
        self.theme_button = tk.Button(root, text="Toggle Theme", command=self.toggle_theme, bg="gray", fg="white")
        self.theme_button.pack(pady=5)
        
        # User List
        self.user_list_label = tk.Label(root, text="Connected Users:")
        self.user_list_label.pack()
        self.user_list = tk.Listbox(root, height=5)
        self.user_list.pack()
        
        # Network Variables
        self.server = None
        self.client = None
        self.port = 12345
        self.server_ip = "192.168.14.204"  # Change this to your actual server IP
        
    def set_nickname(self):
        self.nickname = self.nick_entry.get()
        if self.nickname:
            self.nick_label.pack_forget()
            self.nick_entry.pack_forget()
            self.nick_button.pack_forget()
        else:
            messagebox.showerror("Error", "Nickname cannot be empty")
        
    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", self.port))
        self.server.listen(5)
        threading.Thread(target=self.accept_clients, daemon=True).start()
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "Server started. Waiting for connections...\n")
        self.chat_display.config(state='disabled')
    
    def accept_clients(self):
        while True:
            client_socket, addr = self.server.accept()
            self.clients[client_socket] = addr
            threading.Thread(target=self.receive_messages, args=(client_socket, addr), daemon=True).start()
            self.user_list.insert(tk.END, f"{addr}")
            
    def start_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.server_ip, self.port))
            threading.Thread(target=self.receive_messages, args=(self.client, None), daemon=True).start()
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, "Connected to server!\n")
            self.chat_display.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def receive_messages(self, client, addr):
        while True:
            try:
                message = client.recv(1024).decode()
                if not message:
                    break
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, f"{message}\n")
                self.chat_display.config(state='disabled')
            except (ConnectionResetError, ConnectionAbortedError):
                break

        if client in self.clients:
            del self.clients[client]
            self.update_user_list()
        client.close()

    def send_message(self):
        message = self.entry.get().strip()
        if not message:
            return

        formatted_msg = f"{self.nickname}: {message}"

        disconnected_clients = []
        for client in list(self.clients.keys()):
            try:
                client.sendall(formatted_msg.encode())
            except (ConnectionResetError, BrokenPipeError):
                disconnected_clients.append(client)
        
        for client in disconnected_clients:
            del self.clients[client]
            self.update_user_list()

        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"You: {message}\n")
        self.chat_display.config(state='disabled')

        self.entry.delete(0, tk.END)

    def send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as file:
                file_data = file.read()
            data_packet = f"FILE:{file_name}".encode() + b"\n" + file_data
            try:
                if self.client:
                    self.client.sendall(data_packet)
                else:
                    list(self.clients.keys())[0].sendall(data_packet)
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, f"You sent a file: {file_name}\n")
                self.chat_display.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send file: {e}")

    def update_user_list(self):
        self.user_list.delete(0, tk.END)
        for addr in self.clients.values():
            self.user_list.insert(tk.END, str(addr))

    def toggle_theme(self):
        if self.dark_mode:
            self.root.config(bg="white")
            self.chat_display.config(bg="white", fg="black")
            self.dark_mode = False
        else:
            self.root.config(bg="#2E3440")  # Aesthetic dark blue-gray background
            self.chat_display.config(bg="#3B4252", fg="#D8DEE9")  # Better contrast
            self.dark_mode = True

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
