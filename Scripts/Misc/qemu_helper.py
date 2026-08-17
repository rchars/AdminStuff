from pathlib import Path

import subprocess
import argparse
import shutil

def ask_once(question):
    return input(question)

def ask_till_any(question, default=""):
    while not (answer := ask_once(question) or default):
        continue
    return answer

def ask_till_choosen(question, allowed_values):
    while True:
        answer = ask_once(question + f" (choose one: {", ".join(allowed_values)}):")
        if answer not in allowed_values:
            print("No such option.")
            continue
        return answer

def ask_till_positive_int(question):
    while True:
        try:
            answer = int(ask_once(question))
        except ValueError:
            print("Not a positive integer.")
        else:
            if answer <= 0:
                print("Not a positive integer.")
            return answer

def ask_till_size(question):
    allowed_units = ("K", "M", "G", "T",)
    while True:
        answer = ask_once(question)
        if not answer:
            continue

        try:
            number = int(answer[:-1])
        except ValueError:
            print(f"'{answer}' is not a positive integer with unit.")
            continue
        if number <= 0:
            print("'{answer}' is not a positive integer with unit.")
            continue
    
        unit = answer[-1]
        if unit not in allowed_units:
            print(f"Unit '{unit}' is not allowed. Allowed units: {",".join(allowed_units)}")
            continue

        return answer

class VMPaths:
    def __init__(self, vm_dpath_p):
        self.vm_dpath_p = vm_dpath_p
        
        self.optical_discs_dpath_p = vm_dpath_p / "OpticalDiscs"
        self.hard_drives_dpath_p = vm_dpath_p / "HardDrives"
        self.firmware_dpath_p = vm_dpath_p / "Firmware"
        self.tpm_dpath_p = vm_dpath_p / "TPM"

        self.tpm_state_dpath_p = self.tpm_dpath_p / "State"
        
        self.install_script_fpath_p = vm_dpath_p / "Install.sh"
        self.run_script_fpath_p = vm_dpath_p / "Run.sh"

        for dpath_p in (
            self.vm_dpath_p,
            self.hard_drives_dpath_p,
            self.optical_discs_dpath_p,
            self.firmware_dpath_p,
            self.tpm_dpath_p,
            self.tpm_state_dpath_p,
        ):
            dpath_p.mkdir(exist_ok=True)

class CPU:
    def __init__(self):
        self.model = str()
        self.topoext = str()

        self.thread = None
        self.sockets = None
        self.cores = None

    def get_run(self):
        smp = self.cores * self.sockets * self.threads
        return (
            f"-cpu {self.model},topoext={self.topoext}",
            (
                f"-smp {smp},"
                f"sockets={self.sockets},cores={self.cores},threads={self.threads}"
            ),
        )

    def get_install(self):
        return self.get_run()

    def ask(self):
        self.model = ask_till_any(
            "CPU model, most common: (EPYC, qemu64, kvm64, host, base, max), default EPYC:",
            default="EPYC"
        )
        self.topoext = ask_till_choosen(
            "Topoext on / off:",
            allowed_values=("on", "off",)
        )
        self.sockets = ask_till_positive_int("Number of sockets:")
        self.cores = ask_till_positive_int("Number of cores:")
        self.threads = ask_till_positive_int("Number of threads:")

class GPU:
    def __init__(self):
        self.vga = str()

    def get_run(self):
        return (
            f"-vga {self.vga}",
        )

    def get_install(self):
        return self.get_run()

    def ask(self):
        proc = subprocess.run(
            ["qemu-system-x86_64", "-vga", "help"],
            capture_output=True,
        )
        self.vga = ask_till_choosen(
            "VGA:",
            allowed_values=[s[0:s.find(" ")] for s in proc.stdout.decode().split("\n")][0:-1]
        )

