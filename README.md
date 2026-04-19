# LoLdle Solver using Information Theory

## Overview

This project explores how **information theory** can be used to optimally solve the *LoLdle* guessing game (inspired by Wordle).

The goal is to transform the game from a trial-and-error process into a **systematic decision-making problem**, where each guess maximizes information gain and minimizes the expected number of remaining candidates.

The project includes:

* A **full analytical notebook (`notebooks/loldle_analysis.ipynb`)** exploring entropy and feature distributions
* An **interactive CLI solver (`solver/cli.py`)** that guides the user step-by-step with optimal guesses
* A **CSV builder (`dataset/builder.py`)** that creates an *up-to-date* **LoLdle** dataset in the **`results`** folder.
* A modular solver engine

---

## Demo

![Cool Animation](resources/demo.gif)

---

## What is LoLdle?
**LoLdle** is a daily guessing game inspired by **Wordle** and based on the video game League of Legends. Each day, a random champion from the game is selected, and players must guess who it is. 
The goal is to find the correct champion in as few attempts as possible, with fewer guesses reflecting better performance.

After each guess, the game provides feedback in the form of clues about the hidden champion’s characteristics, such as their role, region, resource type, release year, and other attributes. These hints help players narrow down the correct answer through deduction.

---

## Key Idea

Each guess partitions the space of possible champions based on the feedback it produces.

We evaluate guesses using:

* **Entropy** → Measures expected information gain (in bits) → higher = better
* **Expected remaining candidates** → Measures how much the search space shrinks → lower = better

The optimal guess is the one that:

> Maximizes uncertainty reduction across all possible outcomes

The solver suggests guesses based on **entropy** initially, after that by smallest **expected remaining candidates** value.

### Entropy Definition

We compute entropy over feedback partitions:

$$
H(X) = - ∑ p(x) log₂ p(x)
$$

where each $x$ corresponds to a unique feedback pattern induced by a guess.

---

## Features

### Fully Automated ETL Pipeline

* Automatically fetches all data used by LoLdle for each champion
* Stores the data in JSON format
* Automatically updates upon new patch notes

### Information-Theoretic Solver

* Computes entropy of each possible guess
* Evaluates how well a guess splits the hypothesis space
* Dynamically updates after each round

### Interactive CLI Tool

* User inputs feedback from LoLdle
* Solver recomputes best guesses in real time
* Provides ranked suggestions for next guess

### Informative Jupyter Notebook

* Exploratory analysis of data used by LoLdle
* Plots of distributions
* Code & internal logic used for the solver 

### Modular Codebase

* `solver.engine` → core logic
* `solver.plots` → visualization tools
* `cli.py` → interactive solver

---

## How It Works

1. Start with all possible champions
2. For each possible guess:
   * Simulate all feedback outcomes
   * Compute probability of each outcome
   * Calculate entropy
3. Prompt the user for a guess
4. Prompt the user for the feedback they received
5. Filter candidates based on the guess and feedback
6. Repeat until the hidden champion is found


---

## Running the Solver

### 0. Prerequisites

* Python 3.11 or newer

Check your version:

```bash
python3 --version
```

### 1. Clone the repository

```bash
git clone https://github.com/GeorgeAvramidis/loldle-solver
cd loldle-solver
```

### 2. Create a virtual environment

#### Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the interactive solver

```bash
python -m solver
```
> Make sure you run this from the project root directory

### 5. Follow prompts

* Enter your guess in LoLdle
* Input the feedback exactly as shown in the game
* The solver will suggest optimal next guesses

---

## Why This Project Matters

This project demonstrates:

* Applied **ETL pipelines** to fetch data
* Applied **information theory**
* **Algorithm design** for decision-making under uncertainty
* Real-world problem modeling
* Clean modular Python architecture

It bridges theory and practice by turning a game into an **optimization problem**.

---

## Project Structure
```
.
├── LICENSE
├── README.md
├── requirements.txt
│
├── resources/                       # Data storage & images
├── results/
│   ├── plots/                       # Plots for visual analysis
│   └── loldle_dataset.csv           # LoLdle dataset with all champion properties & guess rankings
│
├── dataset/
│   └── loldle_dataset_builder.py    # LoLdle dataset builder for independent analysis
│
├── notebooks/
│   └── loldle_analysis.ipynb        # Exploratory + theoretical analysis
│
└── solver/
    ├── __main__.py                  # Run the interactive solver
    ├── cli.py                       # Interactive solver (CLI)
    │
    ├── champ_pipeline/              # Core ETL pipeline for getting all champion data
    ├── engine/                      # Core solving logic
    ├── plots/                       # Visualization utilities
    ├── ui/                          # UI utilities for cli.py
    └── utils/                       # Helper functionalities
```

---

## Author

George Avramidis

---
