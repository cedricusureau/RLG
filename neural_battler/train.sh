#!/bin/bash
#SBATCH --partition=cpu_med
#SBATCH --ntasks=1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --job-name=neural_battler
#SBATCH --output=train_output_%j.log

# Purger les modules et charger l'environnement Anaconda
module purge
module load anaconda3/2021.05/gcc-9.2.0

# Activer l'environnement Anaconda
source activate cedric_bs

# Chemin absolu vers votre projet (corrigé)
PROJECT_DIR="/gpfs/workdir/usureauc/RLG/neural_battler"

# Se déplacer dans le répertoire du projet
cd $PROJECT_DIR

# Lancer l'entraînement directement avec le script Python
python $PROJECT_DIR/train_all.py train --episodes 3000 --batch-size 128 --save-interval 100