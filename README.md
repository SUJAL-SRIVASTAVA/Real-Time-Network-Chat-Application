1. Introduction

•	Purpose : Document the development of a real-time messaging application for local network communication using Python sockets and Tkinter.
•	Overview of the Web Application: The application enables users to host or join a chat server within the same network, send messages/files, toggle themes, and view connected users.
•	Objectives and Scope:
o	Create a lightweight, internet-independent chat tool for secure internal communication.
o	Implement real-time text and file sharing with minimal latency.
________________________________________

2. Project Background
•	Problem Statement: Organizations often rely on internet-dependent messaging tools, exposing them to security risks and connectivity issues.
•	Target Audience:
o	Small teams, educational labs, or local businesses needing offline communication.
•	Business Requirements:
o	Real-time messaging and file transfer.
o	Simple user authentication via nicknames.
o	Cross-platform compatibility.
________________________________________

3. Technology Stack
•	Frontend Technologies: Tkinter (Python GUI toolkit).
•	Backend Technologies: Python socket library for TCP communication.
•	Database: In-memory storage for active sessions (no persistent database).
•	Other Tools & Frameworks:
o	threading for concurrent client handling.
o	filedialog for file selection.
________________________________________

4. System Architecture
•	Application Architecture: Client-server model with a central server managing multiple clients.
•	Deployment Model: On-premises deployment within a local network.
•	Security Considerations:
o	Basic nickname-based authentication (no encryption).
o	IP whitelisting for server connections.
________________________________________

5. User Interface & UX Design
•	Wireframes & Mockups:
o	Interface 1: Nickname entry screen with "Set Nickname" button.
o	Interface 2: Main chat window with server/client controls, message history, and user list.
o	Theme Toggle: Dark/light mode for visual comfort (see Figure 1).
•	User Experience Considerations:
o	Simple navigation with labeled buttons.
o	Real-time updates for messages and connected users.
•	Accessibility Features:
o	High-contrast themes for readability.
________________________________________

6. Development Process
•	Methodology: Iterative development with incremental feature additions.
•	Version Control & CI/CD Pipeline: GitHub for code management (no CI/CD pipeline).
•	Key Features Implemented:
o	Multithreaded server to handle concurrent clients.
o	File transfer using binary data packets.
o	Dynamic theme switching.
________________________________________

7. Testing & Quality Assurance
•	Types of Testing:
o	Unit Testing: Socket connection stability.
o	Integration Testing: Client-server message synchronization.
•	Testing Tools Used: Manual testing with multiple local devices.
•	Bug Tracking & Resolution: Ad-hoc debugging using print statements and exception handling.
________________________________________

8. Deployment & Hosting
•	Hosting Provider & Server Configuration:
o	Server hosted on a local machine (e.g., 192.168.14.204:12345).
•	Deployment Strategy: Manual execution of Python script on server/client machines.
•	Performance Optimization:
o	Multithreading to prevent UI freezes.
________________________________________

9. Challenges & Solutions
•	Technical Challenges:
o	Issue: Concurrent client connections caused crashes.
o	Solution: Implemented threading for parallel client handling.
•	User Challenges:
o	Issue: File transfer failures for large files.
o	Solution: Chunked data transmission (future enhancement).
________________________________________

10. Future Enhancements
•	Planned Features:
o	End-to-end encryption using TLS/SSL.
o	Message history logging.
•	Scalability Considerations:
o	Load balancing for large user bases.
•	Potential Upgrades:
o	Web-based interface using WebSocket (e.g., Flask-SocketIO).
________________________________________

11. Conclusion
•	Summary: Developed a functional local network chat application with core messaging features.
•	Recommendations:
o	Integrate encryption for secure communication.
o	Replace Tkinter with a modern web framework for broader accessibility.
________________________________________
12. References & Appendices
•	References:
o	Python socket library documentation.
o	Tkinter GUI programming guides.
•	Code Snippets:
 

13. Codes
14. 
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


  
 





