class DeploymentConfig:
    def __init__(self, config_file: str):
        with open(config_file) as f:
            self.config = yaml.safe_load(f)
            
    def get_environment(self, env_name: str) -> Dict:
        return self.config['environments'][env_name]