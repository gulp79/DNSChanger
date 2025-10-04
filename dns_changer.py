import customtkinter as ctk
import subprocess
import json
import os
import sys
import ctypes

# --- Configuration ---
APP_NAME = "DNS Changer"
WIDTH = 900
HEIGHT = 900
DNS_LIST_FILE = "dns_list.txt"

# --- Theme and Colors ---
ctk.set_appearance_mode("Dark")
ACID_GREEN = "#6BFF00"
DARK_GRAY = "#242424"
LIGHT_GRAY = "#2E2E2E"
TEXT_COLOR = "#FFFFFF"
BUTTON_HOVER_COLOR = "#58D300"

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(APP_NAME)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.minsize(WIDTH, HEIGHT)

        self.configure(fg_color=DARK_GRAY)

        # --- State Variables ---
        self.interface_vars = {}
        self.dns_var = ctk.StringVar(value="")

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # --- Left Frame (Network Interfaces) ---
        self.left_frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=10)
        self.left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.left_frame, text="Network Interfaces", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.interfaces_frame = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.interfaces_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # --- Right Frame (DNS Servers) ---
        self.right_frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.right_frame, text="DNS Servers", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.dns_frame = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        self.dns_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # --- Middle Frame (Current DNS Settings) ---
        self.middle_frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=10)
        self.middle_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="ew")
        self.middle_frame.grid_rowconfigure(1, weight=1)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.middle_frame, text="Current DNS Settings", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.current_dns_frame = ctk.CTkScrollableFrame(self.middle_frame, fg_color="transparent", height=120)
        self.current_dns_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # --- Bottom Frame (Actions & Status) ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.refresh_button = ctk.CTkButton(self.bottom_frame, text="Refresh Interfaces", command=self.populate_interfaces, fg_color=ACID_GREEN, text_color=DARK_GRAY, hover_color=BUTTON_HOVER_COLOR)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.apply_button = ctk.CTkButton(self.bottom_frame, text="Apply Selected DNS", command=self.apply_dns, fg_color=ACID_GREEN, text_color=DARK_GRAY, hover_color=BUTTON_HOVER_COLOR)
        self.apply_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.reset_button = ctk.CTkButton(self.bottom_frame, text="Set to Automatic (DHCP)", command=self.reset_dns, fg_color=ACID_GREEN, text_color=DARK_GRAY, hover_color=BUTTON_HOVER_COLOR)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Loading application...", text_color="yellow")
        self.status_label.grid(row=1, column=0, columnspan=3, pady=10)

        # --- Initial Population ---
        self.populate_interfaces()
        self.load_dns_list()
        self.update_current_dns_display()

    def get_resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def run_powershell_command(self, command):
        """Executes a PowerShell command and returns the output with detailed error logging."""
        try:
            completed_process = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                encoding='utf-8'
            )
            return completed_process.stdout.strip()
        except FileNotFoundError:
            self.update_status("Error: PowerShell is not installed or not in PATH.", "red")
            return None
        except subprocess.CalledProcessError as e:
            # Provide a more detailed error message from PowerShell's stderr.
            error_details = e.stderr.strip() if e.stderr else "No details from stderr."
            self.update_status(f"PowerShell Error: {error_details}", "red")
            return None

    def get_network_adapters(self):
        """Fetches connected network adapters using an improved PowerShell command."""
        # Comando migliorato che filtra gli adattatori attivi e non virtuali
        command = """
        @(Get-NetAdapter | Where-Object { 
            $_.Status -eq 'Up' -and 
            $_.Name -notlike '*Loopback*' -and 
            $_.Name -notlike '*Virtual*' -and 
            $_.Name -notlike '*VMware*' -and 
            $_.Name -notlike '*VirtualBox*' -and 
            $_.Name -notlike '*Hyper-V*' -and
            $_.Name -notlike '*TAP*' -and
            $_.InterfaceType -ne 'Software Loopback' -and
            $_.MediaType -ne $null
        } | Select-Object Name, InterfaceIndex, InterfaceDescription, LinkSpeed) | ConvertTo-Json
        """
        
        json_output = self.run_powershell_command(command)
        if json_output:
            try:
                adapters = json.loads(json_output)
                # Se c'è un solo adattatore, PowerShell restituisce un oggetto, non un array
                if isinstance(adapters, dict):
                    adapters = [adapters]
                return adapters
            except json.JSONDecodeError as e:
                self.update_status(f"JSON Parsing Error: {e}. Output: {json_output}", "red")
                # Prova un metodo alternativo se il JSON fallisce
                return self.get_network_adapters_fallback()
        return []

    def get_network_adapters_fallback(self):
        """Metodo alternativo per ottenere gli adattatori di rete."""
        command = "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object Name, InterfaceIndex | ConvertTo-Json"
        json_output = self.run_powershell_command(command)
        if json_output:
            try:
                adapters = json.loads(json_output)
                if isinstance(adapters, dict):
                    adapters = [adapters]
                return adapters
            except json.JSONDecodeError:
                return []
        return []

    def populate_interfaces(self):
        """Clears and re-populates the network interfaces frame with admin checks."""
        # Explicitly check for admin rights when this function is called.
        if not is_admin():
            self.update_status("Error: Administrator rights are required. Please restart.", "red")
            return

        self.update_status("Refreshing network interfaces...", "yellow")
        for widget in self.interfaces_frame.winfo_children():
            widget.destroy()
        self.interface_vars.clear()

        adapters = self.get_network_adapters()
        if adapters is None:
            return

        if not adapters:
            ctk.CTkLabel(self.interfaces_frame, text="No active network adapters found.").pack(pady=10)
            self.update_status("No active network adapters found. Check connections/permissions.", "orange")
            return

        # Ordina gli adattatori per nome in ordine alfabetico
        adapters.sort(key=lambda x: x.get("Name", "").lower())
        
        for adapter in adapters:
            name = adapter.get("Name")
            index = adapter.get("InterfaceIndex")
            description = adapter.get("InterfaceDescription", "")
            link_speed = adapter.get("LinkSpeed", "")
            
            # Crea testo descrittivo per l'interfaccia
            display_text = name
            if description and description != name:
                display_text += f" ({description[:50]}{'...' if len(description) > 50 else ''})"
            if link_speed:
                # Converti velocità in formato leggibile
                try:
                    speed_bps = int(link_speed)
                    if speed_bps >= 1000000000:
                        speed_text = f"{speed_bps//1000000000} Gbps"
                    elif speed_bps >= 1000000:
                        speed_text = f"{speed_bps//1000000} Mbps"
                    else:
                        speed_text = f"{speed_bps//1000} Kbps"
                    display_text += f" - {speed_text}"
                except (ValueError, TypeError):
                    pass
            
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(self.interfaces_frame, text=display_text, variable=var, onvalue=str(index), offvalue="off", command=self.update_current_dns_display)
            cb.pack(anchor="w", padx=10, pady=5)
            self.interface_vars[name] = var
            
        self.update_status("Interfaces refreshed successfully. Ready.", ACID_GREEN)

    def load_dns_list(self):
        """Loads DNS servers from the external text file."""
        for widget in self.dns_frame.winfo_children():
            widget.destroy()
        
        dns_file_path = self.get_resource_path(DNS_LIST_FILE)
        
        # Crea file di esempio se non esiste
        if not os.path.exists(dns_file_path):
            self.create_default_dns_file(dns_file_path)
        
        try:
            with open(dns_file_path, "r", encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            dns_servers = ",".join(parts[1:]).strip()
                            rb = ctk.CTkRadioButton(self.dns_frame, text=f"{name} ({dns_servers})", variable=self.dns_var, value=dns_servers)
                            rb.pack(anchor="w", padx=10, pady=5)
        except FileNotFoundError:
            self.update_status(f"Error: '{DNS_LIST_FILE}' not found.", "red")
        except UnicodeDecodeError:
            self.update_status(f"Error: Cannot read '{DNS_LIST_FILE}'. Check file encoding.", "red")

    def create_default_dns_file(self, file_path):
        """Crea un file DNS di esempio se non esiste."""
        default_content = """# DNS Server List
# Format: Name,Primary DNS,Secondary DNS
Google DNS,8.8.8.8,8.8.4.4
Cloudflare DNS,1.1.1.1,1.0.0.1
OpenDNS,208.67.222.222,208.67.220.220
Quad9,9.9.9.9,149.112.112.112
AdGuard DNS,94.140.14.14,94.140.15.15
"""
        try:
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(default_content)
        except Exception as e:
            self.update_status(f"Error creating default DNS file: {e}", "red")

    def get_selected_interfaces(self):
        """Returns a list of selected interface indices."""
        selected = []
        for var in self.interface_vars.values():
            if var.get() != "off":
                selected.append(var.get())
        return selected

    def apply_dns(self):
        """Applies the selected DNS to the selected interfaces."""
        interfaces = self.get_selected_interfaces()
        dns_servers = self.dns_var.get()

        if not interfaces:
            self.update_status("Please select at least one network interface.", "orange")
            return
        if not dns_servers:
            self.update_status("Please select a DNS server.", "orange")
            return
        
        self.update_status("Applying DNS settings...", "yellow")
        formatted_dns = ",".join([f'"{d.strip()}"' for d in dns_servers.split(',')])
        
        success_count = 0
        for index in interfaces:
            command = f"Set-DnsClientServerAddress -InterfaceIndex {index} -ServerAddresses ({formatted_dns})"
            result = self.run_powershell_command(command)
            if result is not None:
                success_count += 1
        
        if success_count > 0:
            self.update_status(f"Applied DNS to {success_count}/{len(interfaces)} interfaces successfully.", ACID_GREEN)
        else:
            self.update_status("Failed to apply DNS settings. Check permissions.", "red")
        
        self.after(500, self.update_current_dns_display)

    def get_current_dns(self, interface_index):
        """Ottiene i DNS attualmente configurati per un'interfaccia specifica."""
        command = f"Get-DnsClientServerAddress -InterfaceIndex {interface_index} | Where-Object {{$_.AddressFamily -eq 2}} | Select-Object ServerAddresses | ConvertTo-Json"
        result = self.run_powershell_command(command)
        if result:
            try:
                data = json.loads(result)
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("ServerAddresses", [])
                elif isinstance(data, dict):
                    return data.get("ServerAddresses", [])
            except (json.JSONDecodeError, KeyError):
                pass
        return []

    def get_interface_name_by_index(self, interface_index):
        """Ottiene il nome dell'interfaccia dal suo indice."""
        for name, var in self.interface_vars.items():
            if var.get() == str(interface_index):
                return name
        return f"Interface {interface_index}"

    def update_current_dns_display(self):
        """Aggiorna la visualizzazione dei DNS correnti per le interfacce selezionate."""
        # Pulisce il frame corrente
        for widget in self.current_dns_frame.winfo_children():
            widget.destroy()
        
        selected_interfaces = self.get_selected_interfaces()
        
        if not selected_interfaces:
            ctk.CTkLabel(self.current_dns_frame, text="No interfaces selected", text_color="gray").pack(pady=10)
            return
        
        for interface_index in selected_interfaces:
            interface_name = self.get_interface_name_by_index(interface_index)
            current_dns = self.get_current_dns(interface_index)
            
            # Frame per ogni interfaccia
            interface_frame = ctk.CTkFrame(self.current_dns_frame, fg_color=DARK_GRAY, corner_radius=5)
            interface_frame.pack(fill="x", padx=5, pady=2)
            
            # Nome dell'interfaccia
            name_label = ctk.CTkLabel(interface_frame, text=f"{interface_name}:", 
                                    font=ctk.CTkFont(weight="bold"), text_color=ACID_GREEN)
            name_label.pack(anchor="w", padx=10, pady=(5, 0))
            
            # DNS correnti
            if current_dns and len(current_dns) > 0:
                dns_text = ", ".join(current_dns)
                dns_label = ctk.CTkLabel(interface_frame, text=f"DNS: {dns_text}", text_color=TEXT_COLOR)
                dns_label.pack(anchor="w", padx=10, pady=(0, 5))
            else:
                dns_label = ctk.CTkLabel(interface_frame, text="DNS: Automatic (DHCP)", text_color="orange")
                dns_label.pack(anchor="w", padx=10, pady=(0, 5))

    def reset_dns(self):
        """Resets DNS settings to automatic (DHCP) for selected interfaces."""
        interfaces = self.get_selected_interfaces()
        if not interfaces:
            self.update_status("Please select at least one network interface.", "orange")
            return
            
        self.update_status("Resetting DNS to DHCP...", "yellow")
        success_count = 0
        for index in interfaces:
            command = f"Set-DnsClientServerAddress -InterfaceIndex {index} -ResetServerAddresses"
            result = self.run_powershell_command(command)
            if result is not None:
                success_count += 1
        
        if success_count > 0:
            self.update_status(f"Reset DNS for {success_count}/{len(interfaces)} interfaces to DHCP.", ACID_GREEN)
        else:
            self.update_status("Failed to reset DNS settings. Check permissions.", "red")
            
        self.after(500, self.populate_interfaces)
        
    def update_status(self, message, color):
        """Updates the status label with a message and color."""
        self.status_label.configure(text=message, text_color=color)

def is_admin():
    """Checks for administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-runs the script with administrator privileges."""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

if __name__ == "__main__":
    if is_admin():
        app = App()
        app.mainloop()
    else:
        run_as_admin()
