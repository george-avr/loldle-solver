from solver.champ_pipeline.loader import load_champions, create_champions_json
from solver.engine.guess_evaluation import compute_pattern_id_matrix, compute_metrics, filter_candidates
from solver.utils import paths
from solver.ui.interactive import (
    input_champion,
    input_feedback,
    welcome_user,
    show_top_results,
    show_remaining_champions,
    is_correct,
    two_remaining,
    one_remaining
)


def main():
    data_path = paths.champion_data

    create_champions_json(data_path)
    all_champions = load_champions(data_path)
    champion_ids = {champ.name: i for i, champ in enumerate(all_champions)}

    top_k_guesses = 5  # Adjust to show more top-informational guesses

    candidates = all_champions
    attempts = 0

    first_guess = True

    welcome_user()

    while True:
        attempts += 1

        pattern_matrix = compute_pattern_id_matrix(
            all_champions,  # Take all champions
            candidates,  # Compare them with the ones that remain
        )

        # Print a table of the most informative guesses: name, entropy, expected-remaining
        metrics = compute_metrics(pattern_matrix, champion_ids)
        show_top_results(metrics, is_first_guess=first_guess, top=top_k_guesses)

        first_guess = False

        user_champion_guess = input_champion(from_choices=all_champions)
        feedback_pattern = input_feedback(guess=user_champion_guess)

        if is_correct(feedback_pattern):
            print("Good guess!")
            break

        candidates = filter_candidates(candidates, user_champion_guess, feedback_pattern)
        show_remaining_champions(candidates)

        if one_remaining(candidates):
            print(f"The correct champion is: {candidates[0]}")
            break

        if two_remaining(candidates):
            print(f"The correct champion is either: {candidates[0]} or {candidates[1]}")
            print("Flip a coin!")
            break

    print(f"\nTotal attempts: {attempts}")


if __name__ == "__main__":
    main()
