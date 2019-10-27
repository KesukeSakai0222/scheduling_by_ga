# Scheduling by GA
GA is one of machine learning methods, Genetic Algorithm.
When you fill task's name, person-hour, dead line and importance, this program automatically make schedule.

I penalized schedule for 4 points of view.
- pasting deadline penalty
- excessing task penalty
- same task with last task penalty

## flow
1. Make first generation
1. Make next generation
    - unoform crossover as crossover method
    - minimum generation gap; elitist recombination
        - This method select 2 parents' genom and make 2 progeny. Then choose 2 genoms that the penalty is lower out of the 4.
1. Cause mutation
    - Use substitution
1. repeat 2~3