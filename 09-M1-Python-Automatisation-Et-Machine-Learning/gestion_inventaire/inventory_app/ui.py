"""Interface graphique professionnelle (Tkinter / ttk) pour la gestion d'inventaire."""

from __future__ import annotations

import os
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from .inventory import generate_reports
from .mailer import SMTP_PRESETS, SmtpConfig, send_inventory_email
from .models import InventoryReport, StockStatus
from .scheduler import DailyScheduler


COLORS = {
    "bg": "#F1F5F9",
    "card": "#FFFFFF",
    "header": "#0F172A",
    "header_sub": "#94A3B8",
    "text": "#0F172A",
    "muted": "#64748B",
    "border": "#E2E8F0",
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "success": "#15803D",
    "success_bg": "#DCFCE7",
    "warning": "#B45309",
    "warning_bg": "#FEF3C7",
    "danger": "#B91C1C",
    "danger_bg": "#FEE2E2",
}


class InventoryApp(tk.Tk):
    """Fenêtre principale de l'application d'inventaire et de reporting."""

    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        self.base_dir = Path(base_dir)
        self.csv_path = self.base_dir / "inventaire.csv"
        self.alerts_path = self.base_dir / "produits_alertes.csv"
        self.rapport_path = self.base_dir / "rapport.txt"

        self.current_report: Optional[InventoryReport] = None
        self.scheduler = DailyScheduler(self._run_scheduled_email)
        self._is_sending = False
        self._search_after_id: Optional[str] = None

        self.title("Gestion d'Inventaire & Alertes")
        self.geometry("1040x700")
        self.minsize(900, 620)
        self.configure(bg=COLORS["bg"])

        self._setup_styles()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if self.csv_path.is_file():
            self.refresh_inventory(silent=True)

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure(
            "CardTitle.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Helvetica", 12, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted"],
            font=("Helvetica", 10),
        )
        style.configure(
            "Field.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Helvetica", 10, "bold"),
        )
        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#FFFFFF",
            font=("Helvetica", 10, "bold"),
            padding=(12, 7),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["accent_hover"]), ("disabled", "#94A3B8")],
        )
        style.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground=COLORS["text"],
            font=("Helvetica", 10),
            padding=(10, 6),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

        style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=COLORS["text"],
            rowheight=28,
            font=("Helvetica", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#F8FAFC",
            foreground=COLORS["text"],
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padding=(8, 6),
        )

    def _build_ui(self) -> None:
        self._build_header()

        main = tk.Frame(self, bg=COLORS["bg"], padx=18, pady=14)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(1, weight=1)

        self._build_kpi_bar(main)
        self._build_inventory_card(main)
        self._build_email_card(main)
        self._build_status_bar()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=COLORS["header"], padx=20, pady=14)
        header.pack(fill=tk.X)

        left = tk.Frame(header, bg=COLORS["header"])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            left,
            text="Gestion d'Inventaire & Rapports Automatisés",
            bg=COLORS["header"],
            fg="#FFFFFF",
            font=("Helvetica", 16, "bold"),
        ).pack(anchor=tk.W)
        self.lbl_csv_path = tk.Label(
            left,
            text=f"Source : {self.csv_path}",
            bg=COLORS["header"],
            fg=COLORS["header_sub"],
            font=("Helvetica", 10),
        )
        self.lbl_csv_path.pack(anchor=tk.W, pady=(2, 0))

        right = tk.Frame(header, bg=COLORS["header"])
        right.pack(side=tk.RIGHT)
        ttk.Button(
            right,
            text="Choisir CSV…",
            style="Secondary.TButton",
            command=self._choose_csv,
        ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            right,
            text="Analyser & Générer",
            style="Accent.TButton",
            command=self.refresh_inventory,
        ).pack(side=tk.LEFT)

    def _build_kpi_bar(self, parent: tk.Frame) -> None:
        kpi_frame = tk.Frame(parent, bg=COLORS["bg"])
        kpi_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        for col in range(4):
            kpi_frame.columnconfigure(col, weight=1, uniform="kpi")

        self.kpi_total = self._create_kpi_card(kpi_frame, 0, "Total produits", "0", COLORS["text"])
        self.kpi_ok = self._create_kpi_card(kpi_frame, 1, "En stock", "0", COLORS["success"])
        self.kpi_alert = self._create_kpi_card(kpi_frame, 2, "En alerte", "0", COLORS["warning"])
        self.kpi_rupture = self._create_kpi_card(kpi_frame, 3, "Ruptures", "0", COLORS["danger"])

    def _create_kpi_card(
        self, parent: tk.Frame, col: int, title: str, value: str, color: str
    ) -> tk.Label:
        padx = (0, 10) if col < 3 else (0, 0)
        card = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        card.grid(row=0, column=col, sticky="ew", padx=padx)
        tk.Label(
            card, text=title, bg=COLORS["card"], fg=COLORS["muted"], font=("Helvetica", 10)
        ).pack(anchor=tk.W)
        val_lbl = tk.Label(
            card, text=value, bg=COLORS["card"], fg=color, font=("Helvetica", 20, "bold")
        )
        val_lbl.pack(anchor=tk.W, pady=(2, 0))
        return val_lbl

    def _build_inventory_card(self, parent: tk.Frame) -> None:
        card = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=14,
        )
        card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        card.rowconfigure(2, weight=1)
        card.columnconfigure(0, weight=1)

        top = tk.Frame(card, bg=COLORS["card"])
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="État des stocks", style="CardTitle.TLabel").pack(side=tk.LEFT)

        self.var_only_alerts = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            top,
            text="Alertes uniquement",
            variable=self.var_only_alerts,
            command=self._populate_tree,
        ).pack(side=tk.RIGHT)

        search_row = tk.Frame(card, bg=COLORS["card"])
        search_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        tk.Label(
            search_row, text="Rechercher :", bg=COLORS["card"], fg=COLORS["muted"], font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=(0, 6))
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *_: self._on_search_change())
        ttk.Entry(search_row, textvariable=self.var_search).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tree_wrap = tk.Frame(card, bg=COLORS["card"])
        tree_wrap.grid(row=2, column=0, sticky="nsew")
        tree_wrap.rowconfigure(0, weight=1)
        tree_wrap.columnconfigure(0, weight=1)

        columns = ("produit", "quantite", "seuil", "statut")
        self.tree = ttk.Treeview(tree_wrap, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("produit", text="Produit")
        self.tree.heading("quantite", text="Quantité")
        self.tree.heading("seuil", text="Seuil critique")
        self.tree.heading("statut", text="Statut")

        self.tree.column("produit", width=210, anchor=tk.W)
        self.tree.column("quantite", width=85, anchor=tk.E)
        self.tree.column("seuil", width=105, anchor=tk.E)
        self.tree.column("statut", width=100, anchor=tk.CENTER)

        self.tree.tag_configure("rupture", background=COLORS["danger_bg"], foreground=COLORS["danger"])
        self.tree.tag_configure("alerte", background=COLORS["warning_bg"], foreground=COLORS["warning"])
        self.tree.tag_configure("ok", background="#FFFFFF", foreground=COLORS["text"])

        scrollbar = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_email_card(self, parent: tk.Frame) -> None:
        card = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        card.grid(row=1, column=1, sticky="nsew")
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Envoi & Planification E-mail", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        # Fournisseur SMTP
        ttk.Label(card, text="Fournisseur SMTP", style="Field.TLabel").grid(row=1, column=0, sticky="w")
        self.var_preset = tk.StringVar(value="Gmail (smtp.gmail.com)")
        preset_box = ttk.Combobox(
            card,
            textvariable=self.var_preset,
            values=list(SMTP_PRESETS.keys()),
            state="readonly",
        )
        preset_box.grid(row=2, column=0, sticky="ew", pady=(2, 8))
        preset_box.bind("<<ComboboxSelected>>", self._on_preset_change)

        host_row = tk.Frame(card, bg=COLORS["card"])
        host_row.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        host_row.columnconfigure(0, weight=3)
        host_row.columnconfigure(1, weight=1)

        self.var_host = tk.StringVar(value="smtp.gmail.com")
        self.var_port = tk.StringVar(value="587")
        self.entry_host = ttk.Entry(host_row, textvariable=self.var_host)
        self.entry_host.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entry_port = ttk.Entry(host_row, textvariable=self.var_port, width=7)
        self.entry_port.grid(row=0, column=1, sticky="ew")

        # Expéditeur
        ttk.Label(card, text="E-mail expéditeur (Gmail)", style="Field.TLabel").grid(row=4, column=0, sticky="w")
        self.var_sender = tk.StringVar(value=os.environ.get("EMAIL_EXPEDITEUR", ""))
        ttk.Entry(card, textvariable=self.var_sender).grid(row=5, column=0, sticky="ew", pady=(2, 8))

        # Mot de passe d'application
        ttk.Label(card, text="Mot de passe d'application", style="Field.TLabel").grid(row=6, column=0, sticky="w")
        pwd_row = tk.Frame(card, bg=COLORS["card"])
        pwd_row.grid(row=7, column=0, sticky="ew", pady=(2, 4))
        pwd_row.columnconfigure(0, weight=1)

        self.var_password = tk.StringVar(value=os.environ.get("EMAIL_PASSWORD", ""))
        self.entry_password = ttk.Entry(pwd_row, textvariable=self.var_password, show="•")
        self.entry_password.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._show_pwd = False
        self.btn_toggle_pwd = ttk.Button(
            pwd_row, text="Afficher", style="Secondary.TButton", command=self._toggle_password
        )
        self.btn_toggle_pwd.grid(row=0, column=1)

        self.lbl_gmail_tip = tk.Label(
            card,
            text="Astuce Gmail : utilisez un « Mot de passe d'application » Google (16 caractères).",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=("Helvetica", 9),
            wraplength=320,
            justify=tk.LEFT,
        )
        self.lbl_gmail_tip.grid(row=8, column=0, sticky="w", pady=(0, 8))

        # Destinataire
        ttk.Label(card, text="E-mail destinataire", style="Field.TLabel").grid(row=9, column=0, sticky="w")
        self.var_recipient = tk.StringVar(value=os.environ.get("EMAIL_DESTINATAIRE", ""))
        ttk.Entry(card, textvariable=self.var_recipient).grid(row=10, column=0, sticky="ew", pady=(2, 12))

        self.btn_send = ttk.Button(
            card,
            text="Envoyer le rapport maintenant",
            style="Accent.TButton",
            command=self._send_now_clicked,
        )
        self.btn_send.grid(row=11, column=0, sticky="ew", pady=(0, 14))

        # Séparateur + Planification
        ttk.Separator(card, orient=tk.HORIZONTAL).grid(row=12, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(card, text="Envoi automatique quotidien", style="Field.TLabel").grid(
            row=13, column=0, sticky="w", pady=(0, 6)
        )

        sched_row = tk.Frame(card, bg=COLORS["card"])
        sched_row.grid(row=14, column=0, sticky="ew")
        tk.Label(
            sched_row, text="Heure (HH:MM) :", bg=COLORS["card"], fg=COLORS["muted"], font=("Helvetica", 10)
        ).pack(side=tk.LEFT)
        self.var_time = tk.StringVar(value="08:00")
        ttk.Entry(sched_row, textvariable=self.var_time, width=8).pack(side=tk.LEFT, padx=(6, 10))
        self.btn_schedule = ttk.Button(
            sched_row,
            text="Activer",
            style="Secondary.TButton",
            command=self._toggle_schedule,
        )
        self.btn_schedule.pack(side=tk.RIGHT)

        self.lbl_schedule_status = tk.Label(
            card,
            text="Planification inactive.",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=("Helvetica", 9),
        )
        self.lbl_schedule_status.grid(row=15, column=0, sticky="w", pady=(6, 0))

    def _build_status_bar(self) -> None:
        self.var_status = tk.StringVar(value="Prêt.")
        bar = tk.Label(
            self,
            textvariable=self.var_status,
            bg="#E2E8F0",
            fg=COLORS["text"],
            anchor=tk.W,
            padx=16,
            pady=6,
            font=("Helvetica", 9),
        )
        bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _set_status(self, message: str) -> None:
        self.var_status.set(message)

    def _choose_csv(self) -> None:
        selected = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV d'inventaire",
            initialdir=str(self.base_dir),
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
        )
        if selected:
            self.csv_path = Path(selected)
            self.lbl_csv_path.config(text=f"Source : {self.csv_path}")
            self.refresh_inventory()

    def refresh_inventory(self, silent: bool = False) -> None:
        try:
            report, alerts_path, txt_path = generate_reports(
                self.csv_path, self.alerts_path, self.rapport_path
            )
        except Exception as exc:
            if not silent:
                messagebox.showerror("Erreur de lecture", str(exc))
            self._set_status(f"Erreur : {exc}")
            return

        self.current_report = report
        self.kpi_total.config(text=str(len(report.products)))
        self.kpi_ok.config(text=str(len(report.in_stock)))
        self.kpi_alert.config(text=str(len(report.alerts)))
        self.kpi_rupture.config(text=str(len(report.out_of_stock)))

        self._populate_tree()
        self._set_status(
            f"Rapports générés ({txt_path.name}, {alerts_path.name}) — {len(report.alerts)} alerte(s)."
        )
        if report.errors and not silent:
            messagebox.showwarning(
                "Lignes ignorées",
                "\n".join(report.errors[:10]),
            )

    def _on_search_change(self) -> None:
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(150, self._populate_tree)

    def _populate_tree(self) -> None:
        self._search_after_id = None
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        if self.current_report is None:
            return

        query = self.var_search.get().strip().lower()
        only_alerts = self.var_only_alerts.get()

        for product in self.current_report.products:
            if only_alerts and not product.is_alert:
                continue
            if query and query not in product.name.lower():
                continue

            if product.status == StockStatus.RUPTURE:
                tag = "rupture"
            elif product.status == StockStatus.ALERTE:
                tag = "alerte"
            else:
                tag = "ok"

            self.tree.insert(
                "",
                tk.END,
                values=(product.name, product.quantity, product.threshold, product.status.value),
                tags=(tag,),
            )

    def _on_preset_change(self, _event: object = None) -> None:
        preset = self.var_preset.get()
        host, port = SMTP_PRESETS.get(preset, ("", 587))
        if host:
            self.var_host.set(host)
        self.var_port.set(str(port))

    def _toggle_password(self) -> None:
        self._show_pwd = not self._show_pwd
        self.entry_password.config(show="" if self._show_pwd else "•")
        self.btn_toggle_pwd.config(text="Masquer" if self._show_pwd else "Afficher")

    def _build_smtp_config(self) -> SmtpConfig:
        try:
            port = int(self.var_port.get().strip())
        except ValueError as exc:
            raise ValueError("Le port SMTP doit être un nombre entier (ex: 587).") from exc

        return SmtpConfig(
            sender=self.var_sender.get().strip(),
            recipient=self.var_recipient.get().strip(),
            password=self.var_password.get(),
            host=self.var_host.get().strip(),
            port=port,
        )

    def _send_now_clicked(self) -> None:
        if self._is_sending:
            return
        try:
            config = self._build_smtp_config()
            if not config.sender or not config.recipient or not config.password:
                raise ValueError("Veuillez renseigner l'expéditeur, le mot de passe et le destinataire.")
        except ValueError as exc:
            messagebox.showwarning("Champs incomplets", str(exc))
            return

        if self.current_report is None and self.csv_path.is_file():
            self.refresh_inventory(silent=True)

        self._is_sending = True
        self.btn_send.config(state=tk.DISABLED)
        self._set_status(f"Envoi de l'e-mail via {config.host}…")

        thread = threading.Thread(
            target=self._send_email_worker,
            args=(config, True),
            daemon=True,
        )
        thread.start()

    def _send_email_worker(self, config: SmtpConfig, interactive: bool) -> None:
        try:
            send_inventory_email(
                config=config,
                report=self.current_report,
                attachments=[self.rapport_path, self.alerts_path],
            )
            self.after(0, lambda: self._on_send_success(config.recipient, interactive))
        except Exception as exc:
            msg = str(exc)
            self.after(0, lambda: self._on_send_error(msg, interactive))

    def _on_send_success(self, recipient: str, interactive: bool) -> None:
        self._is_sending = False
        self.btn_send.config(state=tk.NORMAL)
        self._set_status(f"E-mail envoyé avec succès à {recipient}.")
        if interactive:
            messagebox.showinfo("Succès", f"Rapport envoyé avec succès à {recipient} !")

    def _on_send_error(self, error_msg: str, interactive: bool) -> None:
        self._is_sending = False
        self.btn_send.config(state=tk.NORMAL)
        self._set_status(f"Échec d'envoi : {error_msg}")
        if interactive:
            messagebox.showerror("Erreur d'envoi", error_msg)

    def _toggle_schedule(self) -> None:
        if self.scheduler.is_running:
            self.scheduler.stop()
            self.btn_schedule.config(text="Activer")
            self.lbl_schedule_status.config(text="Planification inactive.", fg=COLORS["muted"])
            self._set_status("Planification arrêtée.")
            return

        try:
            config = self._build_smtp_config()
            if not config.sender or not config.recipient or not config.password:
                raise ValueError("Remplissez d'abord les informations e-mail avant d'activer la planification.")
            next_run = self.scheduler.start(self.var_time.get())
        except ValueError as exc:
            messagebox.showwarning("Planification impossible", str(exc))
            return

        self.btn_schedule.config(text="Désactiver")
        next_str = next_run.strftime("%d/%m à %H:%M")
        self.lbl_schedule_status.config(
            text=f"Actif — prochain envoi le {next_str}.", fg=COLORS["success"]
        )
        self._set_status(f"Envoi quotidien planifié à {self.var_time.get().strip()}.")

    def _run_scheduled_email(self) -> None:
        def trigger() -> None:
            if self.csv_path.is_file():
                self.refresh_inventory(silent=True)
            try:
                config = self._build_smtp_config()
            except ValueError:
                return
            threading.Thread(
                target=self._send_email_worker,
                args=(config, False),
                daemon=True,
            ).start()

        self.after(0, trigger)

    def _on_close(self) -> None:
        self.scheduler.stop()
        self.destroy()


def launch_gui(base_dir: Path) -> None:
    """Lance l'interface graphique."""
    app = InventoryApp(base_dir=base_dir)
    app.mainloop()
