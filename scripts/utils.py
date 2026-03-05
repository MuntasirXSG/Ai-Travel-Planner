import os 
import json 

def load_mcp_config(*servers):
    config_path=os.path.join(os.path.dirname(__file__),'mcp_config.json')
    selected_config={}

    with open(config_path , 'r') as f:
        all_config= json.load(f)
        if len(servers)==0:
            return all_config
        for name in servers:
            if name in all_config:
                selected_config['name'] = all_config['name']
        return selected_config


