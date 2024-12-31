import tkinter as tk
from tkinter import messagebox, ttk
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

class MailClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Mail Client")
        self.login_screen()

    def login_screen(self):
        self.clear_screen()

        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(self.root, text="Email:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.email_var).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.root, text="Password:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        self.email = self.email_var.get()
        self.password = self.password_var.get()

        try:
            self.smtp_server = smtplib.SMTP_SSL("mailserver", 465)
            self.smtp_server.login(self.email, self.password)

            self.imap_server = imaplib.IMAP4_SSL("mailserver")
            self.imap_server.login(self.email, self.password)

            self.main_screen()
        except Exception as e:
            messagebox.showerror("Login Error", str(e))

    def main_screen(self):
        self.clear_screen()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_send = ttk.Frame(self.notebook)
        self.frame_inbox = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_send, text="Send Email")
        self.notebook.add(self.frame_inbox, text="Inbox")

        self.send_email_screen()
        self.inbox_screen()

    def send_email_screen(self):
        self.recipient_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.body_var = tk.StringVar()

        tk.Label(self.frame_send, text="To:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.frame_send, textvariable=self.recipient_var).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.frame_send, text="Subject:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self.frame_send, textvariable=self.subject_var).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.frame_send, text="Body:").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(self.frame_send, textvariable=self.body_var).grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.frame_send, text="Send", command=self.send_email).grid(row=3, column=0, columnspan=2, pady=10)

    def send_email(self):
        recipient = self.recipient_var.get()
        subject = self.subject_var.get()
        body = self.body_var.get()

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            self.smtp_server.sendmail(self.email, recipient, msg.as_string())
            messagebox.showinfo("Success", "Email sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def inbox_screen(self):
        self.tree = ttk.Treeview(self.frame_inbox, columns=("From", "Subject", "Date"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("From", text="From")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Date", text="Date")

        self.tree.column("#0", width=30)
        self.tree.column("From", width=150)
        self.tree.column("Subject", width=200)
        self.tree.column("Date", width=100)

        self.tree.grid(row=0, column=0, padx=10, pady=10)
        self.fetch_emails()

    def fetch_emails(self):
        self.imap_server.select("inbox")
        status, messages = self.imap_server.search(None, 'ALL')
        mail_ids = messages[0].split()

        for i, mail_id in enumerate(mail_ids):
            status, data = self.imap_server.fetch(mail_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            subject = email.header.decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            from_ = msg.get("From")
            date = msg.get("Date")

            self.tree.insert("", "end", text=i + 1, values=(from_, subject, date))

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MailClient(root)
    root.mainloop()
