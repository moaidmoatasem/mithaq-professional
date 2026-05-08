import os
import re

replacements = {
    # File content replacements
    r'\bCHERENKOV\b': 'CHERENKOV',
    r'\bcherenkov\b': 'cherenkov',
    r'\bCherenkov\b': 'Cherenkov',
    r'\bDAQIQ\b': 'CHERENKOV',
    r'\bdaqiq\b': 'cherenkov',
    r'\bDaqiq\b': 'Cherenkov',

    r'\bDAREE3\b': 'MEISSNER',
    r'\bdaree3\b': 'meissner',
    r'\bDaree3\b': 'Meissner',
    r'\bDAREE\b': 'MEISSNER',
    r'\bdaree\b': 'meissner',
    r'\bDaree\b': 'Meissner',
    r'\bUrlGuard\b': 'Meissner',
    r'\burlguard\b': 'meissner',

    r'\bSIYAADA\b': 'ABLATION',
    r'\bsiyaada\b': 'ablation',
    r'\bSiyaada\b': 'Ablation',
    r'\bSIYADA\b': 'ABLATION',
    r'\bsiyada\b': 'ablation',
    r'\bSiyada\b': 'Ablation',

    r'\bAL-BURHAN\b': 'TOKAMAK',
    r'\bAl-Burhan\b': 'Tokamak',
    r'\bal-burhan\b': 'tokamak',
    r'\bBURHAN\b': 'TOKAMAK',
    r'\bBurhan\b': 'Tokamak',
    r'\bburhan\b': 'tokamak',

    r'\bSandbox\b': 'Tokamak',
    r'\bsandbox\b': 'tokamak'
}

print("Ready")
