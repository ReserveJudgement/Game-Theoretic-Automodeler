# Game-Theoretic-Automodeler

<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/460d8741-fc08-441c-a5a0-c3295a132e09" />

Automatically and scalably producing qunatitative models for qualitatively described phenomena with LLM agents presents potential for new avenues in scientific research.
This work makes a preliminary exploration of an LLM Agent for automating game-theoretical modeling of animal interactions.

## Workflow Outline
An LLM agent plays three main roles: a biologist, a game-theoretician and an external tool-user.
- The task of the biologist is to generate descriptions of animal interactions and their most commonly observed outcomes, to semantically validate game models and to suggest ways to test the formal models in biological research.
- The task of the game-theoretician is to formalize the players, strategies and utility functions of a game, improve the model based on feedback and analyze validated games using concepts from game theory.
- The tools employed include the Wikimedia API for searching and extracting relevant text from Wikipedia articles, a function to formally validate proposed games and an open-source game solver package (Nashpy: https://nashpy.readthedocs.io/en/stable/index.html).

The workflow can be divided into four main stages: case generation, auto-modeling, validation and analysis.
- Case generation involves externalizing animal interactions from the LLM's knowledge and grounding them with external knowledge from the internet. Cases that failed to retrieve a supporting article were rejected. In this experiment, ten cases were generated for each of four categories: predator-prey dynamics, symbiotic relationships, social foraging and habitat selection.
- Auto-modeling involves constructing a formal game. For simplicity, games are restricted to two-player normal-form with full-information and discrete strategies but could be expanded.
The strategy profile that corresponds to the natural observed animal behavior is formalized seperately.
- The validation stage is concerned with three assessments. One is syntactic correctness, or the formal coherence of the constructed game (e.g. that there is a utility defined for every player and strategy profile). 
The second is semantic correctness, or whether the model is compatible with biological conditions and common sense (e.g. that the utility for an animal being eaten is lower than survival). 
The third comes after solving the game. The game must not be degenerate and the strategy profile most frequently observed in nature must be the most likely outcome of a Nash equilibrium.
- Analysis stage is designed to lay the groundwork for further research based on the produced game models. One direction is to propose biological experiments or field studies that can test the predictions of validated game models. The other direction is to analyze the games through the lens of game theory to identify patterns or commonalities that might aid theory development.

Failure to validate generates a feedback message and leads to a second pass at auto-modeling.
There is a preference for single-equilibrium outcomes, as multiple equilibria detract from the expanatory power of the model.

## Results
25% of the total cases ended with a validated single-equilibrium game.
Syntactic errors were negligible, and were related to generating games that were not two-player.
Most of the games generated were disqualified due to the observed outcomes not being in the equilibria or the game being degenerate.
The second pass contributed more validated game models but with diminishing returns.
Social foraging contributed the most validated game models with a single equilibrium (50% of cases).
Results by category:

|                               | Predator | Symbiosis | Foraging | Habitat | Total |
|------------------------------ | -------- | --------- | -------- | ------- | ----- |
| Total Cases Generated         | 10       | 10        | 10       | 10      | 40    |
| Validated Single-Equilibrium  | 2        | 1         | 5        | 2       | 10    |


## Possible Future Directions
- Improved grounding using scientific literature.
- More relaxed modeling assumptions, e.g. extended-form, multiplayer, incomplete information, boundedly-rational agents.
- Experiment with other base LLM, possibly fine-tuning.
- Additional validation mechanisms, e.g. perturbation tests for robustness.
- Human baseline.
- Human evaluation.
- Data-driven techniques for analysis of produced game models, e.g. clustering, correlation between game and species types, relational graphs, simulating evolutionary dynamics.