class TPM:
    def __init__(self):
        self.enabled = None
        self.run_command = (
            "swtpm socket",
            "--tpm2",
            "--ctrl type=unixio,path=./TPM/Ctrl.sock",
            "--tpmstate dir=./TPM/State",
            "--log level=20 & disown",
        )

        self.install_command = (
            "swtpm_setup",
            "--tpm2",
            "--tpmstate dir://./TPM/State",
            "--overwrite",
            "--createek",
            "--lock-nvram",
        )

    def get_run(self):
        if self.enabled == "y":
            return (
                "-chardev socket,id=chrtpm,path=\"./TPM/Ctrl.sock\"",
                "-tpmdev emulator,id=tpm0,chardev=chrtpm",
                "-device tpm-tis,tpmdev=tpm0",
            )
        return tuple()

    def get_install(self):
        return self.get_run()

    def get_setup_run(self):
        if self.enabled == "y":
            return self.run_command
        return tuple()

    def get_setup_install(self):
        if self.enabled == "y":
            return self.install_command
        return tuple()

    def ask(self):
        self.enabled = ask_till_choosen(
            "TPM",
            allowed_values=("y", "n",)
        )

class Memory:
    def __init__(self):
        self.m = None

    def get_run(self):
        return (f"-m {self.m}",)

    def get_install(self):
        return self.get_run()

    def ask(self):
        self.m = ask_till_positive_int("Memory (MB):")

class Network:
    def __init__(self):
        self.nic = str()

    def get_run(self):
        return (self.nic,)

    def get_install(self):
        return self.get_run()

    def ask(self):
        yes_or_no = ask_till_choosen(
            "NAT to Internet",
            allowed_values=("y", "n")
        )
        if yes_or_no == "y":
            self.nic = "-nic user,ipv6=off,model=e1000"
        else:
            self.nic = "-nic none"

class Machine:
    def __init__(self):
        self.enable_kvm = str()
        self.machine = str()
        self.accel = str()

    def get_run(self):
        ret = (
            f"-machine {self.machine},accel={self.accel}",
        )
        if self.enable_kvm:
            return ret + (self.enable_kvm,)
        return ret

    def get_install(self):
        return self.get_run()

    def ask(self):
        self.machine = ask_till_any(
            "Machine type, most common: (q35, pc, isapc, none), default q35:",
            default="q35"
        )
        proc = subprocess.run(
            ["qemu-system-x86_64", "-accel", "help"],
            capture_output=True,
        )
        supported_accels = proc.stdout.decode().split("\n")[1:-1]
        self.accel = ask_till_choosen(
            "Accel",
            allowed_values=supported_accels,
        )
        if self.accel == "kvm":
            self.enable_kvm = "-enable-kvm"
        else:
            self.enable_kvm = ""

class Firmware:
    def __init__(self, firmware_dpath_p):
        self.copy = str()
        self.firmware_dpath_p = firmware_dpath_p

    def get_run(self):
        if self.copy == "n":
            return tuple()
        return (
            "-drive if=pflash,format=raw,readonly=on,file=./Firmware/OVMF_CODE_4M.ms.fd",
            "-drive if=pflash,format=raw,file=./Firmware/OVMF_VARS_4M.ms.fd",
        )

    def get_install(self):
        return self.get_run()

    def ask(self):
        self.copy = ask_till_choosen(
            "Copy OVMF firmware (y if TPM)",
            allowed_values=("y", "n",)
        )

    def run_setup_commands(self):
        if self.copy != "y":
            return None
        ovmf_code_fpath_p = self.firmware_dpath_p / "OVMF_CODE_4M.ms.fd"
        ovmf_vars_fpath_p = self.firmware_dpath_p / "OVMF_VARS_4M.ms.fd"
        search_dpath_p = Path("/usr/share/OVMF")
        files_left = {
            "OVMF_CODE_4M.ms.fd": ovmf_code_fpath_p,
            "OVMF_VARS_4M.ms.fd": ovmf_vars_fpath_p,
        }
        for elem_p in search_dpath_p.iterdir():
            if elem_p.name in files_left.keys():
                dest_fpath_p = files_left[elem_p.name]
                print(f"Copying {elem_p.name} to {dest_fpath_p}")
                shutil.copy(elem_p, dest_fpath_p)
                files_left.pop(elem_p.name)
                if not len(files_left):
                    break
        else:
            print(f"Could not find OVMF files: {files_left.keys()}")
        print("Setting permissions for copied OVMF files.")
        ovmf_code_fpath_p.chmod(0o400)
        ovmf_vars_fpath_p.chmod(0o600)

