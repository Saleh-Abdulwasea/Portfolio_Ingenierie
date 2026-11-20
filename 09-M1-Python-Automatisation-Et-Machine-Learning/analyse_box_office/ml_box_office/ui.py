"""Interface graphique interactive (Tkinter + Matplotlib) pour l'analyse Box Office ML."""

from __future__ import annotations

from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional, Tuple

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd

from .anomaly import AnomalySummary, detect_box_office_anomalies, export_anomalies
from .classification import SvmBenchmarkResult, run_svm_comparison
from .preprocessing import load_and_clean_box_office


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
    "danger": "#DC2626",
    "danger_bg": "#FEE2E2",
}

AXIS_PRESETS: Dict[str, Tuple[str, str, str, str]] = {
    "Recettes mondiales vs Votes": (
        "$Worldwide",
        "Vote_Count",
        "Recettes mondiales ($Worldwide, symlog)",
        "Nombre de votes (symlog)",
    ),
    "Recettes US vs International": (
        "$Domestic",
        "$Foreign",
        "Recettes domestiques ($Domestic, symlog)",
        "Recettes internationales ($Foreign, symlog)",
    ),
    "Note vs Recettes mondiales": (
        "Rating_Num",
        "$Worldwide",
        "Note moyenne (/10)",
        "Recettes mondiales ($Worldwide, symlog)",
    ),
}


