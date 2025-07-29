import os
import subprocess

class TerraformExecutor:
    def __init__(self):
        self.working_directory = os.path.join(os.path.dirname(__file__), "../terraform")
    
    def init(self):
        subprocess.run(["terraform", "init"], cwd=self.working_directory)
    
    def apply(self):
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=self.working_directory)
    
    def destroy(self):
        subprocess.run(["terraform", "destroy", "-auto-approve"], cwd=self.working_directory)