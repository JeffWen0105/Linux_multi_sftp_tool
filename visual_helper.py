from config_manager import load_config

def generate_jump_diagram(config_file):
    try:
        cfg = load_config(config_file)
        labels = ["LOCAL"]
        for jump in cfg.get('jump_servers', []):
            labels.append(f"{jump.get('username')}@{jump.get('host')}")
        tgt = cfg.get('target', {})
        labels.append(f"{tgt.get('username')}@{tgt.get('host')}")
        widths = [len(lbl) for lbl in labels]
        segments = ['+' + '-'*(w+2) + '+' for w in widths]
        line_top = '     '.join(segments)
        content_parts = []
        for i, lbl in enumerate(labels):
            part = '| ' + lbl + ' '*(widths[i]-len(lbl)) + ' |'
            content_parts.append(part)
            if i != len(labels)-1:
                content_parts.append('<->')
        line_mid = ' '.join(content_parts)
        line_bot = line_top
        return '\n'.join([line_top, line_mid, line_bot])
    except Exception:
        return "[無法解析 AUTH 檔案]"
