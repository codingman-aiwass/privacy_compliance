$condaPath = (conda info --base)
Invoke-Expression "$condaPath/etc/profile.d/conda.sh"
conda activate py310
$param = $args[0]
python run.py $param