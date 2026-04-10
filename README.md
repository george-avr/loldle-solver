# LoLdle Solver using Information Theory

## Overview

This project explores how **information theory** can be used to optimally solve the *LoLdle* guessing game (inspired by Wordle).

The goal is to transform the game from a trial-and-error process into a **systematic decision-making problem**, where each guess maximizes information gain and minimizes the expected number of remaining candidates.

The project includes:

* A full analytical notebook (`solver\loldle_analysis.ipynb`) exploring entropy and feature distributions
* A modular solver engine
* An **interactive CLI solver (`solver\cli.py`)** that guides the user step-by-step with optimal guesses

---

## What is LoLdle?
**LoLdle** is a guessing game, similar to other popular online guessing games such as **Wordle**, where a randomly selected character (or champion) is chosen daily from the League of Legends video game. The goal for players is to find what the randomly selected hidden champion is, by taking a guess each time until the champion is found.

What makes this challenge interesting is that after each guess the player makes, there is a feedback loop that takes place after each guess. Where, us the players, get some hints as to what the hidden champion's properties might be.

---

## Key Idea

Each guess partitions the space of possible champions based on the feedback it produces.

We evaluate guesses using:

* **Entropy** → Measures expected information gain (in bits) → higher = better
* **Expected remaining candidates** → Measures how much the search space shrinks → lower = better

The optimal guess is the one that:

> Maximizes uncertainty reduction across all possible outcomes
> 
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

### Feature Engineering

Handles multiple property types:

* Scalar (e.g. gender, region)
* Categorical
* Set-based (e.g. roles, traits with overlap)

### Informative Jupyter Notebook

* Exploratory analysis of data used by LoLdle
* Plots of distributions
* Code & internal logic used for the solver 

### Modular Codebase

* `solver.engine` → core logic
* `solver.plots` → visualization tools
* `cli.py` → interactive solver

---

## Project Structure
```
.
├── README.md
├── requirements.txt
│
├── resources/         # Data storage & images
├── results/           # Plots & CSV results
│
├── solver/
│   ├── __main__.py             # Run the interactive solver
│   ├── cli.py                  # Interactive solver (CLI)
│   ├── loldle_analysis.ipynb   # Exploratory + theoretical analysis
│   ├── champ_pipeline/         # Core ETL pipeline for gathering champion data
│   ├── engine/                 # Core solving logic
│   ├── metrics/                # Module for independent analysis
│   ├── plots/                  # Visualization utilities
│   ├── ui/                     # UI utilities for cli.py
│   └── utils/                  # Helper functions
```

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
6. Repeat until solution is found


---

## Running the Solver

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the interactive solver

```bash
python -m solver
```

### 3. Follow prompts

* Enter your guess in LoLdle
* Input the feedback
* The solver will suggest the best next guesses

---

## Example Workflow

```
Top 5 most informative guesses today:
==================================================================
Champion Name | Information (bits) | Expected Remaining Champions
------------------------------------------------------------------
1) Talon      | 6.2296973808094345 | 2.91812865497076
2) Riven      | 6.153845738275009  | 3.2339181286549707
...

Enter your guess: Talon

What indicator do you see for each property for Talon?
Answer with:  'correct'  'incorrect'  'partial'  'higher'  'lower'
------------------------------------------------------------------
Gender: ...
```

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

## Author

George Avramidis

---
