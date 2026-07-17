"""
QuBit Guard — Interactive BB84 Quantum Key Distribution Simulator
Modern light-themed desktop app using CustomTkinter.
"""
import customtkinter as ctk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from bb84 import run_bb84
from polarization import icon_for, color_for

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- Palette ----------
BG = "#f4f6fb"
CARD = "#ffffff"
ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
PURPLE = "#8b5cf6"
PURPLE_HOVER = "#7c3aed"
CYAN = "#06b6d4"
CYAN_HOVER = "#0891b2"
TEXT = "#111827"
SUBTEXT = "#6b7280"
GREEN = "#16a34a"
GREEN_LIGHT = "#dcfce7"
RED = "#dc2626"
RED_LIGHT = "#fee2e2"
YELLOW_LIGHT = "#fef9c3"
GRAY_LIGHT = "#f3f4f6"


class QuBitGuardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuBit Guard — BB84 Quantum Key Distribution Simulator")
        self.geometry("1300x860")
        self.configure(fg_color=BG)
        self.minsize(1100, 720)

        self.result = None
        self.step_index = 0
        self.history = []

        self._style_treeview()
        self._build_header()

        self.tabs = ctk.CTkTabview(self, fg_color=CARD, segmented_button_selected_color=ACCENT,
                                     segmented_button_selected_hover_color=ACCENT_HOVER,
                                     segmented_button_unselected_color="#e5e7eb",
                                     text_color=TEXT, corner_radius=14)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tabs.add("⚛  Simulator")
        self.tabs.add("📘  Learn")
        self.tabs.add("📊  History")

        self._build_simulator_tab(self.tabs.tab("⚛  Simulator"))
        self._build_learn_tab(self.tabs.tab("📘  Learn"))
        self._build_history_tab(self.tabs.tab("📊  History"))

    # ---------- ttk styling for Treeview (used inside CTk frames) ----------
    def _style_treeview(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=CARD, fieldbackground=CARD, foreground=TEXT,
                         rowheight=28, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Custom.Treeview.Heading",
                         background="#eef2ff", foreground=TEXT,
                         font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Custom.Treeview.Heading", background=[("active", "#e0e7ff")])

    # ================= HEADER =================
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(22, 10))

        ctk.CTkLabel(header, text="🔐  QuBit Guard", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="An interactive playground for the BB84 Quantum Key Distribution protocol.",
                      font=ctk.CTkFont(size=13), text_color=SUBTEXT).pack(anchor="w", pady=(2, 0))

    # ================= SIMULATOR TAB =================
    def _build_simulator_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        # ---- Controls card ----
        controls = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        controls.pack(fill="x", pady=(15, 12))
        row = ctk.CTkFrame(controls, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(row, text="Qubits:", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).grid(row=0, column=0, padx=(0, 8))
        self.n_var = ctk.IntVar(value=12)
        ctk.CTkEntry(row, textvariable=self.n_var, width=60, corner_radius=8).grid(row=0, column=1, padx=(0, 20))

        self.eve_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(row, text="😈  Enable Eve", variable=self.eve_var, text_color=TEXT,
                          font=ctk.CTkFont(size=13, weight="bold"), corner_radius=6,
                          fg_color=RED, hover_color="#b91c1c").grid(row=0, column=2, padx=(0, 25))

        self.run_btn = ctk.CTkButton(row, text="▶  Run Animated Simulation", command=self.start_full_run,
                                       fg_color=ACCENT, hover_color=ACCENT_HOVER, corner_radius=10,
                                       font=ctk.CTkFont(size=13, weight="bold"), height=38)
        self.run_btn.grid(row=0, column=3, padx=(0, 10))

        self.step_btn = ctk.CTkButton(row, text="⏭  Step-by-Step", command=self.start_step_mode,
                                        fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=10,
                                        font=ctk.CTkFont(size=13, weight="bold"), height=38)
        self.step_btn.grid(row=0, column=4, padx=(0, 10))

        self.next_btn = ctk.CTkButton(row, text="Next ▶", command=self.reveal_next, state="disabled",
                                        fg_color=CYAN, hover_color=CYAN_HOVER, corner_radius=10,
                                        font=ctk.CTkFont(size=13, weight="bold"), height=38)
        self.next_btn.grid(row=0, column=5)

        # ---- Photon channel ----
        channel_card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        channel_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(channel_card, text="Quantum Channel", font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=TEXT).pack(anchor="w", padx=18, pady=(14, 0))
        self.channel_canvas = ctk.CTkCanvas(channel_card, height=170, bg="#fbfbfd", highlightthickness=0)
        self.channel_canvas.pack(fill="x", padx=18, pady=14)
        self.after(100, self._draw_channel_labels)

        # ---- Split area ----
        split = ctk.CTkFrame(parent, fg_color="transparent")
        split.pack(fill="both", expand=True)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=2)
        split.grid_rowconfigure(0, weight=1)

        # Left: table
        left = ctk.CTkFrame(split, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="Basis Comparison Table", font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=TEXT).pack(anchor="w", padx=18, pady=(14, 8))

        table_frame = ctk.CTkFrame(left, fg_color=CARD)
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        columns = ("idx", "abit", "abasis", "ebasis", "bbasis", "match", "bbit", "inkey")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, style="Custom.Treeview")
        headers = ["#", "Alice Bit", "Alice Basis", "Eve Basis", "Bob Basis", "Match?", "Bob Bit", "In Key"]
        widths = [35, 70, 95, 85, 90, 65, 65, 65]
        for c, h, w in zip(columns, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        self.tree.tag_configure("match", background=GREEN_LIGHT)
        self.tree.tag_configure("mismatch", background=RED_LIGHT)
        self.tree.tag_configure("nomatch", background=GRAY_LIGHT)
        self.tree.tag_configure("eve", background=YELLOW_LIGHT)
        self.tree.pack(fill="both", expand=True)

        # Right: status + key + chart
        right = ctk.CTkFrame(split, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.status_card = ctk.CTkFrame(right, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        self.status_card.pack(fill="x", pady=(0, 10))
        self.status_label = ctk.CTkLabel(self.status_card, text="Status: waiting for run…",
                                           font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT)
        self.status_label.pack(pady=16)

        self.key_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11, family="Consolas"),
                                        text_color=TEXT, justify="left", anchor="w", wraplength=430)
        self.key_label.pack(fill="x", pady=(0, 10))

        chart_card = ctk.CTkFrame(right, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        chart_card.pack(fill="both", expand=True)
        self.fig = Figure(figsize=(4.3, 3), dpi=100, facecolor=CARD)
        self.ax = self.fig.add_subplot(111)
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas_chart.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)
        self._draw_empty_chart()

    def _draw_channel_labels(self):
        c = self.channel_canvas
        c.delete("labels")
        w = max(c.winfo_width(), 900)
        c.create_text(65, 20, text="👩 Alice", font=("Segoe UI", 12, "bold"), fill=TEXT, tags="labels")
        c.create_text(w // 2, 20, text="😈 Eve", font=("Segoe UI", 12, "bold"), fill=RED, tags="labels")
        c.create_text(w - 65, 20, text="👨 Bob", font=("Segoe UI", 12, "bold"), fill=TEXT, tags="labels")
        c.create_line(35, 95, w - 35, 95, fill="#d8dce8", dash=(4, 3), width=2, tags="labels")

    def _draw_empty_chart(self):
        self.ax.clear()
        self.ax.set_facecolor(CARD)
        self.fig.patch.set_facecolor(CARD)
        self.ax.set_title("Error Rate", fontsize=11, color=TEXT)
        self.ax.set_ylim(0, 100)
        for spine in self.ax.spines.values():
            spine.set_color("#e5e7eb")
        self.canvas_chart.draw()

    # ---------- Simulation control ----------
    def start_full_run(self):
        self._reset_run(auto=True)

    def start_step_mode(self):
        self._reset_run(auto=False)

    def _reset_run(self, auto):
        try:
            n = int(self.n_var.get())
        except Exception:
            n = 12
        n = max(4, min(60, n))
        eve_present = bool(self.eve_var.get())

        self.result = run_bb84(n=n, eve_present=eve_present)
        self.step_index = 0
        self.tree.delete(*self.tree.get_children())
        self.status_label.configure(text="Status: running…", text_color=TEXT)
        self.key_label.configure(text="")
        self._draw_channel_labels()
        self.next_btn.configure(state="disabled" if auto else "normal")
        self.run_btn.configure(state="disabled")
        self.step_btn.configure(state="disabled")

        if auto:
            self._auto_step()

    def reveal_next(self):
        if not self.result or self.step_index >= self.result["n"]:
            return
        self._reveal_qubit(self.step_index)
        self.step_index += 1
        if self.step_index >= self.result["n"]:
            self.next_btn.configure(state="disabled")
            self._finish_run()

    def _auto_step(self):
        if not self.result or self.step_index >= self.result["n"]:
            self._finish_run()
            return
        self._reveal_qubit(self.step_index)
        self.step_index += 1
        self.after(280, self._auto_step)

    def _finish_run(self):
        self.run_btn.configure(state="normal")
        self.step_btn.configure(state="normal")
        r = self.result
        self.key_label.configure(
            text=f"Alice's sifted key: {r['alice_key']}\nBob's sifted key:   {r['bob_key']}"
        )
        if r["eavesdropper_detected"]:
            self.status_label.configure(text="⚠️  Eavesdropper Detected!", text_color=RED)
        else:
            self.status_label.configure(text="✅  Secure Communication", text_color=GREEN)
        self._render_chart(r)
        self._add_to_history(r)

    def _reveal_qubit(self, i):
        q = self.result["qubits"][i]
        tag = "nomatch"
        if q["in_key"]:
            tag = "mismatch" if q["mismatch"] else "match"
        if q["eve_present_here"]:
            tag = "eve" if not (q["in_key"] and q["mismatch"]) else "mismatch"

        self.tree.insert("", "end", values=(
            q["index"], q["alice_bit"],
            icon_for(q["alice_basis"], q["alice_bit"]),
            icon_for(q["eve_basis"], q["eve_bit"]) if q["eve_present_here"] else "—",
            icon_for(q["bob_basis"], q["bob_bit"]),
            "✓" if q["bases_match"] else "✗",
            q["bob_bit"], "Yes" if q["in_key"] else "No",
        ), tags=(tag,))
        self.tree.yview_moveto(1.0)
        self._animate_photon(q)

    def _animate_photon(self, q):
        c = self.channel_canvas
        c.delete("photon")
        w = max(c.winfo_width(), 900)
        y = 95
        alice_x, eve_x, bob_x = 65, w // 2, w - 65
        color = color_for(q["alice_bit"])

        photon = c.create_oval(alice_x - 9, y - 9, alice_x + 9, y + 9, fill=color, outline="", tags="photon")
        icon = c.create_text(alice_x, y - 24, text=icon_for(q["alice_basis"], q["alice_bit"]),
                               font=("Segoe UI", 15, "bold"), fill=color, tags="photon")

        target_x = eve_x if q["eve_present_here"] else bob_x
        self._move_step(photon, icon, alice_x, target_x, y, 12,
                          lambda: self._mid_or_end(q, photon, icon, eve_x, bob_x, y))

    def _mid_or_end(self, q, photon, icon, eve_x, bob_x, y):
        c = self.channel_canvas
        if q["eve_present_here"]:
            new_color = color_for(q["eve_bit"])
            c.itemconfig(photon, fill=new_color)
            c.itemconfig(icon, text=icon_for(q["eve_basis"], q["eve_bit"]), fill=new_color)
            self._move_step(photon, icon, eve_x, bob_x, y, 12, lambda: None)

    def _move_step(self, photon, icon, from_x, to_x, y, steps, on_done):
        c = self.channel_canvas
        dx = (to_x - from_x) / steps

        def step(n):
            if n <= 0:
                on_done()
                return
            c.move(photon, dx, 0)
            c.move(icon, dx, 0)
            self.after(15, lambda: step(n - 1))

        step(steps)

    def _render_chart(self, r):
        self.ax.clear()
        self.ax.set_facecolor(CARD)
        rate = r["error_rate"]
        color = RED if r["eavesdropper_detected"] else GREEN
        self.ax.bar(["Error Rate"], [rate], color=color, width=0.4)
        self.ax.axhline(10, color="#9ca3af", linestyle="--", linewidth=1, label="Threshold (10%)")
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel("Error Rate (%)")
        self.ax.set_title(f"Error Rate: {rate:.2f}%", fontsize=11, color=TEXT)
        self.ax.legend(fontsize=8)
        for spine in self.ax.spines.values():
            spine.set_color("#e5e7eb")
        self.canvas_chart.draw()

    # ================= LEARN TAB =================
    def _build_learn_tab(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        card.pack(fill="both", expand=True, pady=15)

        textbox = ctk.CTkTextbox(card, fg_color="#fbfbfd", text_color=TEXT,
                                    font=ctk.CTkFont(size=13), corner_radius=10, wrap="word")
        textbox.pack(fill="both", expand=True, padx=18, pady=18)

        content = """📘 How BB84 Works

BB84 lets Alice and Bob create a shared secret key using quantum bits (qubits), in a way that reveals any eavesdropper.

1. Alice generates random bits (0s and 1s).
2. Alice encodes each bit using a randomly chosen basis:
     • Rectilinear (+): 0 = ↔ horizontal, 1 = ↕ vertical
     • Diagonal (x): 0 = ↗ (45°), 1 = ↖ (135°)
3. She sends the qubits through the quantum channel.
4. Bob independently guesses a random basis to measure each qubit.
     • If his basis matches Alice's, he reads the correct bit.
     • If it doesn't match, the result is random — a coin flip.
5. Alice and Bob publicly compare which BASES they used (not the bit values).
6. They keep only the bits where their bases matched — the "sifted key."
7. To check for eavesdropping, they compare a sample of their sifted key.
   A high error rate (typically > ~11%) means someone measured the qubits
   in transit — and quantum mechanics guarantees that act changes them.

😈 Why Eve Gets Caught

Eve doesn't know which basis Alice used, so she has to guess. About half
the time she guesses wrong, and just like Bob, a wrong-basis measurement
scrambles the qubit before she resends it. That disturbance shows up
later as errors in Bob's key — even though Bob measured correctly.

This is the core idea of quantum cryptography: you cannot observe a
quantum system without risking disturbing it.

🎮 Try it in the Simulator tab

- Run without Eve → error rate stays near 0%.
- Enable Eve and run again → watch the error rate spike and the
  "Eavesdropper Detected!" warning appear.
- Use Step-by-Step Mode to watch each qubit travel one at a time.
"""
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

    # ================= HISTORY TAB =================
    def _build_history_tab(self, parent):
        chart_card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        chart_card.pack(fill="both", expand=True, pady=(15, 10))
        ctk.CTkLabel(chart_card, text="Error Rate Across Runs", font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=TEXT).pack(anchor="w", padx=18, pady=(14, 0))

        self.hist_fig = Figure(figsize=(6, 3), dpi=100, facecolor=CARD)
        self.hist_ax = self.hist_fig.add_subplot(111)
        self.hist_canvas = FigureCanvasTkAgg(self.hist_fig, master=chart_card)
        self.hist_canvas.get_tk_widget().pack(fill="both", expand=True, padx=18, pady=18)
        self._render_history_chart()

        table_card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color="#e5e7eb")
        table_card.pack(fill="both", expand=True)
        ctk.CTkLabel(table_card, text="Run Log", font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=TEXT).pack(anchor="w", padx=18, pady=(14, 8))

        table_frame = ctk.CTkFrame(table_card, fg_color=CARD)
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        cols = ("run", "n", "eve", "errorrate", "status")
        self.hist_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8, style="Custom.Treeview")
        for c, h, w in zip(cols, ["Run #", "Qubits", "Eve?", "Error Rate", "Result"], [55, 60, 55, 90, 130]):
            self.hist_tree.heading(c, text=h)
            self.hist_tree.column(c, width=w, anchor="center")
        self.hist_tree.tag_configure("secure", background=GREEN_LIGHT)
        self.hist_tree.tag_configure("detected", background=RED_LIGHT)
        self.hist_tree.pack(fill="both", expand=True)

        ctk.CTkButton(table_card, text="Clear History", command=self._clear_history,
                       fg_color="#6b7280", hover_color="#4b5563", corner_radius=8,
                       font=ctk.CTkFont(size=12, weight="bold"), height=32
                       ).pack(anchor="e", padx=18, pady=(10, 14))

    def _add_to_history(self, r):
        run_id = len(self.history) + 1
        entry = {"run": run_id, "n": r["n"], "eve": r["eve_present"],
                  "error_rate": r["error_rate"], "detected": r["eavesdropper_detected"]}
        self.history.append(entry)

        tag = "detected" if entry["detected"] else "secure"
        self.hist_tree.insert("", "end", values=(
            entry["run"], entry["n"], "Yes" if entry["eve"] else "No",
            f"{entry['error_rate']:.2f}%", "Detected" if entry["detected"] else "Secure"
        ), tags=(tag,))
        self._render_history_chart()

    def _render_history_chart(self):
        self.hist_ax.clear()
        self.hist_ax.set_facecolor(CARD)
        self.hist_fig.patch.set_facecolor(CARD)
        self.hist_ax.axhline(10, color="#9ca3af", linestyle="--", linewidth=1, label="Detection Threshold")

        if self.history:
            runs = [h["run"] for h in self.history]
            rates = [h["error_rate"] for h in self.history]
            colors = [RED if h["detected"] else GREEN for h in self.history]
            self.hist_ax.scatter(runs, rates, c=colors, s=65, zorder=3)
            self.hist_ax.plot(runs, rates, color="#9ca3af", linewidth=1, zorder=2)
            self.hist_ax.set_xticks(runs)

        self.hist_ax.set_ylim(0, 100)
        self.hist_ax.set_xlabel("Run #")
        self.hist_ax.set_ylabel("Error Rate (%)")
        self.hist_ax.legend(fontsize=8)
        for spine in self.hist_ax.spines.values():
            spine.set_color("#e5e7eb")
        self.hist_canvas.draw()

    def _clear_history(self):
        self.history.clear()
        self.hist_tree.delete(*self.hist_tree.get_children())
        self._render_history_chart()


if __name__ == "__main__":
    app = QuBitGuardApp()
    app.mainloop()