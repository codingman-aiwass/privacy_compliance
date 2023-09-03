import subprocess

# Define the command to be executed
command = 'conda info --base'

# Run the command and capture the output
output = subprocess.check_output(command, shell=True, text=True)

# Extract the desired information from the output
path_to_conda = output.strip()

# Print the captured output and assign it to a variable
print("Path to Conda:", path_to_conda)

conda_init_command = 'source {}/etc/profile.d/conda.sh'.format(path_to_conda)
print(conda_init_command)

# Initialize Conda in the shell
subprocess.run(['bash', '-c', conda_init_command])

# Activate the Conda environment
subprocess.run(['bash', '-c', 'conda activate py310'])

# Continue with the rest of your script
# ...

# Example: Run a Python script within the activated environment
subprocess.run('which python', shell=True)