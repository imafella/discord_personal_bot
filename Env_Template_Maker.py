import os

env_path = ".env"
template_path = ".env_template"

def blank_env_values(line):
    if "=" in line and not line.strip().startswith("#"):
        key = line.split("=", 1)[0]
        return f"{key}=\n"
    return line

with open(env_path, "r") as env_file:
    lines = env_file.readlines()

with open(template_path, "w") as template_file:
    for line in lines:
        template_file.write(blank_env_values(line))
    print(f"\n\nTemplate created at {template_path} with blank values.")