class HardDrive:
    def __init__(self, hard_drives_dpath_p, hard_drive_fname):
        self.hard_drives_dpath_p = hard_drives_dpath_p
        self.hard_drive_fname = hard_drive_fname
        self.hard_drive_format = str()
        # number + unit
        self.hard_drive_size = str()

    def get_dot_slash_drive_fpath_s(self):
        return "./" + str(
            (
                Path("./HardDrives") / self.hard_drive_fname
            ).with_suffix("." + self.hard_drive_format)
        )

    def get_absolute_drive_fpath_s(self):
        return str(
            (
                self.hard_drives_dpath_p / self.hard_drive_fname
            ).with_suffix("." + self.hard_drive_format)
        )

    def get_run(self):
        return (
            (
                f"-drive file={self.get_dot_slash_drive_fpath_s()},"
                f"format={self.hard_drive_format}"
            ),
        )

    def get_install(self):
        return self.get_run()

    def ask(self):
        self.hard_drive_format = ask_till_any(
            "Hard drive format, most common: (qcow2, raw, vdi), default qcow2:",
            default="qcow2"
        )
        self.hard_drive_size = ask_till_size("Hard drive size:")

    def run_setup_commands(self):
        subprocess.run(
            [
                "qemu-img",
                "create",
                "-f",
                self.hard_drive_format,
                self.get_absolute_drive_fpath_s(),
                self.hard_drive_size,
            ],
            check=True,
        )

class OpticalDisc:
    def __init__(self):
        self.optical_disc = str()

    def get_run(self):
        return tuple()

    def get_install(self):
        return (f"-cdrom {self.optical_disc}",)

    def ask(self):
        self.optical_disc = Path(
            ask_once("Path to optical disc:")
        ).expanduser()

class Main:
    def __init__(self, vm_dpath_p):
        self.vm_paths = VMPaths(vm_dpath_p)

    def run(self):
        machine = Machine()
        cpu = CPU()
        tpm = TPM()
        firmware = Firmware(self.vm_paths.firmware_dpath_p)
        gpu = GPU()
        memory = Memory()
        network = Network()
        optical_disc = OpticalDisc()
        hard_drive = HardDrive(
            self.vm_paths.hard_drives_dpath_p,
            self.vm_paths.vm_dpath_p.name,
        )

        all_components = (
            machine,
            cpu,
            tpm,
            firmware,
            gpu,
            memory,
            hard_drive,
            optical_disc,
            network,
        )

        for component in all_components:
            component.ask()

        install_script_content = "#!/usr/bin/env bash\n\n"
        install_script_content += "cd \"$(dirname \"$(readlink -f \"$0\")\")\"\n\n"

        for part in (" \\\n".join(tpm.get_setup_install()), " \\\n".join(tpm.get_setup_run()),):
            if part:
                install_script_content += part + "\n\n"
        
        install_script_content += "qemu-system-x86_64 \\\n"
        
        run_script_content = "#!/usr/bin/env bash\n\n"
        run_script_content += "cd \"$(dirname \"$(readlink -f \"$0\")\")\"\n\n"

        part = " \\\n".join(tpm.get_setup_run())
        if part:
            run_script_content += part + "\n\n"
        
        run_script_content += "qemu-system-x86_64 \\\n"

        install_script_content_list = []
        run_script_content_list = []

        for component in all_components:
            for method, l in {
                component.get_install: install_script_content_list,
                component.get_run: run_script_content_list,
            }.items():
                ret = method()
                if ret:
                    for s in method():
                        l.append(s)
                    l.append("")

        hard_drive.run_setup_commands()
        firmware.run_setup_commands()

        final_install_script_content = install_script_content + " \\\n".join(install_script_content_list)
        final_run_script_content = run_script_content + " \\\n".join(run_script_content_list)

        self.vm_paths.install_script_fpath_p.write_text(final_install_script_content)
        self.vm_paths.run_script_fpath_p.write_text(final_run_script_content)

        print("Setting permissions for Install.sh script.")
        self.vm_paths.install_script_fpath_p.chmod(0o755)

        print("Setting permissions for Run.sh script.")
        self.vm_paths.run_script_fpath_p.chmod(0o755)
        
def main(args):
    Main(args.vm_dir.expanduser()).run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("vm_dir", type=Path)
    args = parser.parse_args()
    main(args)
