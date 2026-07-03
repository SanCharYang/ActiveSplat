import os
import re

def patch_file():
    filepath = 'submodules/habitat/habitat-lab/habitat-lab/habitat/config/default_structured_configs.py'
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    with open(filepath, 'r') as f:
        content = f.read()

    replacements = {
        r"iterator_options: IteratorOptionsConfig = IteratorOptionsConfig\(\)": r"iterator_options: IteratorOptionsConfig = field(default_factory=IteratorOptionsConfig)",
        r"fog_of_war: FogOfWarConfig = FogOfWarConfig\(\)": r"fog_of_war: FogOfWarConfig = field(default_factory=FogOfWarConfig)",
        r"habitat_sim_v0: HabitatSimV0Config = HabitatSimV0Config\(\)": r"habitat_sim_v0: HabitatSimV0Config = field(default_factory=HabitatSimV0Config)",
        r"locobot: LocobotConfig = LocobotConfig\(\)": r"locobot: LocobotConfig = field(default_factory=LocobotConfig)",
        r"environment: EnvironmentConfig = EnvironmentConfig\(\)": r"environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)",
        r"simulator: SimulatorConfig = SimulatorConfig\(\)": r"simulator: SimulatorConfig = field(default_factory=SimulatorConfig)",
        r"gym: GymConfig = GymConfig\(\)": r"gym: GymConfig = field(default_factory=GymConfig)"
    }

    modified_content = content
    for old, new in replacements.items():
        modified_content = re.sub(old, new, modified_content)

    if content != modified_content:
        with open(filepath, 'w') as f:
            f.write(modified_content)
        print("Successfully patched default_structured_configs.py for Python 3.12 compatibility.")
    else:
        print("No changes needed or file already patched.")

if __name__ == '__main__':
    patch_file()
