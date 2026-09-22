import os

target = '/home/kai/projects/rung/backend/app/api/v1/routes/listings.py'
with open(target, 'r') as f:
    content = f.read()

content = content.replace(
    "if identifier.startswith('_'):\n            handles_to_try.append('@' + identifier[1:])",
    "if identifier.startswith('_'):\n            handles_to_try.append('@' + identifier[1:])\n            handles_to_try.append('@' + identifier.strip('_'))"
+
with open(target, 'w') as f:
    f.write(content)

print("Fixed strip listings.py")
