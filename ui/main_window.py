"""Main application window for DNSChanger."""

import customtkinter as ctk
import logging
import threading
import time
from pathlib import Path
from typing import Optional, List
from tkinter import messagebox

from core.dns_loader import DNSLoader
from core.dns_verifier import DNSVerifier
from core.migration import migrate_txt_to_yaml, can_migrate
from ps.ps_adapter import PowerShellAdapter
from ps.doh_manager import DoHManager
from models.dns_provider import DNSProvider

logger = logging.getLogger(__name__)

# Theme and Colors
ctk.set_appearance_mode("Dark")
ACID_GREEN = "#6BFF00"
DARK_GRAY = "#242424"
LIGHT_GRAY = "#2E2E2E"
TEXT_COLOR = "#FFFFFF"
BUTTON_HOVER_COLOR = "#58D300"
ERROR_COLOR = "#FF4444"
WARNING_COLOR = "#FFA500"
SUCCESS_COLOR = ACID_GREEN


class DNSChangerApp(ctk.CTk):
    """Main DNS Changer application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("DNS Changer - Advanced")
        self.geometry("1000x900")
        self.minsize(900, 800)
        self.configure(fg_color=DARK_GRAY)
        
        # Initialize components
        self.ps_adapter = PowerShellAdapter()
        self.doh_manager = DoHManager(self.ps_adapter)
        self.dns_loader = DNSLoader()
        self.dns_verifier = DNSVerifier(self.ps_adapter)
        
        # State variables
        self.interface_vars = {}
        self.selected_provider: Optional[DNSProvider] = None
        self.use_doh_var = ctk.BooleanVar(value=True)
        self.flush_cache_var = ctk.BooleanVar(value=True)
        self.rollback_timer: Optional[threading.Timer] = None
        
        self._setup_ui()
        self._load_initial_data()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=0)
        
        # Left frame - Network Interfaces
        self._create_interfaces_frame()
        
        # Right frame - DNS Providers
        self._create_providers_frame()
        
        # Middle frame - Current Status
        self._create_status_frame()
        
        # Bottom frame - Actions
        self._create_actions_frame()
    
    def _create_interfaces_frame(self):
        """Create network interfaces panel."""
        frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=10)
        frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            title_frame,
            text="Network Interfaces",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")
        
        ctk.CTkButton(
            title_frame,
            text="↻",
            width=30,
            command=self._refresh_interfaces,
            fg_color=ACID_GREEN,
            text_color=DARK_GRAY,
            hover_color=BUTTON_HOVER_COLOR
        ).pack(side="right")
        
        self.interfaces_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.interfaces_scroll.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
    
    def _create_providers_frame(self):
        """Create DNS providers panel."""
        frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=10)
        frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame,
            text="DNS Providers",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # DoH toggle
        doh_frame = ctk.CTkFrame(frame, fg_color="transparent")
        doh_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        self.doh_toggle = ctk.CTkSwitch(
            doh_frame,
            text="Use DoH (DNS over HTTPS)",
            variable=self.use_doh_var,
            onvalue=True,
            offvalue=False,
            progress_color=ACID_GREEN
        )
        self.doh_toggle.pack(side="left")
        
        self.doh_status_label = ctk.CTkLabel(
            doh_frame,
            text="",
            text_color=WARNING_COLOR,
            font=ctk.CTkFont(size=11)
        )
        self.doh_status_label.pack(side="left", padx=10)
        
        # Providers list
        self.providers_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.providers_scroll.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="nsew")
    
    def _create_status_frame(self):
        """Create current status panel."""
        frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=10)
        frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame,
            text="Current Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.status_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", height=150)
        self.status_scroll.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
    
    def _create_actions_frame(self):
        """Create actions panel."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Options
        options_frame = ctk.CTkFrame(frame, fg_color=LIGHT_GRAY, corner_radius=5)
        options_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ctk.CTkCheckBox(
            options_frame,
            text="Flush DNS cache after applying",
            variable=self.flush_cache_var,
            fg_color=ACID_GREEN,
            hover_color=BUTTON_HOVER_COLOR
        ).pack(side="left", padx=15, pady=5)
        
        # Action buttons
        self.apply_btn = ctk.CTkButton(
            frame,
            text="Apply DNS Settings",
            command=self._apply_dns,
            fg_color=ACID_GREEN,
            text_color=DARK_GRAY,
            hover_color=BUTTON_HOVER_COLOR,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.apply_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            frame,
            text="Reset to DHCP",
            command=self._reset_dns,
            fg_color=WARNING_COLOR,
            text_color=DARK_GRAY,
            hover_color="#CC8400"
        ).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            frame,
            text="Migrate from dns_list.txt",
            command=self._show_migration_dialog,
            fg_color=LIGHT_GRAY,
            hover_color="#3E3E3E"
        ).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            frame,
            text="Ready",
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=2, column=0, columnspan=3, pady=10)
    
    def _load_initial_data(self):
        """Load initial data (interfaces and providers)."""
        # Check DoH support
        supported, msg = self.doh_manager.is_supported()
        if not supported:
            self.doh_toggle.configure(state="disabled")
            self.doh_status_label.configure(text="⚠️ " + msg.split('.')[0])
            self.use_doh_var.set(False)
        
        # Load providers
        self._load_providers()
        
        # Load interfaces
        self._refresh_interfaces()
        
        self._update_status("Ready", SUCCESS_COLOR)
    
    def _load_providers(self):
        """Load DNS providers from configuration."""
        providers = self.dns_loader.load_providers()
        
        if not providers:
            # Check for migration
            if self.dns_loader.has_legacy_file() and not self.dns_loader.has_yaml_file():
                self._update_status(
                    "⚠️ Legacy dns_list.txt found. Click 'Migrate' to convert to new format.",
                    WARNING_COLOR
                )
            else:
                errors = "\n".join(self.dns_loader.get_errors())
                self._update_status(f"Error loading providers: {errors}", ERROR_COLOR)
            return
        
        # Clear existing providers
        for widget in self.providers_scroll.winfo_children():
            widget.destroy()
        
        # Add provider buttons
        for provider in providers:
            self._create_provider_button(provider)
        
        logger.info(f"Loaded {len(providers)} DNS providers")
    
    def _create_provider_button(self, provider: DNSProvider):
        """Create a provider selection button."""
        btn_frame = ctk.CTkFrame(self.providers_scroll, fg_color=DARK_GRAY, corner_radius=5)
        btn_frame.pack(fill="x", padx=5, pady=3)
        
        # Provider name and badges
        info_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=provider.name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        )
        name_label.pack(side="left")
        
        # Badges
        badges_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        badges_frame.pack(side="right")
        
        if provider.doh_template:
            ctk.CTkLabel(
                badges_frame,
                text="🔒 DoH",
                font=ctk.CTkFont(size=10),
                text_color=ACID_GREEN
            ).pack(side="left", padx=2)
        
        for tag in provider.tags[:3]:  # Show first 3 tags
            ctk.CTkLabel(
                badges_frame,
                text=f"#{tag}",
                font=ctk.CTkFont(size=9),
                text_color="gray"
            ).pack(side="left", padx=2)
        
        # DNS addresses
        dns_text = ", ".join(provider.ipv4[:2])
        if len(provider.ipv4) > 2:
            dns_text += f" +{len(provider.ipv4) - 2} more"
        
        ctk.CTkLabel(
            btn_frame,
            text=dns_text,
            font=ctk.CTkFont(size=11),
            text_color="lightgray",
            anchor="w"
        ).pack(padx=10, pady=(0, 5), anchor="w")
        
        # Select button
        def select_provider():
            self.selected_provider = provider
            self._update_status(f"Selected: {provider.name}", TEXT_COLOR)
            # Highlight selected
            for child in self.providers_scroll.winfo_children():
                child.configure(fg_color=DARK_GRAY)
            btn_frame.configure(fg_color="#3A3A3A")
        
        btn_frame.bind("<Button-1>", lambda e: select_provider())
        for child in btn_frame.winfo_children():
            child.bind("<Button-1>", lambda e: select_provider())
    
    def _refresh_interfaces(self):
        """Refresh network interfaces list."""
        self._update_status("Loading interfaces...", TEXT_COLOR)
        
        adapters = self.ps_adapter.get_network_adapters(include_virtual=False, include_down=False)
        
        # Clear existing
        for widget in self.interfaces_scroll.winfo_children():
            widget.destroy()
        self.interface_vars.clear()
        
        if not adapters:
            ctk.CTkLabel(
                self.interfaces_scroll,
                text="No active network adapters found",
                text_color=WARNING_COLOR
            ).pack(pady=20)
            self._update_status("No active adapters found", WARNING_COLOR)
            return
        
        # Add interface checkboxes
        for adapter in adapters:
            var = ctk.StringVar(value="off")
            self.interface_vars[adapter.index] = (var, adapter.name)
            
            cb = ctk.CTkCheckBox(
                self.interfaces_scroll,
                text=f"{adapter.display_name}\n{adapter.description}",
                variable=var,
                onvalue=adapter.index,
                offvalue="off",
                command=lambda: self._update_current_status(),
                fg_color=ACID_GREEN,
                hover_color=BUTTON_HOVER_COLOR
            )
            cb.pack(anchor="w", padx=10, pady=5)
        
        self._update_status(f"Found {len(adapters)} network interfaces", SUCCESS_COLOR)
        self._update_current_status()
    
    def _update_current_status(self):
        """Update current DNS status display."""
        # Clear existing
        for widget in self.status_scroll.winfo_children():
            widget.destroy()
        
        selected = self._get_selected_interfaces()
        
        if not selected:
            ctk.CTkLabel(
                self.status_scroll,
                text="No interfaces selected",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for index, name in selected:
            frame = ctk.CTkFrame(self.status_scroll, fg_color=DARK_GRAY, corner_radius=5)
            frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(
                frame,
                text=name,
                font=ctk.CTkFont(weight="bold"),
                text_color=ACID_GREEN
            ).pack(anchor="w", padx=10, pady=(5, 0))
            
            dns_servers = self.ps_adapter.get_dns_servers(index)
            
            if dns_servers:
                dns_text = "DNS: " + ", ".join(dns_servers)
                ctk.CTkLabel(
                    frame,
                    text=dns_text,
                    text_color=TEXT_COLOR,
                    font=ctk.CTkFont(size=11)
                ).pack(anchor="w", padx=10, pady=(0, 5))
                
                # Check DoH status
                if self.doh_manager.doh_supported:
                    doh_state = self.doh_manager.get_interface_doh_state(index, name)
                    if doh_state.doh_servers:
                        ctk.CTkLabel(
                            frame,
                            text="🔒 DoH Active",
                            text_color=ACID_GREEN,
                            font=ctk.CTkFont(size=10)
                        ).pack(anchor="w", padx=10, pady=(0, 5))
            else:
                ctk.CTkLabel(
                    frame,
                    text="DNS: Automatic (DHCP)",
                    text_color=WARNING_COLOR,
                    font=ctk.CTkFont(size=11)
                ).pack(anchor="w", padx=10, pady=(0, 5))
    
    def _apply_dns(self):
        """Apply DNS settings with verification."""
        selected = self._get_selected_interfaces()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one network interface.")
            return
        
        if not self.selected_provider:
            messagebox.showwarning("No Provider", "Please select a DNS provider.")
            return
        
        # Confirm action
        msg = f"Apply {self.selected_provider.name} to {len(selected)} interface(s)?"
        if not messagebox.askyesno("Confirm", msg):
            return
        
        self.apply_btn.configure(state="disabled")
        self._update_status("Applying DNS settings...", TEXT_COLOR)
        
        # Inizia il tracciamento del tempo di applicazione totale (incluso avvio script PS)
        start_apply_time = time.time()
        
        # Run in thread to avoid blocking UI
        threading.Thread(target=self._apply_dns_thread, args=(selected, start_apply_time), daemon=True).start()
    
    def _apply_dns_thread(self, selected, start_apply_time):
        """Apply DNS settings in background thread."""
        success_count = 0
        failed = []
        
        for index, name in selected:
            # Create snapshot for rollback
            self.dns_verifier.create_snapshot(index, name)
            
            # Apply DNS
            if self.use_doh_var.get() and self.doh_manager.doh_supported:
                # Apply with DoH
                success, msg = self.doh_manager.configure_provider_doh(
                    index,
                    self.selected_provider.ipv4,
                    self.selected_provider.doh_template,
                    self.selected_provider.policy.encrypted_only,
                    self.selected_provider.policy.autoupgrade,
                    self.selected_provider.policy.allow_udp_fallback
                )
            else:
                # Apply without DoH
                success, msg = self.ps_adapter.set_dns_servers(
                    index,
                    self.selected_provider.ipv4,
                    validate=True
                )
            
            if success:
                success_count += 1
            else:
                failed.append((name, msg))
        
        # Flush cache if requested
        if self.flush_cache_var.get():
            self.ps_adapter.flush_dns_cache()
            
        apply_duration_ms = (time.time() - start_apply_time) * 1000
        
        # Verify DNS
        self.after(0, lambda: self._verify_dns_and_rollback(selected, success_count, failed, apply_duration_ms))
    
    def _verify_dns_and_rollback(self, selected, success_count, failed, apply_duration_ms):
        """Verify DNS and setup rollback timer."""
        if success_count > 0:
            result = self.dns_verifier.verify_dns()
            
            if result.is_successful:
                total_time = apply_duration_ms + result.duration_ms
                msg = (f"✓ DNS applied to {success_count} interface(s).\n"
                       f"Verification passed (Apply: {apply_duration_ms:.0f}ms, Verify: {result.duration_ms:.0f}ms)")
                self._update_status(msg, SUCCESS_COLOR)
            else:
                self._update_status(
                    f"⚠️ DNS applied but verification failed. Auto-rollback in 30s...",
                    WARNING_COLOR
                )
                # Setup rollback timer
                self.rollback_timer = threading.Timer(30, self._auto_rollback, args=(selected,))
                self.rollback_timer.start()
        
        if failed:
            error_msg = "\n".join([f"{name}: {msg}" for name, msg in failed])
            messagebox.showerror("Errors", f"Failed on some interfaces:\n{error_msg}")
        
        self.apply_btn.configure(state="normal")
        self._update_current_status()
    
    def _auto_rollback(self, selected):
        """Auto rollback after verification failure."""
        for index, name in selected:
            self.dns_verifier.rollback(index)
        
        self.after(0, lambda: self._update_status("DNS rolled back to previous settings", WARNING_COLOR))
        self.after(0, self._update_current_status)
    
    def _reset_dns(self):
        """Reset DNS to DHCP."""
        selected = self._get_selected_interfaces()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one network interface.")
            return
        
        if not messagebox.askyesno("Confirm", f"Reset {len(selected)} interface(s) to DHCP?"):
            return
        
        success_count = 0
        for index, name in selected:
            success, msg = self.ps_adapter.reset_dns(index)
            if success:
                success_count += 1
        
        self._update_status(f"Reset {success_count} interface(s) to DHCP", SUCCESS_COLOR)
        self._update_current_status()
    
    def _show_migration_dialog(self):
        """Show migration dialog."""
        can_mig, msg = can_migrate(
            Path.cwd() / "dns_list.txt",
            Path.cwd() / "dns_providers.yaml"
        )
        
        if not can_mig:
            messagebox.showinfo("Migration", msg)
            return
        
        if messagebox.askyesno("Migrate", f"{msg}\n\nMigrate now?"):
            self._migrate_legacy_file()
    
    def _migrate_legacy_file(self):
        """Migrate legacy dns_list.txt to YAML."""
        success, msg = migrate_txt_to_yaml(
            Path.cwd() / "dns_list.txt",
            Path.cwd() / "dns_providers.yaml",
            backup=True
        )
        
        if success:
            messagebox.showinfo("Success", msg)
            self._load_providers()
        else:
            messagebox.showerror("Error", msg)
    
    def _get_selected_interfaces(self):
        """Get list of selected interfaces."""
        selected = []
        for index, (var, name) in self.interface_vars.items():
            if var.get() != "off":
                selected.append((index, name))
        return selected
    
    def _update_status(self, message: str, color: str):
        """Update status label."""
        self.status_label.configure(text=message, text_color=color)
        logger.info(f"Status: {message}")