class BoxOfficeApp(tk.Tk):
    """Dashboard interactif pour explorer les anomalies Box Office et les modèles ML."""

    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        self.base_dir = Path(base_dir)
        self.csv_path = self.base_dir / "data" / "box_office_2000_2024.csv"
        self.output_dir = self.base_dir / "outputs"

        self.raw_df: Optional[pd.DataFrame] = None
        self.result_df: Optional[pd.DataFrame] = None
        self.anomalies_df: Optional[pd.DataFrame] = None
        self.summary: Optional[AnomalySummary] = None
        self._is_running = False
        self._search_after_id: Optional[str] = None

        self.title("Analyse Box Office — Détection d'Anomalies ML")
        self.geometry("1220x780")
        self.minsize(1020, 680)
        self.configure(bg=COLORS["bg"])

        self._setup_styles()
        self._build_ui()

        if self.csv_path.is_file():
            self.after(100, self.run_analysis)

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 7), font=("Helvetica", 10, "bold"))
        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#FFFFFF",
            font=("Helvetica", 10, "bold"),
            padding=(12, 6),
            borderwidth=0,
        )
        style.map("Accent.TButton", background=[("active", COLORS["accent_hover"])])
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
            rowheight=26,
            font=("Helvetica", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#F8FAFC",
            foreground=COLORS["text"],
            font=("Helvetica", 10, "bold"),
        )

    def _build_ui(self) -> None:
        self._build_header()

        container = tk.Frame(self, bg=COLORS["bg"], padx=16, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        self._build_kpi_bar(container)
        self._build_controls_bar(container)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self._build_charts_tab()
        self._build_table_tab()
        self._build_svm_tab()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=COLORS["header"], padx=20, pady=12)
        header.pack(fill=tk.X)

        left = tk.Frame(header, bg=COLORS["header"])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            left,
            text="Analyse Box Office — Détection d'Anomalies (Isolation Forest)",
            bg=COLORS["header"],
            fg="#FFFFFF",
            font=("Helvetica", 15, "bold"),
        ).pack(anchor=tk.W)
        self.lbl_csv = tk.Label(
            left,
            text=f"Dataset : {self.csv_path.name}",
            bg=COLORS["header"],
            fg=COLORS["header_sub"],
            font=("Helvetica", 10),
        )
        self.lbl_csv.pack(anchor=tk.W)

        right = tk.Frame(header, bg=COLORS["header"])
        right.pack(side=tk.RIGHT)
        ttk.Button(
            right, text="Choisir CSV…", style="Secondary.TButton", command=self._choose_csv
        ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            right, text="Exporter Anomalies", style="Secondary.TButton", command=self._export_csv
        ).pack(side=tk.LEFT, padx=(0, 8))
        self.btn_run = ttk.Button(
            right, text="Recalculer ML", style="Accent.TButton", command=self.run_analysis
        )
        self.btn_run.pack(side=tk.LEFT)

    def _build_kpi_bar(self, parent: tk.Frame) -> None:
        kpi_frame = tk.Frame(parent, bg=COLORS["bg"])
        kpi_frame.pack(fill=tk.X, pady=(0, 10))
        for col in range(4):
            kpi_frame.columnconfigure(col, weight=1, uniform="kpi")

        self.kpi_total = self._make_kpi(kpi_frame, 0, "Films analysés", "—", COLORS["text"])
        self.kpi_norm = self._make_kpi(kpi_frame, 1, "Films normaux", "—", COLORS["accent"])
        self.kpi_anom = self._make_kpi(kpi_frame, 2, "Anomalies détectées", "—", COLORS["danger"])
        self.kpi_top = self._make_kpi(kpi_frame, 3, "Film le plus atypique", "—", COLORS["success"])

    def _make_kpi(
        self, parent: tk.Frame, col: int, title: str, value: str, color: str
    ) -> tk.Label:
        padx = (0, 10) if col < 3 else (0, 0)
        card = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=8,
        )
        card.grid(row=0, column=col, sticky="ew", padx=padx)
        tk.Label(card, text=title, bg=COLORS["card"], fg=COLORS["muted"], font=("Helvetica", 10)).pack(
            anchor=tk.W
        )
        lbl = tk.Label(card, text=value, bg=COLORS["card"], fg=color, font=("Helvetica", 16, "bold"))
        lbl.pack(anchor=tk.W, pady=(2, 0))
        return lbl

    def _build_controls_bar(self, parent: tk.Frame) -> None:
        bar = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=8,
        )
        bar.pack(fill=tk.X)

        tk.Label(
            bar, text="Taux de contamination :", bg=COLORS["card"], fg=COLORS["text"], font=("Helvetica", 10, "bold")
        ).pack(side=tk.LEFT)
        self.var_contam = tk.DoubleVar(value=0.05)
        self.lbl_contam_val = tk.Label(
            bar, text="5.0 %", bg=COLORS["card"], fg=COLORS["accent"], font=("Helvetica", 10, "bold"), width=6
        )
        self.lbl_contam_val.pack(side=tk.LEFT, padx=(4, 6))

        scale = ttk.Scale(
            bar,
            from_=0.01,
            to=0.20,
            variable=self.var_contam,
            orient=tk.HORIZONTAL,
            length=180,
            command=self._on_slider_move,
        )
        scale.pack(side=tk.LEFT, padx=(0, 18))

        tk.Label(
            bar, text="Axes du graphique :", bg=COLORS["card"], fg=COLORS["text"], font=("Helvetica", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 6))
        self.var_axes = tk.StringVar(value="Recettes mondiales vs Votes")
        combo = ttk.Combobox(
            bar,
            textvariable=self.var_axes,
            values=list(AXIS_PRESETS.keys()),
            state="readonly",
            width=28,
        )
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", lambda *_: self._draw_anomaly_charts())

    def _build_charts_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg=COLORS["card"])
        self.notebook.add(tab, text="Graphiques Isolation Forest")

        self.fig_anom = Figure(figsize=(11, 4.8), dpi=100)
        self.canvas_anom = FigureCanvasTkAgg(self.fig_anom, master=tab)
        toolbar = NavigationToolbar2Tk(self.canvas_anom, tab)
        toolbar.update()
        self.canvas_anom.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_table_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg=COLORS["card"], padx=12, pady=12)
        self.notebook.add(tab, text="Explorateur des Films")
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        top = tk.Frame(tab, bg=COLORS["card"])
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        tk.Label(top, text="Rechercher un film :", bg=COLORS["card"], fg=COLORS["muted"]).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *_: self._on_search_change())
        ttk.Entry(top, textvariable=self.var_search, width=32).pack(side=tk.LEFT, padx=(0, 16))

        self.var_only_anom = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top,
            text="Afficher uniquement les anomalies",
            variable=self.var_only_anom,
            command=self._populate_table,
        ).pack(side=tk.LEFT)

        wrap = tk.Frame(tab, bg=COLORS["card"])
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        cols = ("titre", "annee", "genres", "worldwide", "votes", "note", "score", "statut")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings")
        headers = {
            "titre": ("Film", 220, tk.W),
            "annee": ("Année", 65, tk.CENTER),
            "genres": ("Genres", 180, tk.W),
            "worldwide": ("Recettes ($)", 125, tk.E),
            "votes": ("Votes", 80, tk.E),
            "note": ("Note", 70, tk.CENTER),
            "score": ("Score ML", 85, tk.E),
            "statut": ("Statut", 90, tk.CENTER),
        }
        for key, (label, width, anchor) in headers.items():
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor=anchor)

        self.tree.tag_configure("anomaly", background=COLORS["danger_bg"], foreground=COLORS["danger"])
        self.tree.tag_configure("normal", background="#FFFFFF", foreground=COLORS["text"])

        sb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

    def _build_svm_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg=COLORS["card"], padx=12, pady=12)
        self.notebook.add(tab, text="Comparaison SVM (Linear vs RBF)")

        ctrl = tk.Frame(tab, bg=COLORS["card"])
        ctrl.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(
            ctrl,
            text="Lancer / Régénérer comparaison SVM",
            style="Accent.TButton",
            command=self._run_svm_tab,
        ).pack(side=tk.LEFT)
        self.lbl_svm_info = tk.Label(
            ctrl,
            text="Cliquez pour comparer SVC(kernel='linear') et SVC(kernel='rbf').",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=("Helvetica", 10),
        )
        self.lbl_svm_info.pack(side=tk.LEFT, padx=(12, 0))

        self.fig_svm = Figure(figsize=(11, 4.6), dpi=100)
        self.canvas_svm = FigureCanvasTkAgg(self.fig_svm, master=tab)
        self.canvas_svm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_status_bar(self) -> None:
        self.var_status = tk.StringVar(value="Prêt.")
        tk.Label(
            self,
            textvariable=self.var_status,
            bg="#E2E8F0",
            fg=COLORS["text"],
            anchor=tk.W,
            padx=16,
            pady=6,
            font=("Helvetica", 9),
        ).pack(fill=tk.X, side=tk.BOTTOM)

    def _on_slider_move(self, value: str) -> None:
        self.lbl_contam_val.config(text=f"{float(value) * 100:.1f} %")

    def _choose_csv(self) -> None:
        selected = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV Box Office",
            initialdir=str(self.base_dir),
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
        )
        if selected:
            self.csv_path = Path(selected)
            self.raw_df = None
            self.lbl_csv.config(text=f"Dataset : {self.csv_path.name}")
            self.run_analysis()

    def run_analysis(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self.btn_run.config(state=tk.DISABLED)
        contam = round(self.var_contam.get(), 3)
        self.var_status.set(f"Calcul Isolation Forest en cours (contamination={contam:.1%})…")

        threading.Thread(
            target=self._analysis_worker,
            args=(contam,),
            daemon=True,
        ).start()

    def _analysis_worker(self, contam: float) -> None:
        try:
            if self.raw_df is None:
                self.raw_df = load_and_clean_box_office(self.csv_path)
            res_df, anom_df, summary = detect_box_office_anomalies(
                self.raw_df, contamination=contam
            )
            self.after(0, lambda: self._on_analysis_done(res_df, anom_df, summary))
        except Exception as exc:
            msg = str(exc)
            self.after(0, lambda: self._on_analysis_error(msg))

    def _on_analysis_done(
        self, res_df: pd.DataFrame, anom_df: pd.DataFrame, summary: AnomalySummary
    ) -> None:
        self._is_running = False
        self.btn_run.config(state=tk.NORMAL)
        self.result_df = res_df
        self.anomalies_df = anom_df
        self.summary = summary

        self.kpi_total.config(text=f"{summary.total_movies:,}".replace(",", " "))
        self.kpi_norm.config(text=f"{summary.normal_count:,}".replace(",", " "))
        self.kpi_anom.config(text=f"{summary.anomaly_count:,}".replace(",", " "))
        top_title = str(anom_df.iloc[0].get("Release Group", "—"))[:24] if not anom_df.empty else "—"
        self.kpi_top.config(text=top_title)

        self._draw_anomaly_charts()
        self._populate_table()
        self.var_status.set(
            f"Analyse terminée : {summary.anomaly_count} anomalies détectées sur {summary.total_movies} films."
        )

    def _on_analysis_error(self, msg: str) -> None:
        self._is_running = False
        self.btn_run.config(state=tk.NORMAL)
        self.var_status.set(f"Erreur : {msg}")
        messagebox.showerror("Erreur d'analyse", msg)

    def _draw_anomaly_charts(self) -> None:
        if self.result_df is None:
            return
        self.fig_anom.clear()
        ax1 = self.fig_anom.add_subplot(1, 2, 1)
        ax2 = self.fig_anom.add_subplot(1, 2, 2)

        x_col, y_col, x_lbl, y_lbl = AXIS_PRESETS[self.var_axes.get()]
        df = self.result_df
        normales = df[~df["is_anomaly"]]
        anomalies = df[df["is_anomaly"]].sort_values("anomaly_score", ascending=True)

        ax1.scatter(normales[x_col], normales[y_col], alpha=0.4, s=16, c="#2563EB", label=f"Normaux ({len(normales)})")
        ax1.scatter(anomalies[x_col], anomalies[y_col], alpha=0.85, s=30, c="#DC2626", label=f"Anomalies ({len(anomalies)})")

        offsets = [(8, 8), (-95, 14), (-110, -14), (8, -12), (-95, -26)]
        for idx, (_, row) in enumerate(anomalies.head(5).iterrows()):
            if pd.isna(row[x_col]) or pd.isna(row[y_col]):
                continue
            dx, dy = offsets[idx % len(offsets)]
            ax1.annotate(
                str(row.get("Release Group", ""))[:20],
                (row[x_col], row[y_col]),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=8,
                color="#991B1B",
                arrowprops={"arrowstyle": "-", "color": "#991B1B", "alpha": 0.5, "lw": 0.8},
            )

        if "$" in x_col:
            ax1.set_xscale("symlog", linthresh=1e5)
        if "$" in y_col:
            ax1.set_yscale("symlog", linthresh=1e5)
        elif y_col == "Vote_Count":
            ax1.set_yscale("symlog", linthresh=10)

        ax1.set_xlabel(x_lbl)
        ax1.set_ylabel(y_lbl)
        ax1.set_title("Nuage de points des films")
        ax1.legend()
        ax1.grid(alpha=0.25)

        ax2.hist(normales["anomaly_score"], bins=35, alpha=0.75, color="#2563EB", label="Normaux")
        ax2.hist(anomalies["anomaly_score"], bins=20, alpha=0.85, color="#DC2626", label="Anomalies")
        ax2.axvline(0.0, color="#0F172A", linestyle="--", linewidth=1.2, label="Seuil (0.0)")
        ax2.set_xlabel("Score d'anomalie (decision_function)")
        ax2.set_ylabel("Nombre de films")
        ax2.set_title("Distribution des scores")
        ax2.legend()
        ax2.grid(alpha=0.25)

        self.fig_anom.tight_layout()
        self.canvas_anom.draw()

    def _on_search_change(self) -> None:
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(150, self._populate_table)

    def _populate_table(self) -> None:
        self._search_after_id = None
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        if self.result_df is None:
            return

        df = self.result_df.sort_values("anomaly_score", ascending=True)
        if self.var_only_anom.get():
            df = df[df["is_anomaly"]]

        query = self.var_search.get().strip().lower()
        if query and "Release Group" in df.columns:
            df = df[df["Release Group"].astype(str).str.lower().str.contains(query, na=False)]

        for _, row in df.head(500).iterrows():
            is_anom = bool(row["is_anomaly"])
            worldwide = f"{row['$Worldwide']:,.0f}".replace(",", " ") if pd.notna(row["$Worldwide"]) else "—"
            votes = f"{int(row['Vote_Count']):,}".replace(",", " ") if pd.notna(row["Vote_Count"]) else "—"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row.get("Release Group", "—"),
                    row.get("Year", "—"),
                    str(row.get("Genres", "—"))[:28],
                    worldwide,
                    votes,
                    row.get("Rating", "—"),
                    f"{row['anomaly_score']:.4f}",
                    "Anomalie" if is_anom else "Normal",
                ),
                tags=("anomaly" if is_anom else "normal",),
            )

    def _export_csv(self) -> None:
        if self.anomalies_df is None or self.anomalies_df.empty:
            messagebox.showinfo("Export", "Aucune anomalie à exporter.")
            return
        out = export_anomalies(self.anomalies_df, self.output_dir / "anomalies_box_office.csv")
        self.var_status.set(f"Anomalies exportées dans {out}")
        messagebox.showinfo("Export réussi", f"Fichier enregistré :\n{out}")

    def _run_svm_tab(self) -> None:
        import numpy as np

        X, y, results = run_svm_comparison()
        self.fig_svm.clear()

        xx, yy = np.meshgrid(
            np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 140),
            np.linspace(X[:, 1].min() - 0.5, X[:, 1].max() + 0.5, 140),
        )
        grid = np.c_[xx.ravel(), yy.ravel()]

        summary_parts = []
        for idx, (kernel, res) in enumerate(results.items(), start=1):
            ax = self.fig_svm.add_subplot(1, len(results), idx)
            Z = res.pipeline.predict(grid).reshape(xx.shape)
            ax.contourf(xx, yy, Z, alpha=0.35, levels=[-0.5, 0.5, 1.5], colors=["#93C5FD", "#FCA5A5"])
            ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1D4ED8", s=20, label="Classe 0")
            ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#B91C1C", s=20, label="Classe 1")
            ax.set_title(f"SVC (kernel='{kernel}') — Précision : {res.accuracy:.1%}")
            ax.set_xlabel("Feature 1")
            ax.set_ylabel("Feature 2")
            ax.legend()
            ax.grid(alpha=0.2)
            summary_parts.append(f"{kernel}: {res.accuracy:.1%}")

        self.lbl_svm_info.config(text="Précision test — " + " | ".join(summary_parts))
        self.fig_svm.tight_layout()
        self.canvas_svm.draw()


def launch_gui(base_dir: Path) -> None:
    """Lance le dashboard interactif Box Office."""
    app = BoxOfficeApp(base_dir=base_dir)
    app.mainloop()
